/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-18
 * Time: 上午11:16
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	"bytes"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"log"
	"net"
	"strings"
	"time"
	//	"strconv"
	//	"net/rpc"
	"compress/zlib"
	"reflect"
)

const (
	BUFF_LEN      = 1024
	UID_LEN       = 32
	CHAN_BUFF_LEN = 10
)

var (
	NONE_KW        = make(map[interface{}]interface{})
	value_indexint = reflect.ValueOf(indexint(1))
	ServiceMethod  map[string]*methodType
)

type indexint uint32

type Service struct {
	Uid       string
	Stoped    bool
	sock      net.Conn
	rpc       Rpc
	chSend    chan []byte
	chResp    chan *resper
	chWait    chan *waiter
	chnoWait  chan indexint
	r, w      []byte
	export    *Export
	index     indexint
	heartTime int64
	waits     map[indexint]*waiter
}

type waiter struct {
	i indexint
	c chan interface{}
}
type resper struct {
	i   indexint
	rs  interface{}
	err error
}

func NewService(rpc Rpc, uid string, conn net.Conn) (svc *Service) {
	svc = &Service{Uid: uid, Stoped: true,
		sock:  conn,
		rpc:   rpc,
		r:     make([]byte, BUFF_LEN),
		w:     make([]byte, BUFF_LEN),
		waits: make(map[indexint]*waiter),
	}
	svc.chSend = make(chan []byte, CHAN_BUFF_LEN)
	svc.chResp = make(chan *resper, CHAN_BUFF_LEN)
	svc.chWait = make(chan *waiter, CHAN_BUFF_LEN)
	svc.chnoWait = make(chan indexint, CHAN_BUFF_LEN)
	svc.export = &Export{v: reflect.ValueOf(svc), t: reflect.TypeOf(svc)}
	svc.export.method = ServiceMethod
	return
}

func handshakeSvr(sock net.Conn) string {
	buf := make([]byte, UID_LEN)
	n, err := sock.Read(buf)
	if err != nil || n != UID_LEN {
		return ""
	}
	return string(buf)
}

func handshakeCli(sock net.Conn, uid string) string {
	if len(uid) != UID_LEN {
		return ""
	}
	buf := []byte(uid)
	n, err := sock.Write(buf)
	if err != nil || n != UID_LEN {
		return ""
	}
	return uid
}

func (svc *Service) heartbeat() {
	log.Printf("[grpc]heartbeat(%s) start:%s\n", HEARTBEAT_TIME/time.Second, svc.sock.RemoteAddr())
	svc.heartTime = time.Now().Unix()
	check_times := int64(RECONNECT_TIMEOUT) * int64(HEARTBEAT_TIME)
	for !svc.Stoped {
		err := svc.send(RT_HEARTBEAT)
		if err != nil {
			break
		}
		time.Sleep(HEARTBEAT_TIME)
		//check time out
		curTime := time.Now().Unix()
		if svc.heartTime+check_times < curTime {
			log.Printf("[grpc]****WARNING*** heartbeat timeout:%s\n", svc.sock.RemoteAddr())
			svc.Remote_stop()
			break
		}
		svc.heartTime = curTime
	}
}

func (svc *Service) Start() {
	if !svc.Stoped {
		return
	}
	//	log.Printf("[grpc]Service(%s) Start", svc.Uid)
	svc.Stoped = false
	go svc.goRecv()
	go svc.goSend()
	go svc.goWait()
	go svc.heartbeat()
}

func (svc *Service) Stop() {
	if svc.Stoped {
		return
	}
	svc.Stoped = true
	log.Printf("[grpc]Service(%s) Stop", svc.Uid)
	svc.uninit()
}

func (svc *Service) uninit() {
	svc.closeSock()
	close(svc.chnoWait)
	close(svc.chResp)
	close(svc.chWait)
	close(svc.chSend)
	svc.rpc.StopService(svc)
}

func (svc *Service) closeSock() {
	svc.Call("", "remote_stop", nil, nil, true, false, 0)
	time.Sleep(10 * time.Millisecond)
	svc.sock.Close()
}

