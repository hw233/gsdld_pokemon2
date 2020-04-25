package gateway

import (
	"log"
	"net"
	"runtime/debug"
	"sync"
	"time"
)

type GateFactory interface {
	NewHandler(*Gate) GateHandle
	NewProcesser(*Gate) GateProcess
}

type Gateway struct {
	sync.Mutex
	Net, Addr string
	listener  net.Listener
	gates     map[*Gate]net.Addr
	Started   bool
	factory   GateFactory
}

func NewGateway(factory GateFactory) *Gateway {
	gw := &Gateway{}
	gw.Started = false
	gw.gates = make(map[*Gate]net.Addr)
	gw.factory = factory
	return gw
}

//监听
func (gw *Gateway) Listen(protocol, addr string) (err error) {
	listener, err := net.Listen(protocol, addr)
	if err != nil {
		return err
	}
	gw.listener = listener
	gw.Net, gw.Addr = protocol, addr
	return nil
}

func (gw *Gateway) Start() {
	if gw.Started {
		return
	}
	gw.Started = true
	go gw.loop()
}

func (gw *Gateway) StartForever() {
	if gw.Started {
		return
	}
	gw.Started = true
	gw.loop()
}

func (gw *Gateway) Stop() {
	if !gw.Started {
		return
	}
	gw.Started = false
}

func (gw *Gateway) loop() {
	defer func() {
		if r := recover(); r != nil {
			log.Println("[gateway]loop error:", r)
		}
	}()
	syscallLimit()

	for gw.Started {
		conn, err := gw.listener.Accept()
		if err != nil {
			log.Println("[gateway]loop error:", err)
			time.Sleep(100 * time.Millisecond)
			//gw.Stop()
			continue
		}
		//log.Println("conn:", conn)
		proxy := NewTcpSocketProxy(conn)
		gw.Accept(proxy)
	}
}

func (gw *Gateway) Accept(proxy ConnProxy) (err error) {
	defer func() {
		if r := recover(); r != nil {
			log.Println("[Gateway]accept error:", r)
			debug.PrintStack()
			proxy.Close()
		}
	}()
	gate, err := NewGate(gw, proxy)
	if err != nil {
		log.Printf("accept error:%s\n", err.Error())
		return
	}
	addr := proxy.RemoteAddr()
	gw.Lock()
	defer gw.Unlock()
	gw.gates[gate] = addr
	return
}

func (gw *Gateway) delGate(g *Gate) {
	gw.Lock()
	defer gw.Unlock()
	delete(gw.gates, g)
}
