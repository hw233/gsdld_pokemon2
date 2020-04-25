/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-19
 * Time: 下午1:53
 * To change this template use File | Settings | File Templates.
 */
package main

import (
	"bitbucket.org/seewind/gateway"
	"bitbucket.org/seewind/grpc/golang/grpc"
	"flag"
	"fmt"
	"gate"
	"github.com/gorilla/websocket"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"path"
	"path/filepath"
	"runtime"
	"runtime/pprof"
	"strings"
	"syscall"
	"time"
)

var port *int = flag.Int("p", 18011, "port")
var defaultGameAddr *string = flag.String("GAddr", "127.0.0.1:18002", "default gameserver addr, like: 127.0.0.1:18002")
var aes_key *string = flag.String("ak", "4fcc09d3ceb79129", "default aes_key, like: 4fcc09d3ceb79129")
var connMode *string = flag.String("ct", "tcp", "net connect type")
var isSSL *int = flag.Int("ssl", 0, "isSSL")
var certFile *string = flag.String("certFile", "1_game.chinakinggame.com_bundle.crt", "ssl certFile")
var keyFile *string = flag.String("keyFile", "2_game.chinakinggame.com.key", "ssl keyFile")

var upgrader = websocket.Upgrader{
	CheckOrigin: func(_ *http.Request) bool { return true },
} // use default options
var gw *gateway.Gateway

func getHome() string {
	// home := os.Getenv("HOME")
	// if home == "" {
	home, _ := os.Getwd()
	// }
	return home
}

func profile() {
	pwd := getHome()
	fname := path.Join(pwd, "prof.cmd")
	for {
		input, err := ioutil.ReadFile(fname)
		if err != nil || len(input) == 0 {
			time.Sleep(2 * time.Second)
			continue
		}
		ioutil.WriteFile(fname, []byte(""), 0744)
		cmd := strings.Trim(string(input), "\n\r\t")
		var p *pprof.Profile
		switch cmd {
		case "lookup goroutine":
			p = pprof.Lookup("goroutine")
		case "lookup heap":
			p = pprof.Lookup("heap")
		case "lookup threadcreate":
			p = pprof.Lookup("threadcreate")
		default:
			log.Println("unknow command: '" + cmd + "'")
		}
		if p != nil {
			file, err := os.Create(path.Join(pwd, "prof.out"))
			if err != nil {
				log.Println("couldn't create prof.out")
			} else {
				p.WriteTo(file, 2)
			}
		}
		time.Sleep(2 * time.Second)
	}
}

func home(w http.ResponseWriter, r *http.Request) {
	wsc, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		log.Print("upgrade:", err)
		return
	}
	conn := gateway.NewWebSocketProxy(wsc)
	gw.Accept(conn)
}

// 响应系统中断事件
func handleSignal() {
	ch := make(chan os.Signal)
	for {
		signal.Notify(ch, syscall.SIGINT, syscall.SIGHUP, syscall.SIGKILL, syscall.SIGTERM)
		sig := <-ch
		switch sig {
		default:
			log.Println("[*] other signal:", sig)
		case syscall.SIGINT:
			log.Println("[*] on sigint")
			os.Exit(1)
		case syscall.SIGHUP:
			log.Println("[*] on sighup")
			os.Exit(1)
		case syscall.SIGKILL:
			log.Println("[*] on sigkill")
			os.Exit(1)
		case syscall.SIGTERM:
			log.Println("[*] on sigterm")
			os.Exit(1)
		}
	}
}

func getCurrentDirectory() string {
	dir, err := filepath.Abs(filepath.Dir(os.Args[0])) //返回绝对路径  filepath.Dir(os.Args[0])去除最后一个元素的路径
	if err != nil {
		log.Fatal(err)
	}
	return strings.Replace(dir, "\\", "/", -1) //将\替换成/
}

func main() {
	exeDir := getCurrentDirectory()
	log.Println("EXE_DIR:" + exeDir)
	os.Chdir(exeDir)
	flag.Parse()
	if port == nil {
		panic("no port")
	}
	np := runtime.NumCPU()
	//多cpu可能会引起rpc.service处理tcp包顺序乱掉,考虑到rpc的设计是无序的,顺序问题需要在其它地方解决,如:RespAndSends
	//np = 1
	runtime.GOMAXPROCS(np)

	grpc.HEARTBEAT_TIME = 60 * time.Second
	grpc.RECONNECT_TIMEOUT = 5

	pwd := getHome()
	log.SetFlags(log.Lshortfile | log.LstdFlags)
	log.Println("gateway running at:", *port, "NumCPU:", np, "pwd:", pwd,
		"\nDefaultGameAddr:", *defaultGameAddr, "aes_key:", *aes_key)
	gateway.DefaultGameAddr = *defaultGameAddr
	gate.AES_KEY = *aes_key
	go profile()

	gate.InitAes()

	f := gate.NewMyFactory()
	gw = gateway.NewGateway(f)
	listenAddr := fmt.Sprintf("0.0.0.0:%d", *port)
	if *connMode == "ws" {
		http.HandleFunc("/", home)
		log.Println("websocket mode")
		if *isSSL == 1 {
			go func() {
				listenAddrTLS := fmt.Sprintf("0.0.0.0:%d", *port+4)
				log.Fatal(http.ListenAndServeTLS(listenAddrTLS, *certFile, *keyFile, nil))
			}()

		}

		log.Fatal(http.ListenAndServe(listenAddr, nil))

		handleSignal()
	} else if *connMode == "tcp" {
		err := gw.Listen("tcp", listenAddr)
		log.Println("tcp mode")
		if err != nil {
			log.Println("Listen(", listenAddr, ") error:", err)
			return
		}
		gw.StartForever()
	}
}