func (svc *Service) Remote_stop() error {
	svc.sock.Close()
	svc.Stop()
	return nil
}

func (svc *Service) goRecv() {
	var hl uint32
	var db []byte
	var err error
	hb := make([]byte, 4)

	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			if svc.Stoped {
				return
			}
			log.Printf("[grpc]goRecv error:%s", r)
		}
		svc.Stop()
	}()

	for !svc.Stoped {
		err = svc.read(hb)
		if err != nil {
			if svc.Stoped {
				return
			}
			if string(err.Error()) == "EOF" {
				return
			}
			log.Printf("[grpc]goRecv read head error:%s", err.Error())
			return
		}
		hl = binary.LittleEndian.Uint32(hb)
		db = make([]byte, hl)
		err = svc.read(db)
		if err != nil {
			if svc.Stoped {
				return
			}
			log.Printf("[grpc]goRecv read data error:%s", err.Error())
			return
		}
		v := svc.rpc.Unpack(db).([]interface{})
		go svc.handle(v)
	}
}

func (svc *Service) goSend() {
	var d []byte
	var i, n int
	var l uint32
	var err error
	hb := make([]byte, 4)
	defer svc.Stop()
	for !svc.Stoped {
		d = <-svc.chSend
		l = uint32(len(d))
		binary.LittleEndian.PutUint32(hb, l)
		n, _ = svc.sock.Write(hb)
		i = 0
		for {
			n, err = svc.sock.Write(d[i:l])
			//			log.Printf("[grpc]goSend data:%d, %s", n, d[i:l])
			if err != nil {
				if svc.Stoped {
					return
				}
				log.Printf("[grpc]goSend error:%s", err.Error())
				return
			}
			i += n
			if int(l) == i {
				break
			}
		}
	}
}

func (svc *Service) goWait() {
	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			if svc.Stoped {
				return
			}
			log.Printf("goWait error:%s", r)
		}
		svc.Stop()
	}()
	for !svc.Stoped {
		select {
		case w := <-svc.chWait:
			//log.Printf("<- chWait:%s", w.i)
			svc.waits[w.i] = w
		case rs := <-svc.chResp:
			w, ok := svc.waits[rs.i]
			if ok {
				//log.Printf("<- chResp:%s, %d", rs, w.i)
				//delete(svc.waits, w.i)
				if rs.err != nil {
					w.c <- rs.err
				} else {
					w.c <- rs.rs
				}
				delete(svc.waits, w.i)
				close(w.c)
			}
		case i := <-svc.chnoWait:
			//log.Printf("<- chnoWait:%s", i)
			w, ok := svc.waits[i]
			if ok {
				delete(svc.waits, i)
				close(w.c)
			}
		}
	}
	for key, w := range svc.waits {
		delete(svc.waits, key)
		w.c <- errors.New("service close")
		close(w.c)
	}
}

func (svc *Service) handle(v []interface{}) {
	var dtype, index uint
	var obj_id, name, argkw string
	dtype = iftoui(v[0])
	rt := dtype & RT_MARK
	if rt == RT_HEARTBEAT || len(v) == 1 {
		return //heart beat
	}
	switch v[1].(type) {
	case string:
		obj_id = v[1].(string)
	case int8, int16, int32:
		obj_id = ""
	}

	//	log.Printf("[grpc]handle rt:%d, v:%s", rt, v)
	switch rt {
	case RT_REQUEST:
		index = iftoui(v[2])
		name = v[3].(string)
		argkw = v[4].(string)
		svc.handle_request(dtype, index, obj_id, name, argkw)
	case RT_RESPONSE:
		index = iftoui(v[1])
		name = v[2].(string)
		svc.handle_response(dtype, index, name)
	case RT_EXCEPTION:
		index = iftoui(v[1])
		name = v[2].(string)
		svc.handle_exception(dtype, index, name)
	}
}

