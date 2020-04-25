/**
 * Created with IntelliJ IDEA.
 * User: see
 * Date: 13-7-26
 * Time: 下午2:08
 * To change this template use File | Settings | File Templates.
 */
package gateway

import (
	"crypto/aes"
	"crypto/cipher"
	"log"
)

func PKCS7Padding(data []byte) []byte {

	// 数据的长度
	dataLen := len(data)

	var bit16 int

	if dataLen%16 == 0 {
		bit16 = dataLen + 16
	} else {
		// 计算补足的位数，填补16的位数，例如 10 = 16, 17 = 32, 33 = 48
		bit16 = int(dataLen/16+1) * 16
	}

	// 需要填充的数量
	paddingNum := bit16 - dataLen

	bitCode := byte(paddingNum)

	padding := make([]byte, paddingNum)
	for i := 0; i < paddingNum; i++ {
		padding[i] = bitCode

	}
	return append(data, padding...)
}

/**
 *	去除PKCS7的补码
 */
func UnPKCS7Padding(data []byte) []byte {
	dataLen := len(data)

	// 在使用PKCS7会以16的倍数减去数据的长度=补位的字节数作为填充的补码，所以现在获取最后一位字节数进行切割
	endIndex := int(data[dataLen-1])

	// 验证结尾字节数是否符合标准，PKCS7的补码字节只会是1-15的字节数
	if endIndex == 0 {
		return data[:dataLen-16]
	} else { //}if 16 > endIndex {
		// 判断结尾的补码是否相同 TODO 不相同也先不管了，暂时不知道怎么处理
		//		if 1 < endIndex {
		//			for i := dataLen - endIndex; i < dataLen; i++ {
		//				if data[dataLen-1] != data[i] {
		//					log.Println("不同的字节码，尾部字节码:", data[dataLen-1], "  下标：", i, "  字节码：", data[i])
		//				}
		//			}
		//		}

		return data[:dataLen-endIndex]
	}
	//	log.Println(endIndex)

	return nil
}

type AESEncrypter struct {
	key       []byte
	encrypter cipher.BlockMode
	decrypter cipher.BlockMode
}

func NewAESEncrypter(key []byte) (rs *AESEncrypter, err error) {
	ckey, err := aes.NewCipher([]byte(key))
	if nil != err {
		return nil, err
	}
	return &AESEncrypter{
		key:       key,
		encrypter: NewECBEncrypter(ckey),
		decrypter: NewECBDecrypter(ckey),
	}, nil
}

func (c *AESEncrypter) Encrypt(b []byte) (rs []byte) {
	// PKCS7补码
	b = PKCS7Padding(b)
	rs = make([]byte, len(b))
	c.encrypter.CryptBlocks(rs, b)
	return rs
}

func (c *AESEncrypter) Decrypt(b []byte) (rs []byte) {
	rs = make([]byte, len(b))
	c.decrypter.CryptBlocks(rs, b)
	rs = UnPKCS7Padding(rs)
	return rs
}

func aesEncrypt() {
	key := "mofeimofeimofeimofeimofeimofeimo"
	ckey, err := aes.NewCipher([]byte(key))
	if nil != err {
		log.Println("钥匙创建错误:", err)
	}

	str := []byte("1234567890")
	iv := []byte("1234567890123456")
	log.Println("加密的字符串", string(str), "\n加密钥匙", key, "\n向量IV", string(iv))

	log.Println("加密前的字节：", str, "\n")

	encrypter := NewECBEncrypter(ckey)

	// PKCS7补码
	str = PKCS7Padding(str)
	out := make([]byte, len(str))

	encrypter.CryptBlocks(out, str)

}
