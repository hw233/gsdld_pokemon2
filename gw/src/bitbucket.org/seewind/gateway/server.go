/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-27
 * Time: 上午9:22
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"bitbucket.org/seewind/grpc/golang/grpc"
	"errors"
	"log"
	"sync"
	"time"
	"encoding/binary"
)

const (
	RPC_SERVER_NAME = "gw"
	MSG_QUEUE       = 100
	MSG_TYPE_MSG    = 0
	MSG_TYPE_CLOSE  = 1
	MSG_TYPE_OPEN   = 2
)

var (
	svrLock sync.Mutex
	servers map[string]*Server
	uuid    string
)

type sendMsg struct {
	pid     uint16
	c       chan interface{}
	Type    int
	msg     interface{}
	addr    string
	routeId byte
}

type Server struct {
	sync.Mutex
	Addr   string
	cond   *sync.Cond
	rpc    *grpc.RpcClient
	rpcSvr *RpcServer
	//	msgIds     IterUInt16
	processers map[uint16]GateProcess
	cSend      chan *sendMsg
	stoped     bool
}

/*
 */
func GetServer(addr string) (svr *Server, err error) {
	svrLock.Lock()
	defer func() {
		var c *sync.Cond
		if svr != nil {
			svr.Lock()
			if svr.cond == nil {
				svrLock.Unlock()
				svr.Unlock()
				return
			}
			c = svr.cond
			svrLock.Unlock()
			c.Wait() // wait for connect
			svr.Unlock()
			if svr.IsStoped() {
				err = errors.New("server is stoped!")
			}
		} else {
			svrLock.Unlock()
		}
	}()
	svr, ok := servers[addr]
	if ok && !svr.IsStoped() {
		return
	}

	log.Println("[NewServer]", addr)
	svr = NewServer()
	servers[addr] = svr
	go svr.Connect(addr)
	return
}

func NewServer() (svr *Server) {
	svr = &Server{rpc: grpc.NewRpcClient(),
		rpcSvr:     NewRpcServer(),
		processers: make(map[uint16]GateProcess),
		cSend:      make(chan *sendMsg, 50),
		stoped:     false,
	}
	//connect wait cond
	svr.cond = sync.NewCond(svr)
	return
}

func (svr *Server) Connect(addr string) (err error) {
	defer func() {
		svr.Lock()
		c := svr.cond
		svr.cond = nil
		c.Broadcast()
		svr.Unlock()
	}()
	svr.Addr = addr
	err = svr.rpc.Connect(addr, time.Second*3)
	if err != nil {
		svr.Stop()
		return
	}
	svr.rpc.Start()
	svr.rpcSvr.svr = svr
	err = svr.rpcSvr.reg()
	if err != nil {
		svr.Stop()
		return
	}
	go svr.loop()
	return
}

func (svr *Server) IsStoped() (rs bool) {
	svr.Lock()
	rs = svr.stoped || (svr.cond == nil && !svr.rpc.Started)
	svr.Unlock()
	return rs
}

func (svr *Server) Stop() {
	if svr.stoped {
		return
	}
	svr.stoped = true
	svrLock.Lock()
	delete(servers, svr.Addr)
	svrLock.Unlock()
	log.Println("[Server.Stop]", svr.rpc.SAddr)
	close(svr.cSend)
	for _, p := range svr.processers {
		p.CloseServer()
	}
}

func (svr *Server) AddProcesser(p GateProcess, routeId byte) {
	pid := p.GetPid()
	svr.Lock()
	svr.processers[pid] = p
	svr.Unlock()
	//	svr.Send(pid, MSG_TYPE_OPEN, nil, nil, false)
	svr.SendMsg(&sendMsg{Type: MSG_TYPE_OPEN, pid: pid,
		addr:    p.GetRemoteAddr(),
		routeId: routeId,
	})
}

