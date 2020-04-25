/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-29
 * Time: 上午11:24
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"log"
	"syscall"
)

func syscallLimit() {
	var rlim, rlim1 syscall.Rlimit
	err := syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rlim)
	if err != nil {
		log.Println("get rlimit error: " + err.Error())
	}
	log.Println("system rlimit:", rlim)
	rlim1.Cur = 65536
	rlim1.Max = 65536
	syscall.Setrlimit(syscall.RLIMIT_NOFILE, &rlim1)
	syscall.Getrlimit(syscall.RLIMIT_NOFILE, &rlim)
	log.Println("set rlimit:", rlim)
}