func (svc *Service) handle_request(dtype, index uint, obj_id, name, argkw string) {
	//	log.Printf("[grpc]handle_request v:%s", obj_id, name, argkw)
	var err error
	export := svc.GetExport(obj_id)
	if export == nil {
		svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) no found", obj_id))
		return
	}
	mtype, ok := export.method[strings.Title(name)]
	if !ok {
		svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) func(%s) no found", obj_id, name))
		return
	}

	var dargkw []byte
	if dtype&DT_ZIP == DT_ZIP {
		var akbuf bytes.Buffer
		b1 := bytes.NewBuffer([]byte(argkw))
		r, err := zlib.NewReader(b1)
		if err != nil {
			svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) zlib error:(%s)", obj_id, err.Error()))
			return
		}
		io.Copy(&akbuf, r)
		dargkw = akbuf.Bytes()
	} else {
		dargkw = []byte(argkw)
	}

	var d []interface{}
	switch x := svc.rpc.Unpack(dargkw); y := x.(type) {
	case []interface{}:
		d = y
	default:
		svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) Unpack error:%s", obj_id, x))
		return
	}
	args, ok := d[0].([]interface{})
	kw, ok := d[1].(map[interface{}]interface{})
	if dtype&DT_PROXY == DT_PROXY {
		args[0], err = svc.GetProxys(args[0])
		if err != nil {
			svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) Proxy error:%s", obj_id, err.Error()))
		}
	}

	rs, err := svc.callExport(export, mtype, args, kw)
	if dtype&ST_NO_RESULT == ST_NO_RESULT {
		return
	}
	if err != nil {
		svc.send(RT_EXCEPTION, index, fmt.Sprintf("error:%s", err.Error()))
		//log.Printf("handle_request error:%s", err.Error())
		return
	}

	var b1 []byte
	b1, err = svc.rpc.Pack(rs)
	if err != nil {
		svc.send(RT_EXCEPTION, index, fmt.Sprintf("export(%s) Pack result error:%s", err.Error()))
		return
	}
	svc.send(RT_RESPONSE, index, b1)
}

func (svc *Service) handle_response(dtype, index uint, argkw string) {
	resp := &resper{i: indexint(index), rs: svc.rpc.Unpack([]byte(argkw))}
	svc.chResp <- resp
}

func (svc *Service) handle_exception(dtype, index uint, e string) {
	resp := &resper{i: indexint(index), err: errors.New(e)}
	svc.chResp <- resp
}

func (svc *Service) send(data ...interface{}) (err error) {
	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			log.Printf("[ERROR]recover send:%s", r)
			err = errors.New("close")
		}
	}()

	//log.Printf("send:%s", data)
	d, err := svc.rpc.Pack(data)
	if err != nil {
		log.Printf("send error:%s", err.Error())
		return
	}
	svc.chSend <- d
	return nil
}

func (svc *Service) read(buf []byte) (err error) {
	c := len(buf)
	i := 0
	n := 0
	for c > 0 {
		n, err = svc.sock.Read(buf[i:])
		if err != nil {
			return err
		}
		i += n
		c -= n
	}
	return nil
}

func (svc *Service) nextIndex() indexint {
	if value_indexint.OverflowUint(uint64(svc.index) + 1) {
		svc.index = 1
	} else {
		svc.index += 1
	}
	return svc.index
}

func (svc *Service) readResponse(index indexint, timeout int64) (rs interface{}, err error) {
	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			rs, err = nil, recoverToError(r)
		}
	}()

	c := make(chan interface{}, 0)
	w := &waiter{
		c: c,
		i: index,
	}
	svc.chWait <- w
	select {
	case r, ok := <-c:
		if !ok {
			return nil, errors.New("readResponse error")
		}
		err, ok = r.(error)
		if !ok {
			rs = r
			err = nil
		}
		return
	case <-time.After(time.Duration(timeout)):
		svc.chnoWait <- index
		err = errors.New(fmt.Sprintf("TimeOut(%d)", timeout))
	}
	return
}

