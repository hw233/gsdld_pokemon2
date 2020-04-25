/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-05-24
 * Time: 上午10:410
 * proxy
 */

package grpc

import (
	"reflect"
)

type Proxy interface {
	Init(svc *Service, id string)
	GetService() *Service
	Call(name string, args []interface{}, no_result, proxy bool, timeout int64) (interface{}, error)
}

type Proxyer struct {
	Svc *Service
	id  string
}

var ProxyType = reflect.TypeOf(&Proxyer{})

func (p *Proxyer) Init(svc *Service, id string) {
	p.Svc = svc
	p.id = id
}

func (p *Proxyer) GetService() *Service {
	return p.Svc
}

func (p *Proxyer) Call(name string, args []interface{},
	no_result, proxy bool, timeout int64) (rs interface{}, err error) {
	rs, err = p.Svc.Call(p.id, name, args, nil, no_result, proxy, timeout)
	return
}
