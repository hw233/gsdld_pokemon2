/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-26
 * Time: 上午10:25
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"errors"
	"fmt"
	"log"
	"sync"
)

const (
	//ctrl
	CTRL_CTAG_LEN = 1
	CTAG_ROUTE    = 0
	CTAG_CONNECT  = 1
	CTRL_OK       = "ok"
)

var (
	pIds            IterUInt16
	DefaultGameAddr string

	processers  map[uint16]*Processer
	processersL sync.RWMutex
)

type GateProcess interface {
	GetPid() uint16
	GetRemoteAddr() string
	Stop()
	Connect(addr string) (err error)
	Process(data []byte) error
	SvrSend(routeId byte, msg []byte) //server send message to client
	AddRouter(rid byte, addr string) error
	RemoveRouter(rid byte) error
	CleanRouter() error
	CloseServer()
	CloseClient() error
}

type Processer struct {
	g     *Gate
	Pid   uint16
	svr   *Server
	rSvrs map[byte]*Server //rsvr = room svr
}

func NewProcesser(g *Gate) (p *Processer) {
	p = &Processer{
		g:     g,
		Pid:   pIds.Next(),
		rSvrs: make(map[byte]*Server),
	}
	processersL.Lock()
	processers[p.Pid] = p
	processersL.Unlock()
	return p
}

func GetProcesser(pid uint16) (p *Processer, ok bool) {
	processersL.RLock()
	p, ok = processers[pid]
	processersL.RUnlock()
	return
}

func (bp *Processer) log(format string, v ...interface{}) {
	Log(2, fmt.Sprintf("[Processer]pid(%d): ", bp.Pid)+format, v...)
}

func (bp *Processer) GetPid() uint16 {
	return bp.Pid
}

//return remote's socket addr
func (bp *Processer) GetRemoteAddr() string {
	addr := bp.g.Sock.RemoteAddr()
	return addr.String()
}

func (bp *Processer) getSvr(rid byte) (svr *Server, err error) {
	svr, ok := bp.rSvrs[rid]
	if !ok {
		if rid != 0 {
			bp.log("processRouter warn:rid(%d) no found", rid)
		}
		if bp.svr == nil && DefaultGameAddr != "" {
			err = bp.Connect(DefaultGameAddr)
		}
		if err != nil {
			return nil, err
		}
		svr = bp.svr
	}
	if svr == nil || svr.IsStoped() {
		return nil, errors.New(fmt.Sprintf("[Processer]not server for router:%d", rid))
	}
	return
}

// close client
func (bp *Processer) CloseClient() error {
	bp.log("CloseClient")
	return bp.g.Sock.Close()
}

//close server
func (bp *Processer) CloseServer() {
	if bp.svr != nil {
		bp.CleanRouter()
		bp.svr.DelProcesser(bp.Pid)
	}
}

func (bp *Processer) Stop() {
	processersL.Lock()
	delete(processers, bp.Pid)
	processersL.Unlock()
	bp.CloseClient()
	bp.CloseServer()
}

//client control:connect to server
func (bp *Processer) Connect(addr string) (err error) {
	bp.log("Connect:%s", addr)
	bp.CloseServer()
	bp.svr, err = GetServer(addr)
	if err != nil {
		return
	}
	bp.svr.AddProcesser(bp, 0)
	bp.log("Connect finish ")
	return
}

func (bp *Processer) routerConnect(rid byte, addr string) (err error) {
	//	bp.log("routerConnect:%s", addr)
	svr, err := GetServer(addr)
	if err != nil {
		return
	}
	svr.AddProcesser(bp, rid)
	bp.rSvrs[rid] = svr
	return
}

//process client's message
func (bp *Processer) Process(data []byte) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = errors.New(fmt.Sprintf("ctrl error:%s", r))
		}
	}()
	switch data[0] {
	case CTAG_CONNECT: // 1
		err = bp.processConnect(data)
	case CTAG_ROUTE: // 0
		rid := data[1]
		err = bp.processRouter(rid, data[2:])
	}
	return
}

func (h *Processer) makeCtrlResult(ctag byte, msg string) (rs []byte) {
	l := len(msg)
	rs = make([]byte, l+CTRL_CTAG_LEN)
	rs[0] = ctag
	copy(rs[CTRL_CTAG_LEN:], msg)
	//	rs[CTRL_CTAG_LEN:] = []byte(msg)
	return
}

func (bp *Processer) processConnect(data []byte) (err error) {
	addr := string(data[CTRL_CTAG_LEN:])
	bp.log("connect:%s", addr)
	err = bp.Connect(addr)
	bp.log("connected:%s, error:%s", addr, err)
	if err != nil {
		bp.g.Handler.Push(bp.makeCtrlResult(byte(CTAG_CONNECT), err.Error()))
	} else {
		bp.g.Handler.Push(bp.makeCtrlResult(byte(CTAG_CONNECT), CTRL_OK))
	}
	return nil
}

func (bp *Processer) processRouter(rid byte, data []byte) (err error) {
	// bp.log("processRouter:%s", string(data))
	//	bp.SvrSend(data) // test
	//	return
	svr, err := bp.getSvr(rid)
	if err != nil {
		return
	}
	svr.Send(bp.Pid, MSG_TYPE_MSG, data)
	return

}

//process server's message
func (bp *Processer) SvrSend(routeId byte, data []byte) {
	bp.g.Handler.Push(append([]byte{0, routeId}, data...))
}

// add router
func (bp *Processer) AddRouter(rid byte, addr string) (err error) {
	err = bp.routerConnect(rid, addr)
	return
}

// remove router
func (bp *Processer) RemoveRouter(rid byte) error {
	svr, ok := bp.rSvrs[rid]
	if ok {
		delete(bp.rSvrs, rid)
		svr.DelProcesser(bp.Pid)
	}
	return nil
}

func (bp *Processer) CleanRouter() error {
	log.Println("[DEBUG CleanRouter] pid:", bp.Pid)
	for rid, svr := range bp.rSvrs {
		delete(bp.rSvrs, rid)
		svr.DelProcesser(bp.Pid)
	}
	return nil
}

func init() {
	processers = make(map[uint16]*Processer)
}

/////////
/////////
