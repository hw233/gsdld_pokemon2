/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-29
 * Time: 上午11:24
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"bytes"
	"compress/gzip"
	"compress/zlib"
	"fmt"
	"github.com/golang/snappy"
	"io"
	"log"
	"math"
	"path"
	"reflect"
	"runtime"
	"sync"
)

type IterUInt16 struct {
	sync.Mutex
	index uint16
}

func (i *IterUInt16) Next() uint16 {
	i.Lock()
	defer i.Unlock()
	i.index += 1
	if i.index >= math.MaxUint16-1 {
		i.index = 1
	}
	return i.index
}

func iftoi(v interface{}) (i int64) {
	switch v.(type) {
	case uint, uint16, uint8, uint32, uint64:
		i = int64(reflect.ValueOf(v).Uint())
	case int, int8, int16, int32, int64:
		i = reflect.ValueOf(v).Int()
	}
	return i
}

//log
func Log(callerLevel int, format string, v ...interface{}) {
	msg := fmt.Sprintf(format, v...)
	pc, file, line, ok := runtime.Caller(callerLevel)
	if ok {
		log.Printf("{%s:%d (0x%x)} %s\n", path.Base(file), line, pc, msg)
	} else {
		log.Printf("{} %s\n", msg)
	}
}

//解压
func ZlibDecompress(b []byte) (rs []byte, err error) {
	buf := bytes.NewBuffer(b)
	r, err := zlib.NewReader(buf)
	if err != nil {
		return nil, err
	}
	buf = bytes.NewBuffer(nil)
	io.Copy(buf, r)
	r.Close()
	return buf.Bytes(), nil
}

//压缩
func ZlibCompress(b []byte) (rs []byte) {
	var buf bytes.Buffer
	w := zlib.NewWriter(&buf)
	w.Write(b)
	w.Close()
	rs = buf.Bytes()
	return
}

//解压
func GzipDecompress(b []byte) (rs []byte, err error) {
	buf := bytes.NewBuffer(b)
	r, err := gzip.NewReader(buf)
	if err != nil {
		return nil, err
	}
	buf = bytes.NewBuffer(nil)
	io.Copy(buf, r)
	r.Close()
	return buf.Bytes(), nil
}

//压缩
func GzipCompress(b []byte) (rs []byte) {
	var buf bytes.Buffer
	w := gzip.NewWriter(&buf)
	w.Write(b)
	w.Close()
	rs = buf.Bytes()
	return
}

//解压
func SnappyDecompress(b []byte) (rs []byte, err error) {
	rs, err = snappy.Decode(rs, b)
	return
}

//压缩
func SnappyCompress(b []byte) (rs []byte) {
	rs = snappy.Encode(rs, b)
	return
}