func (svr *Server) DelProcesser(pid uint16) (ok bool) {
	svr.Lock()
	delete(svr.processers, pid)
	svr.Unlock()
	svr.Send(pid, MSG_TYPE_CLOSE, nil)
	return true
}

func (svr *Server) GetProcesser(pid uint16) (p GateProcess, ok bool) {
	svr.Lock()
	defer svr.Unlock()
	p, ok = svr.processers[pid]
	if ok {
		return
	}
	p, ok = GetProcesser(pid)
	return
}

func (svr *Server) Send(pid uint16, Type int, msg []byte) {
	s := &sendMsg{Type: Type, pid: pid, msg: msg}
	svr.SendMsg(s)
}

func (svr *Server) SendMsg(msg *sendMsg) {
	if svr.stoped {
		return
	}
	defer func() { grpc.PrintRecover(recover()) }()
	svr.cSend <- msg
	return
}

func (svr *Server) loop() {
	delay := 300 * time.Microsecond
	mlen := 50
	msgs := make([]*sendMsg, mlen+10)
	index := 0
	//count := 0
	cClose := make(chan int, 0)
	close(cClose)

	defer func() {
		svr.Stop()
	}()
	sends_func := func() {
		if index > 0 {
			//count += index
			//log.Println("sends_func", index, "/", count)
			svr.rpcSvr.callSends(msgs[:index])
			index = 0
		}
	}

	switchSendFunc := func(msg *sendMsg, delay time.Duration) {
		switch msg.Type {
		case MSG_TYPE_MSG:
			msgs[index] = msg
			index += 1
			if delay > 0 {
				time.Sleep(delay)
			} else if index >= mlen {
				sends_func()
			}
		case MSG_TYPE_CLOSE:
			sends_func()
			svr.rpcSvr.callClose(msg)
		case MSG_TYPE_OPEN:
			sends_func()
			svr.rpcSvr.callOpen(msg)
		}
	}

	//select cClose will do immediately, so if index ==0, no select cClose
	for !svr.IsStoped() {
		if index > 0 {
			select {
			case msg := <-svr.cSend:
				switchSendFunc(msg, 0)
			case <-cClose:
				sends_func()
			}
		} else {
			select {
			case msg := <-svr.cSend:
				switchSendFunc(msg, delay)
			}
		}
	}
}

type RpcServer struct {
	grpc.Proxyer
	svr *Server
}

func NewRpcServer() (s *RpcServer) {
	s = &RpcServer{}
	return s
}

func (svr *RpcServer) reg() (err error) {
	name := RPC_SERVER_NAME
	rpc := svr.svr.rpc
	rpc.Register(name, svr)
	rpc.GetProxy(name, svr)
	for i := 0; i < 5; i++ {
		_, err = svr.Call("reg", []interface{}{name, uuid}, false, true, 0)
		if err == nil {
			break
		}
		time.Sleep(time.Second)
	}
	return err
}

//send message to server
func (svr *RpcServer) callSend(msg *sendMsg) (err error) {
	//log.Println("[DEBUG]Server.Send:", msg)
	_, err = svr.Call("send", []interface{}{msg.pid, msg.msg},
		true, false, 0)
	return
}

func (svr *RpcServer) callSends(msgs []*sendMsg) (err error) {

	args := make([]interface{}, len(msgs))
	for index := range msgs {
		msg := msgs[index]
		args[index] = []interface{}{msg.pid, msg.msg}
	}
	// log.Println("[DEBUG]Server.Sends:", args)
	_, err = svr.Call("sends", []interface{}{args}, true, false, 0)
	return
}

//send process close msg
func (svr *RpcServer) callClose(msg *sendMsg) (rs interface{}, err error) {
	rs, err = svr.Call("close", []interface{}{msg.pid}, true, false, 0)
	return
}

func (svr *RpcServer) callOpen(msg *sendMsg) (rs interface{}, err error) {
	rs, err = svr.Call("open", []interface{}{msg.pid, msg.addr, int(msg.routeId)}, true, false, 0)
	return
}

