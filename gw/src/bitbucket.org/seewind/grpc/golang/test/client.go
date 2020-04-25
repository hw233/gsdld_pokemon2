package main

import (
	"../../golang/grpc"
	"flag"
	"fmt"
	"log"
	"time"
	//	curl "github.com/go-av/curl"
)

const (
	svrTCPAddr = "0.0.0.0:18081"
	UNIXAddr   = "/tmp/grpc_svr.sock"
)

type MyServer struct {
	grpc.Proxyer
}

func (svr *MyServer) Echo(s string) (rs string, err error) {
	//	curl.String()
	r, err := svr.Call("echo", []interface{}{s}, false, false, 0)
	if err != nil {
		return
	}
	rs = r.(string)
	return
}

func (svr *MyServer) Test_proxy(export string) (rs interface{}, err error) {
	rs, err = svr.Call("test_proxy", []interface{}{export}, false, true, 0)
	return
}

type MyClient struct {
}

func (mc *MyClient) Get_name() (rs string, err error) {
	return "client", nil
}

func benchmark(concurrent, number int) {
	msg0 := "**********"
	index := 0

	bfunc := func(c chan int, proxy *MyServer, msg string) {
		rs, _ := proxy.Echo(msg)
		//		log.Printf("func:%s", rs)
		if rs == msg {
			c <- 1
		} else {
			log.Printf("result(%s) <> msg(%s)", rs, msg)
			c <- 0
		}

	}

	proxys := make([]*MyServer, concurrent)
	for i := 0; i < concurrent; i++ {
		c := grpc.NewRpcClient()
		err := c.Connect(svrTCPAddr, time.Second*10)
		if err != nil {
			log.Printf("error:%s", err.Error())
			return
		}
		c.Start()
		p, ok := c.GetProxy("server", new(MyServer)).(*MyServer)
		if !ok {
			log.Printf("GetProxy error")
			return
		}
		proxys[i] = p
	}

	begin := time.Now()
	for x := 0; x < number; x++ {
		i := 0
		c := make(chan int)
		for i, p := range proxys {
			msg := fmt.Sprintf("%d:%s", i, msg0)
			go bfunc(c, p, msg)
		}
		cc := 0
	for1:
		for {
			//log.Printf("begin:%d", x)
			select {
			case i = <-c:
				index = index + i
				cc++
			}
			if cc == concurrent {
				//				log.Printf("finish:%d", x)
				break for1
			}
		}
	}
	end := time.Now()
	t := float64(end.UnixNano()-begin.UnixNano()) / float64(time.Second)
	log.Printf("total:%f  %f per/sec", t, float64(index)/t)

	//stop
	for _, p := range proxys {
		p.Svc.Stop()
	}
}

func test1() {
	c := grpc.NewRpcClient()
	err := c.Connect(svrTCPAddr, time.Second*10)
	if err != nil {
		log.Printf("error:%s", err.Error())
		return
	}
	log.Println("start test1")
	c.Start()
	p := new(MyServer)
	p, ok := c.GetProxy("server", p).(*MyServer)
	if !ok {
		log.Printf("GetProxy error")
		return
	}
	log.Println("test1: echo")
	s, err := p.Echo("abc")
	log.Printf("echo:%s", s)

	mc := &MyClient{}
	ename := "client"
	c.Register(ename, mc)
	rs, err := p.Test_proxy(ename)
	log.Printf("test_proxy:%s, %s", rs, err)
	c.Stop()
}

func main() {
	b := flag.Int("b", 0, "benchmark")
	c := flag.Int("c", 90, "concurrent")
	n := flag.Int("n", 1000, "benchmark count")
	flag.Parse()
	switch *b {
	case 0:
		test1()
	case 1:
		benchmark(*c, *n)
	}

}
