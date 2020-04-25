/**
 * Created with IntelliJ IDEA.
 * User: remote
 * Date: 12-12-18
 * Time: 上午10:42
 * To change this template use File | Settings | File Templates.
 */
package grpc

import (
	"reflect"
)

type methodType struct {
	//	sync.Mutex // protects counters
	method    reflect.Method
	mtype     reflect.Type
	numReturn int
	numCalls  uint
}

type Export struct {
	v      reflect.Value
	t      reflect.Type
	method map[string]*methodType
}

type exportHandler map[string]*Export

// suitableMethods returns suitable Rpc methods of typ, it will report
// error using log if reportErr is true.
func suitableMethods(typ reflect.Type, reportErr bool) (methods map[string]*methodType) {
	methods = make(map[string]*methodType)
	//printf("suitableMethods:%s", typ.Name())
	for m := 0; m < typ.NumMethod(); m++ {
		method := typ.Method(m)
		mtype := method.Type
		mname := method.Name
		//printf("suitableMethods:%s", mname)
		// Method must be exported.
		//		if false && method.PkgPath != "" {
		//			continue
		//		}
		numReturn := mtype.NumOut()
		methods[mname] = &methodType{method: method,
			mtype:     mtype,
			numReturn: numReturn,
		}
	}
	return methods
}

func newExportHandler() (hd exportHandler) {
	hd = make(exportHandler)
	return hd
}

func (hd *exportHandler) Register(name string, export interface{}) {
	e := &Export{v: reflect.ValueOf(export), t: reflect.TypeOf(export)}
	e.method = suitableMethods(e.t, true)
	(*hd)[name] = e
}

func (hd *exportHandler) UnRegister(name string) {
	delete(map[string]*Export(*hd), name)
}

func (hd *exportHandler) GetExport(name string) *Export {
	return map[string]*Export(*hd)[name]
}
