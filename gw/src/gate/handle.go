/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-26
 * Time: 下午2:08
 * To change this template use File | Settings | File Templates.
 */
package gate

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"runtime/debug"
	"sync"
	"time"

	"bitbucket.org/seewind/gateway"
	//"log"
)

const (
	RecvAndSendHeartbeat = true
	PACK_AES             = false
	PACK_ZIP             = true
	//data
	HEAD_DATA_LEN  = 4
	READTIMEOUTSEC = 600
)

var (
	svrLock sync.Mutex
	//	locks     map[string]*sync.Mutex
	aes       *gateway.AESEncrypter
	BIN_HEART []byte
	AES_KEY   string
)

type MyFactory struct {
}

func (f *MyFactory) NewHandler(g *gateway.Gate) gateway.GateHandle {
	return NewMyHandler(g)
}

func (f *MyFactory) NewProcesser(g *gateway.Gate) gateway.GateProcess {
	return gateway.NewProcesser(g)
}

func NewMyFactory() (f *MyFactory) {
	f = &MyFactory{}
	return f
}

type MyHandler struct {
	gateway.BuffHandler
}

func NewMyHandler(g *gateway.Gate) (h *MyHandler) {
	h = &MyHandler{*gateway.NewBuffHandler(g, 0)}
	// set socket timeout
	h.SetTimeout(READTIMEOUTSEC * time.Second) //test
	return
}

func (h *MyHandler) log(format string, v ...interface{}) {
	gateway.Log(2, fmt.Sprintf("[handler-%s]pid(%d): ", h.G.RemoteAddr(), h.G.Processer.GetPid())+format, v...)
}

func (h *MyHandler) unPack(data []byte) (rs []byte, err error) {
	rs = data
	//aes
	if PACK_AES {
		rs = aes.Decrypt(rs)
	}
	//压缩  客户端不压缩了
	//if PACK_ZIP {
	//	rs, err = gateway.SnappyDecompress(rs)
	//	if err != nil {
	//		return
	//	}
	//}
	return
}

func (h *MyHandler) pack(data []byte) (rs []byte, err error) {
	rs = data
	//压缩
	if PACK_ZIP {
		rs = gateway.SnappyCompress(rs)
		// rs = gateway.GzipCompress(rs)
	}
	//aes
	if PACK_AES {
		rs = aes.Encrypt(rs)
	}
	return
}

func (h *MyHandler) Loop() {
	defer func() {
		if r := recover(); r != nil {
			h.log("Loop error:%s", r)
			debug.PrintStack()
		}
		h.UnInitSock()
		h.log("Loop stop")
	}()
	h.InitSock()

	h.log("Loop start")
	for !h.G.Stoped {
		//h.log("Before ReadPack")

		b, err := h.ReadPack()
		//h.log("ReadPack:%r, %r, %r", b, err)

		if err != nil {
			h.log("read error:%s", err.Error())
			break
		}

		b, err = h.unPack(b)
		if err != nil {
			h.log("UnPack error:%s", err.Error())
			continue
		}

		//h.log("read:%s", v)
		err = h.G.Processer.Process(b)
		if err != nil {
			h.log("read error:%s", err.Error())
			break
		}
		//h.log("loop one end")
	}
}

// server push message to client
func (h *MyHandler) Push(data []byte) {
	// h.log("Push:%d", len(data))
	h.WritePack(data)
}

//send heartbeat
func (h *MyHandler) Heartbeat() {
	//log.Printf("[handler(%d)Heartbeat send!!!!\n", h.G.Processer.GetPid())
	h.Write(BIN_HEART)
}

func (h *MyHandler) readOne() (b []byte, err error) {
	var d []byte
	for {
		if h.Buf.Len() < HEAD_DATA_LEN {
			return
		}
		d = h.Buf.Bytes()
		if bytes.Compare(d[:HEAD_DATA_LEN], BIN_HEART) == 0 {
			if RecvAndSendHeartbeat {
				h.Heartbeat()
			}
			h.Buf.Next(HEAD_DATA_LEN)
			continue
		}
		break
	}
	dlen := binary.LittleEndian.Uint32(d[:HEAD_DATA_LEN])
	// h.log("***readOne: len:%d, %s", dlen, hex.Dump(d[:HEAD_DATA_LEN]))
	if len(d) < int(dlen)+HEAD_DATA_LEN {
		return nil, nil
	}

	h.Buf.Next(HEAD_DATA_LEN)
	d = make([]byte, dlen)
	_, err = h.Buf.Read(d)
	if err != nil {
		return nil, err
	}
	return d, nil
}

func (h *MyHandler) ReadPack() (b []byte, err error) {
	for {
		b, err = h.readOne()
		if b != nil || err != nil {
			return
		}

		n, err := h.ReadToBuff()
		if n == 0 {
			return nil, gateway.ErrClose
		}
		if err != nil {
			return nil, err
		}
	}
}

func (h *MyHandler) WritePack(b []byte) (err error) {
	// h.log("WritePack1:%d === %s", len(b), string(b))
	b, err = h.pack(b)
	if err != nil {
		h.log("WritePack msg(%s) error:%s", string(b), err.Error())
		return
	}

	var buf bytes.Buffer
	l := len(b)
	head := make([]byte, HEAD_DATA_LEN)
	binary.LittleEndian.PutUint32(head, uint32(l))
	buf.Write(head)
	//<data>
	buf.Write(b)
	d := buf.Bytes()
	//	h.log("WritePack2:%d === %s", len(d), string(d))
	h.Write(d)
	return nil
}

func InitAes() {
	//	locks = make(map[string]*sync.Mutex)
	aes, _ = gateway.NewAESEncrypter([]byte(AES_KEY))
	BIN_HEART = make([]byte, HEAD_DATA_LEN)
}
