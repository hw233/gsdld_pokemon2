package gateway

import (
	"bytes"
	"github.com/gorilla/websocket"
	"log"
	"net"
	"time"
)

type ConnProxy interface {
	Read(b *[]byte) (n int, err error)

	// Write writes data to the connection.
	// Write can be made to time out and return an Error with Timeout() == true
	// after a fixed time limit; see SetDeadline and SetWriteDeadline.
	Write(b []byte) (n int, err error)

	// Close closes the connection.
	// Any blocked Read or Write operations will be unblocked and return errors.
	Close() error

	// LocalAddr returns the local network address.
	LocalAddr() net.Addr

	// RemoteAddr returns the remote network address.
	RemoteAddr() net.Addr

	// SetDeadline sets the read and write deadlines associated
	// with the connection. It is equivalent to calling both
	// SetReadDeadline and SetWriteDeadline.
	//
	// A deadline is an absolute time after which I/O operations
	// fail with a timeout (see type Error) instead of
	// blocking. The deadline applies to all future and pending
	// I/O, not just the immediately following call to Read or
	// Write. After a deadline has been exceeded, the connection
	// can be refreshed by setting a deadline in the future.
	//
	// An idle timeout can be implemented by repeatedly extending
	// the deadline after successful Read or Write calls.
	//
	// A zero value for t means I/O operations will not time out.
	SetDeadline(t time.Time) error

	// SetReadDeadline sets the deadline for future Read calls
	// and any currently-blocked Read call.
	// A zero value for t means Read will not time out.
	SetReadDeadline(t time.Time) error

	// SetWriteDeadline sets the deadline for future Write calls
	// and any currently-blocked Write call.
	// Even if write times out, it may return n > 0, indicating that
	// some of the data was successfully written.
	// A zero value for t means Write will not time out.
	SetWriteDeadline(t time.Time) error

	InitSock()
}

type WebSocketProxy struct {
	conn *websocket.Conn
	buf  *bytes.Buffer
}

func NewWebSocketProxy(ws *websocket.Conn) ConnProxy {
	return &WebSocketProxy{conn: ws, buf: bytes.NewBuffer(nil)}
}

func (proxy *WebSocketProxy) Read(b *[]byte) (n int, err error) {
	_, p, err := proxy.conn.ReadMessage()
	if err != nil {
		log.Printf("[handler] WebSocketProxy proxy.conn.ReadMessage error:%s\n", err.Error())
		return
	}
	if len(p) > 0 {
		_, err = proxy.buf.Write(p)
		if err != nil {
			log.Printf("[handler] buf.Write error:%s\n", err.Error())
			return
		}
	}
	return proxy.buf.Read(*b)
}

func (proxy *WebSocketProxy) Write(b []byte) (n int, err error) {
	err = proxy.conn.WriteMessage(websocket.BinaryMessage, b)
	n = len(b)
	return
}

func (proxy *WebSocketProxy) Close() error {
	return proxy.conn.Close()
}

func (proxy *WebSocketProxy) LocalAddr() net.Addr {
	return proxy.conn.LocalAddr()
}

func (proxy *WebSocketProxy) RemoteAddr() net.Addr {
	return proxy.conn.RemoteAddr()
}

func (proxy *WebSocketProxy) SetDeadline(t time.Time) error {
	return nil
}

func (proxy *WebSocketProxy) SetReadDeadline(t time.Time) error {
	return proxy.conn.SetReadDeadline(t)
}

func (proxy *WebSocketProxy) SetWriteDeadline(t time.Time) error {
	return proxy.conn.SetWriteDeadline(t)
}

func (proxy *WebSocketProxy) InitSock() {
}

type TcpSocketProxy struct {
	conn net.Conn
}

func NewTcpSocketProxy(sock net.Conn) ConnProxy {
	return &TcpSocketProxy{conn: sock}
}

func (proxy *TcpSocketProxy) Read(b *[]byte) (n int, err error) {
	return proxy.conn.Read(*b)
}

func (proxy *TcpSocketProxy) Write(b []byte) (n int, err error) {
	return proxy.conn.Write(b)
}

func (proxy *TcpSocketProxy) Close() error {
	return proxy.conn.Close()
}

func (proxy *TcpSocketProxy) LocalAddr() net.Addr {
	return proxy.conn.LocalAddr()
}

func (proxy *TcpSocketProxy) RemoteAddr() net.Addr {
	return proxy.conn.RemoteAddr()
}

func (proxy *TcpSocketProxy) SetDeadline(t time.Time) error {
	return proxy.conn.SetDeadline(t)
}

func (proxy *TcpSocketProxy) SetReadDeadline(t time.Time) error {
	return proxy.conn.SetReadDeadline(t)
}

func (proxy *TcpSocketProxy) SetWriteDeadline(t time.Time) error {
	return proxy.conn.SetWriteDeadline(t)
}

func (proxy *TcpSocketProxy) InitSock() {
	tcpSock, ok := proxy.conn.(*net.TCPConn)
	if ok {
		tcpSock.SetNoDelay(false)
	}
}
