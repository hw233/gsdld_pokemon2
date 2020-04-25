/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-11
 * Time: 上午11:06
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net"
	"reflect"
	"time"
)

type RpcClient struct {
	rpcBase
	sock net.Conn
	svc  *Service
}

func NewRpcClient() (client *RpcClient) {
	client = &RpcClient{}
	client.Init()
	return
}

func GenUUID() (string, error) {
	uuid := make([]byte, 16)
	n, err := rand.Read(uuid)
	if n != len(uuid) || err != nil {
		return "", err
	}
	// TODO: verify the two lines implement RFC 4122 correctly
	uuid[8] = 0x80 // variant bits see page 5
	uuid[4] = 0x40 // version 4 Pseudo Random, see page 7

	return hex.EncodeToString(uuid), nil
}

//connect to addr
func (rpc *RpcClient) Connect(addr string, timeout time.Duration) (err error) {
	rpc.Stop()
	err = rpc.resolveAddr(addr)
	if err != nil {
		return
	}
	rpc.sock, err = net.DialTimeout(rpc.Net, addr, timeout)
	if err != nil {
		return
	}

	//	tcp_addr, ok := rpc.Addr.(*net.TCPAddr)
	//	if ok {
	//		rpc.sock, err = net.DialTCP("tcp", nil, tcp_addr)
	//		net.DialTimeout("tcp", tcp_addr, timeout)
	//		if err != nil {
	//			return
	//		}
	//	} else {
	//		unix_addr, _ := rpc.Addr.(*net.UnixAddr)
	//		rpc.sock, err = net.DialUnix("unix", nil, unix_addr)
	//		if err != nil {
	//			return
	//		}
	//	}

	uid, _ := GenUUID()
	uid = handshakeCli(rpc.sock, uid)
	if uid == "" {
		rpc.sock.Close()
		rpc.sock = nil
		err = fmt.Errorf("handsshake error:%s", uid)
		return
	}
	rpc.svc = NewService(rpc, uid, rpc.sock)
	return
}

//close rpc
func (rpc *RpcClient) close() {
	if rpc.sock != nil {
		rpc.sock.Close()
		rpc.sock = nil
		rpc.svc = nil
	}
}

func (rpc *RpcClient) Start() {
	if rpc.Started {
		return
	}
	rpc.rpcBase.Start()
	rpc.svc.Start()
}

func (rpc *RpcClient) Stop() {
	if !rpc.Started {
		return
	}
	rpc.rpcBase.Stop()
	rpc.svc.Stop()
	rpc.svc = nil
	rpc.close()
}

func (rpc *RpcClient) Call(obj_id, name string, args []interface{}, kw map[interface{}]interface{},
	no_result, proxy bool, timeout int64) (rs interface{}, err error) {
	return rpc.svc.Call(obj_id, name, args, kw, no_result, proxy, timeout)
}

func (rpc *RpcClient) GetProxy(id string, p Proxy) (rs Proxy) {
	v := reflect.ValueOf(p)
	if v.IsNil() {
		rs = &Proxyer{}
	} else {
		rs = p
	}
	rs.Init(rpc.svc, id)
	//printf("GetProxy:%s, %s, %s", id, rs)
	return rs
}

func (rpc *RpcClient) StopService(svc *Service) {
	rpc.Stop()
}