func (svc *Service) Call(obj_id, name string, args []interface{}, kw map[interface{}]interface{},
	no_result, proxy bool, timeout int64) (rs interface{}, err error) {
	var d []byte
	var dtype indexint
	dtype = RT_REQUEST
	if proxy {
		dtype |= DT_PROXY
	}
	if kw == nil {
		kw = NONE_KW
	}

	d, err = svc.rpc.Pack([]interface{}{args, kw})
	if err != nil {
		log.Printf("call error:%s", err.Error())
		return
	}
	if len(d) >= ZIP_LENGTH {
		zbuf := bytes.NewBuffer(nil)
		dtype |= DT_ZIP
		w := zlib.NewWriter(zbuf)
		w.Write(d)
		w.Close()
		d = zbuf.Bytes()
	}
	if no_result {
		dtype |= ST_NO_RESULT
	}
	index := svc.nextIndex()
	err = svc.send(dtype, obj_id, index, name, d)
	if err != nil {
		return
	}
	if no_result {
		return nil, nil
	}
	if timeout <= 0 {
		timeout = int64(DEFAULT_TIMEOUT)
	}
	rs, err = svc.readResponse(index, timeout)
	return
}

func (svc *Service) GetExport(obj_id string) *Export {
	if obj_id == "" {
		return svc.export
	}
	return svc.rpc.GetExport(obj_id)
}

func (svc *Service) GetProxys(ids interface{}) (rs interface{}, err error) {
	id, ok := ids.(string)
	if ok {
		o, err := svc.GetProxy(id)
		if err != nil {
			return nil, err
		}
		return o.Interface(), nil
	}
	_ids, ok := ids.([]interface{})
	if !ok {
		return nil, errors.New("GetProxys error")
	}

	objs := make([]interface{}, len(_ids))
	for i, v := range _ids {
		id = v.(string)
		o, err := svc.GetProxy(id)
		if err != nil {
			return nil, err
		}
		objs[i] = o.Interface()
	}
	return objs, nil
}

func (svc *Service) GetProxy(id string) (rs reflect.Value, err error) {
	rs, err = svc.rpc.NewProxy(id)
	if err != nil {
		return
	}
	rs.Interface().(Proxy).Init(svc, id)
	return
}

func callMethod(export *Export, mtype *methodType, args []interface{},
	kw map[interface{}]interface{}) (rs []reflect.Value, err error) {
	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			rs, err = nil, recoverToError(r)
		}
	}()
	var it reflect.Type
	function := mtype.method.Func
	//log.Printf("[grpc]Service.call:(%d)%s, %s", mtype.mtype.NumIn(), args, kw)
	l := mtype.mtype.NumIn()
	params := make([]reflect.Value, l)
	params[0] = export.v
	for i := 0; i < len(args); i++ {
		it = mtype.mtype.In(i + 1)
		params[i+1] = reflect.ValueOf(args[i]).Convert(it)
	}
	if (l - 1 - len(args)) > 0 {
		params[l-1] = reflect.ValueOf(kw)
	}
	return function.Call(params), nil
}

func (svc *Service) callExport(export *Export, mtype *methodType, args []interface{},
	kw map[interface{}]interface{}) (rs interface{}, err error) {
	defer func() {
		if r := recover(); r != nil {
			PrintRecover(r)
			rs, err = nil, recoverToError(r)
		}
	}()

	var returnValues []reflect.Value
	returnValues, err = callMethod(export, mtype, args, kw)
	if err != nil {
		return
	}

	rl := len(returnValues)
	if rl > 0 {
		errInter := returnValues[rl-1].Interface()
		if errInter != nil {
			err, ok := errInter.(error)
			if !ok {
				err = errors.New(errInter.(string))
			}
			return nil, err
		}
	}
	switch rl {
	case 1:
		return nil, err
	case 2:
		return returnValues[0].Interface(), err
	}
	ret := make([]interface{}, rl-1)
	for i := 0; i < rl-1; i++ {
		ret[i] = returnValues[i].Interface()
	}
	return ret, err
}

func init() {
	ServiceMethod = suitableMethods(reflect.TypeOf(new(Service)), false)
}
