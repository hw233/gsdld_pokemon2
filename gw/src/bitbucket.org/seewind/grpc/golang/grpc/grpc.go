/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-11
 * Time: 上午11:06
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	"errors"
	"net"
	"reflect"
	"time"
)

const (
	//rpc数据类型
	RT_REQUEST = 1 << iota
	RT_RESPONSE
	RT_HEARTBEAT
	RT_EXCEPTION
	//rpc处理类型
	ST_NO_RESULT = 1 << 5
	ST_NO_MSG    = 1 << 6
	//rpc参数类型
	DT_PICKLE = 1 << 7 //默认用msgpack
	DT_ZIP    = 1 << 8
	DT_PROXY  = 1 << 9 //标示传递的第1个参数是obj, 需要转换成proxy
	//rpc数据类型 mark
	RT_MARK = ST_NO_RESULT - 1

	CALL_TIMEORUT = 120
	ZIP_LENGTH    = 1024 * 2 //if argkw > Nk, use zlib to compress
	ZIP_LEVEL     = 3
)

var (
	Debug             = true
	DEFAULT_TIMEOUT   = 30 * time.Second
	HEARTBEAT_TIME    = 60 * time.Second //heartbeat, if disconnect time > (HEARTBEAT_TIME + RECONNECT_TIMEOUT), connect lost
	RECONNECT_TIMEOUT = 3                //wait reconnect time, zero will disable reconnect wait
)

type Rpc interface {
	Pack(value interface{}) (data []byte, err error)
	Unpack(data []byte) (value interface{})
	GetExport(obj_id string) *Export
	RegProxy(id string, ptype reflect.Type) error
	NewProxy(id string) (rs reflect.Value, err error)
	StopService(svc *Service)
}

type rpcBase struct {
	Started bool
	Net     string
	Addr    net.Addr
	SAddr   string
	Host    string
	Port    int
	exports exportHandler
	Packer  Packer
	proxys  map[string]reflect.Type
}

func resolveAddr(addr string) (network string, rs net.Addr, err error) {
	network = "tcp"
	rs, err = net.ResolveTCPAddr(network, addr)
	if err != nil {
		network = "unix"
		rs, err = net.ResolveUnixAddr(network, addr)
	}
	return
}

func (rpc *rpcBase) Init() {
	rpc.Packer = DefaultPacker
	rpc.exports = newExportHandler()
	rpc.proxys = make(map[string]reflect.Type)
}

func (rpc *rpcBase) Pack(value interface{}) (data []byte, err error) {
	return rpc.Packer.Pack(value)
}

func (rpc *rpcBase) Unpack(data []byte) (value interface{}) {
	return rpc.Packer.Unpack(data)
}

func (rpc *rpcBase) resolveAddr(addr string) (err error) {
	rpc.Net, rpc.Addr, err = resolveAddr(addr)
	if err != nil {
		return err
	}
	rpc.SAddr = addr
	return err
}

func (rpc *rpcBase) Start() {
	if rpc.Started {
		return
	}
	rpc.Started = true
}

func (rpc *rpcBase) Stop() {
	if !rpc.Started {
		return
	}
	rpc.Started = false
}

func (rpc *rpcBase) Register(name string, export interface{}) {
	rpc.exports.Register(name, export)
}

func (rpc *rpcBase) UnRegister(name string) {
	rpc.exports.UnRegister(name)
}

func (rpc *rpcBase) GetExport(obj_id string) *Export {
	return rpc.exports.GetExport(obj_id)
}

func (rpc *rpcBase) RegProxy(id string, ptype reflect.Type) error {
	if ptype.ConvertibleTo(ProxyType) {
		return errors.New("Can not ConvertibleTo Proxy")
	}
	rpc.proxys[id] = ptype
	return nil
}

func (rpc *rpcBase) NewProxy(id string) (rs reflect.Value, err error) {
	t, ok := rpc.proxys[id]
	if !ok {
		//fmt.Errorf("Proxy(%s) no found", id)
		p := new(Proxyer)
		return reflect.ValueOf(p), nil
	}
	return reflect.New(t), nil
}

//
//
