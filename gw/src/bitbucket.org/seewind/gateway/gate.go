/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-19
 * Time: 下午2:23
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"errors"
	"net"
)

type Gate struct {
	gw        *Gateway
	Sock      ConnProxy
	Handler   GateHandle
	Processer GateProcess
	Stoped    bool
}

//create Gate by sock
func NewGate(gw *Gateway, sock ConnProxy) (g *Gate, err error) {
	g = &Gate{gw: gw, Sock: sock, Stoped: false}
	g.Handler = gw.factory.NewHandler(g)
	g.Processer = gw.factory.NewProcesser(g)
	err = g.Start()
	return
}

//start one Gate
func (g *Gate) Start() (err error) {
	if g.Stoped {
		return errors.New("gate Stoped!")
	}
	go g.Handler.Loop()
	return nil
}

func (g *Gate) Stop() {
	if g.Stoped {
		return
	}
	g.Stoped = true
	g.Processer.Stop()
	g.gw.delGate(g)
}

func (g *Gate) UnInit() {

}

func (g *Gate) RemoteAddr() net.Addr {
	return g.Sock.RemoteAddr()
}
