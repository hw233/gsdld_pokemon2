/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-20
 * Time: 上午11:46
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"bytes"
	"log"
	"sync"
	"time"
)

var (
	ErrClose *ErrorClose = new(ErrorClose)
)

func init() {
}

type GateHandle interface {
	Loop()
	Push([]byte) // server push message to client
	SetTimeout(time.Duration)
}

type ErrorClose string

func (ec *ErrorClose) Error() string { return "close" }

type BuffHandler struct {
	G       *Gate
	b       []byte
	wLock   sync.Mutex
	Buf     *bytes.Buffer
	Timeout time.Duration
}

func NewBuffHandler(g *Gate, buffLen int) *BuffHandler {
	if buffLen <= 0 {
		buffLen = BUFF_LEN
	}
	return &BuffHandler{
		G:   g,
		Buf: bytes.NewBuffer(nil),
		b:   make([]byte, buffLen),
	}
}

func (hd *BuffHandler) SetTimeout(s time.Duration) {
	hd.Timeout = s
}

func (hd *BuffHandler) ReadToBuff() (n int, err error) {
	if hd.Timeout > 0 {
		hd.G.Sock.SetReadDeadline(time.Now().Add(hd.Timeout))
	}
	n, err = hd.G.Sock.Read(&hd.b)
	if err != nil {
		log.Printf("[handler(%d)] read error:%s\n", hd.G.Processer.GetPid(), err.Error())
		return
	}
	if n == 0 {
		return 0, ErrClose
	}
	// log.Printf("[handler(%d)]Read :%d\n%s\n", hd.G.Processer.GetPid(), n, hex.Dump(hd.b[:n]))
	_, err = hd.Buf.Write(hd.b[:n])
	if err != nil {
		log.Printf("[handler] buf.Write error:%s\n", err.Error())
		return
	}
	return
}

func (hd *BuffHandler) Write(b []byte) error {
	hd.wLock.Lock()
	defer hd.wLock.Unlock()
	i, l := 0, len(b)
	for {
		n, err := hd.G.Sock.Write(b[i:])
		//		log.Println("[DEBUG]hd.Write:", string(b[i:i+n]), string(b))
		if err != nil {
			return err
		}
		i += n
		if i == l {
			break
		}
	}
	return nil
}

func (hd *BuffHandler) InitSock() {
	hd.G.Sock.InitSock()
}

func (hd *BuffHandler) UnInitSock() {
	hd.G.Sock.Close()
	hd.G.Stop()
}
