package grpc

import (
	"errors"
	"fmt"
	"io"
	"log"
	"runtime"
)

func recoverToError(r interface{}) (err error) {
	switch e := r.(type) {
	case error:
		err = e
	case string:
		err = errors.New(e)
	}
	return
}

func iftoui(v interface{}) uint {
	switch vv := v.(type) {
	case indexint:
		return uint(vv)
	case uint16:
		return uint(vv)
	case uint8:
		return uint(vv)
	case uint32:
		return uint(vv)
	case uint64:
		return uint(vv)
	case int8:
		return uint(vv)
	case int16:
		return uint(vv)
	case int32:
		return uint(vv)
	case int64:
		return uint(vv)
	}
	return 0
}

//nicetrace
func NiceRecover() interface{} {
	e := recover()
	PrintRecover(e)
	return e
}

func PrintRecover(e interface{}) interface{} {
	if e != nil {
		log.Printf("recover: %v\n", e)
		for skip := 1; ; skip++ {
			pc, file, line, ok := runtime.Caller(skip)
			if !ok {
				break
			}
			if file[len(file)-1] == 'c' {
				continue
			}
			f := runtime.FuncForPC(pc)
			fmt.Printf("    -->%s:%d %s()\n", file, line, f.Name())
		}
	}
	return e
}

//nicetrace
func WriteStacktrace(wr io.Writer) {
	for skip := 1; ; skip++ {
		pc, file, line, ok := runtime.Caller(skip)
		if !ok {
			break
		}
		if file[len(file)-1] == 'c' {
			continue
		}
		f := runtime.FuncForPC(pc)
		fmt.Fprintf(wr, "-->%s:%d %s()\n", file, line, f.Name())
	}
}
