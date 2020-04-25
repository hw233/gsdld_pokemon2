/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-05-16
 * Time: 上午10:36
 * grpc server
 */
package main

import (
	//	"fmt"
	"../../golang/grpc"
	"errors"
	"log"
	"reflect"
)

type MyExport struct {
}

func (my *MyExport) Echo(s string) (msg string, err error) {
	return s, nil
}

func (my *MyExport) Test_proxy(p *MyProxy) (rs string, err error) {
	//	log.Printf("Test_proxy:%s", p)
	rs, err = p.Get_name()
	log.Printf("rs:%s, err:%s", rs, err)
	//	p.Test_raise("abc")
	return
}

func (my *MyExport) Test_exception(p *grpc.Proxyer) (rs interface{}, err error) {
	rs, err = p.Call("test_raise", []interface{}{"go"}, false, false, 0)
	if err != nil {
		log.Printf("Test_exception:%s", err.Error())
	}
	return
}

func (my *MyExport) Test_proxys(proxys []interface{}) (rs interface{}, err error) {
	var p *MyProxy = proxys[0].(*MyProxy)
	s, err := p.Get_name()
	log.Printf("params:%s, p.Get_name:%s", proxys, s)
	return
}

type MyProxy struct {
	grpc.Proxyer
}

func (p *MyProxy) Get_name() (rs string, err error) {
	var r interface{}
	var ok bool
	r, err = p.Call("get_name", nil, false, false, 0)
	if err != nil {
		return
	}
	rs, ok = r.(string)
	if !ok {
		err = errors.New("result type error")
		rs = ""
	}
	log.Printf("Get_name:%s", rs)
	return
}

func (p *MyProxy) Test_raise(v string) (rs interface{}, err error) {
	rs, err = p.Call("test_raise", []interface{}{v}, false, false, 0)
	if err != nil {
		log.Printf("test_raise:%s", err.Error())
	}
	return
}

func t1() {
	var i interface{}
	vi, ok := i.(reflect.Value)
	v := reflect.ValueOf(i)
	log.Printf("vi:%s(%s), v:%s", vi, ok, v)
}

const (
	svrTCPAddr = "0.0.0.0:18081"
	UNIXAddr   = "/tmp/grpc_svr.sock"
)

func main() {
	t1()
	log.Printf("start")

	export := &MyExport{}

	svr := grpc.NewRpcServer()
	err := svr.Bind(svrTCPAddr)
	if err != nil {
		log.Println("bind error:%s", err.Error())
	}
	defer svr.Stop()
	svr.Register("server", export)
	svr.RegProxy("client", reflect.TypeOf(MyProxy{}))
	svr.Start(true)
}