func (svr *RpcServer) _send(pid uint16, routeId byte, d []byte) (err error) {
	p, ok := svr.svr.GetProcesser(pid)
	if !ok {
		return errors.New("pid(%s) no found")
	}
	p.SvrSend(routeId, d)
	return nil
}

//server push message to client
/*
func (svr *RpcServer) Send(ipid int, data []byte) (err error) {
	pid := uint16(ipid)
	return svr._send(pid, data)
}

func (svr *RpcServer) Sends(data []interface{}) (err error) {
	for i := range data {
		dd := data[i].([]interface{})
		pid := uint16(iftoi(dd[0]))
		err = svr._send(pid, dd[1].([]byte))
		if err != nil {
			log.Printf("[RpcServer]Sends error:pid(%s) no found\n", pid)
			msg := &sendMsg{pid: pid}
			svr.callClose(msg)
			continue
		}
	}
	return nil
}
*/
func (svr *RpcServer) GameBroadcast(group []interface{}, data interface{}) (err error) {
	//	log.Printf("RespAndSends:%s\n", data)
	msgtype := byte(1)
	msgbytes := []byte(data.(string))

	sendData := make([]byte, 3+len(msgbytes))
	sendData[0] = msgtype
	copy(sendData[3:], msgbytes)

	for i := range group{
		dd := group[i].([]interface{})
		pid := uint16(iftoi(dd[0]))
		routeId := byte(iftoi(dd[1]))

		mid := uint16(iftoi(dd[2]))
		binary.LittleEndian.PutUint16(sendData[1:], mid)

		go func(){
			err = svr._send(pid, routeId, sendData)
			if err != nil {
				log.Printf("[RpcServer]GameBroadcast Sends error:pid(%s) no found\n", pid)
				msg := &sendMsg{pid: pid}
				svr.callClose(msg)
			}
		}()

	}
	return nil
}


func (svr *RpcServer) RespAndSends(data []interface{}) (err error) {
	//	log.Printf("RespAndSends:%s\n", data)
	for i := range data {
		dd := data[i].([]interface{})
		pid := uint16(iftoi(dd[0]))
		routeId := byte(iftoi(dd[1]))
		err = svr._send(pid, routeId, []byte(dd[2].(string)))
		if err != nil {
			log.Printf("[RpcServer]Sends error:pid(%s) no found\n", pid)
			msg := &sendMsg{pid: pid}
			svr.callClose(msg)
		}
	}
	return nil
}

func (svr *RpcServer) Echo(s string) (rs string, err error) {
	log.Println("RpcServer.Echo:", s)
	return s, nil
}

func (svr *RpcServer) Router(pid uint16, rid uint16, addr string) (err error) {
	// log.Println("RpcServer.Router:", pid, filter)
	p, ok := svr.svr.GetProcesser(pid)
	if ok {
		p.AddRouter(byte(rid), addr)
	}
	return nil
}

// remove router
func (svr *RpcServer) RRouter(pid uint16, rid uint16) (err error) {
	log.Println("RpcServer.RemoveRouter:", pid, rid)
	p, ok := svr.svr.GetProcesser(pid)
	if ok {
		p.RemoveRouter(byte(rid))
	}
	return nil
}

// close client
func (svr *RpcServer) CClient(pid uint16) (err error) {
	log.Println("RpcServer.CloseClient:", pid)
	p, ok := svr.svr.GetProcesser(pid)
	if ok {
		p.CloseClient()
	}
	return nil
}

//switch connect other svr
func (svr *RpcServer) Connect(pid uint16, addr string) (err error) {
	p, ok := svr.svr.GetProcesser(pid)
	if ok {
		p.Connect(addr)
	}
	return nil
}

func init() {
	servers = make(map[string]*Server, 0)
	uuid, _ = grpc.GenUUID()
	log.Println("gateway uuid:", uuid)
}
