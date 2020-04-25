/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-11
 * Time: 上午11:06
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	"log"
	"net"
)

type RpcServer struct {
	rpcBase
	listener net.Listener
	svcs     map[string]*Service
}

func NewRpcServer() (svr *RpcServer) {
	svr = &RpcServer{
		svcs: make(map[string]*Service),
	}
	svr.Init()
	return
}

//bind addr
func (rpc *RpcServer) Bind(addr string) error {
	var err error
	rpc.Stop()
	err = rpc.resolveAddr(addr)
	if err != nil {
		return err
	}
	tcp_addr, ok := rpc.Addr.(*net.TCPAddr)
	if ok {
		rpc.listener, err = net.ListenTCP("tcp", tcp_addr)
		if err != nil {
			return err
		}
		log.Printf("[grpc]RpcServer tcp Bind: %s", addr)
	} else {
		unix_addr, _ := rpc.Addr.(*net.UnixAddr)
		rpc.listener, err = net.ListenUnix("unix", unix_addr)
		if err != nil {
			return err
		}
		log.Printf("[grpc]RpcServer unix Bind: %s", addr)
	}
	return nil
}

func (rpc *RpcServer) Start(wait bool) {
	if rpc.Started {
		return
	}
	rpc.rpcBase.Start()
	if wait {
		rpc.loop()
	} else {
		go rpc.loop()
	}
}

func (rpc *RpcServer) Stop() {
	if !rpc.Started {
		return
	}
	log.Printf("[grpc]RpcServer Stop!")
	rpc.rpcBase.Stop()
	rpc.close()
}

func (rpc *RpcServer) loop() {
	for {
		conn, err := rpc.listener.Accept()
		if err != nil {
			log.Printf("Error Accept:%s", err.Error())
			rpc.Stop()
			return
		}
		go rpc.newConn(conn)
	}
}

func (rpc *RpcServer) newConn(conn net.Conn) {
	uid := handshakeSvr(conn)
	if uid == "" {
		conn.Close()
		return
	}
	svc := NewService(rpc, uid, conn)
	rpc.svcs[uid] = svc
	svc.Start()
}

//close rpc
func (rpc *RpcServer) close() {
	if rpc.listener != nil {
		rpc.listener.Close()
		rpc.listener = nil
	}
}

func (rpc *RpcServer) StopService(svc *Service) {
	delete(rpc.svcs, svc.Uid)
}
