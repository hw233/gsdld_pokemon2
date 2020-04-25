/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-18
 * Time: 上午11:43
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	_ "encoding/binary"
	//	msgpack "github.com/msgpack/msgpack-go"
	//	msgpack "github.com/ugorji/go-msgpack"
	"github.com/ugorji/go/codec"
)

var (
	DefaultPacker = &MsgPacker{}
	MsgPackH      = &codec.MsgpackHandle{}
)

func init() {
	MsgPackH.RawToString = true
}

type Packer interface {
	Pack(value interface{}) (data []byte, err error)
	Unpack(data []byte) (value interface{})
}

type MsgPacker struct {
}

func (mp *MsgPacker) Pack(v interface{}) (data []byte, err error) {
	//	data, err = msgpack.Marshal(v)
	err = codec.NewEncoderBytes(&data, MsgPackH).Encode(v)
	//	log.Println("msgpack:", v, data, err)
	return
}

func (mp *MsgPacker) Unpack(data []byte) (v interface{}) {
	//	msgpack.Unmarshal(data, &v, nil)
	codec.NewDecoderBytes(data, MsgPackH).Decode(&v)
	//	log.Println("msgUnpack:", v, data)
	return
}
