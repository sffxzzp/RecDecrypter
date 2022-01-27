package main

import (
	"bytes"
	"encoding/base64"
	"encoding/binary"
	"encoding/hex"
	"fmt"
	"os"
	"strings"
)

type (
	dec struct {
		key string
	}
)

func pathExists(path string) bool {
	if _, err := os.Stat(path); os.IsNotExist(err) {
		fmt.Printf("%s 文件未找到！\n", path)
		return false
	}
	return true
}

func newDec() *dec {
	return &dec{
		key: "aanxinci2sh3en4g",
	}
}

func (d *dec) bytes2int(b []byte) int {
	bytesBuffer := bytes.NewBuffer(b)
	var x int64
	binary.Read(bytesBuffer, binary.LittleEndian, &x)
	return int(x)
}

func (d *dec) decBytes(istr []byte) []byte {
	ostr := make([]byte, len(istr))
	index := 0
	for i := 0; i < len(istr); i++ {
		if istr[i] == byte('b') {
			if istr[i+1] == byte('\'') {
				otmp, offset := d.readto(istr[i+2:], byte('\''))
				copy(ostr[index:], otmp)
				index += offset
				i += offset
			} else if istr[i+1] == byte('"') {
				otmp, offset := d.readto(istr[i+2:], byte('"'))
				copy(ostr[index:], otmp)
				index += offset
				i += offset
			}
		}
	}
	return d.b2b(ostr)
}

func (d *dec) readto(istr []byte, end byte) ([]byte, int) {
	for i := 0; i < len(istr); i++ {
		if istr[i] == byte('\\') {
			if istr[i+1] == byte('x') {
				i += 3
			} else if istr[i+1] == byte('b') || istr[i+1] == byte('n') || istr[i+1] == byte('r') || istr[i+1] == byte('t') || istr[i+1] == byte('\'') || istr[i+1] == byte('"') || istr[i+1] == byte('\\') {
				i += 1
			}
		} else if istr[i] == end {
			return istr[:i], i
		}
	}
	return istr, 0
}

func (d *dec) b2b(istr []byte) []byte {
	ostr := make([]byte, len(istr))
	index := 0
	for i := 0; i < len(istr); i++ {
		if istr[i] == byte('\\') {
			if istr[i+1] == byte('x') {
				otmp, _ := hex.DecodeString(string(istr[i+2 : i+4]))
				copy(ostr[index:], otmp)
				i += 3
			} else if istr[i+1] == byte('b') {
				copy(ostr[index:], []byte{byte('\b')})
				i += 1
			} else if istr[i+1] == byte('n') {
				copy(ostr[index:], []byte{byte('\n')})
				i += 1
			} else if istr[i+1] == byte('r') {
				copy(ostr[index:], []byte{byte('\r')})
				i += 1
			} else if istr[i+1] == byte('t') {
				copy(ostr[index:], []byte{byte('\t')})
				i += 1
			} else if istr[i+1] == byte('\'') {
				copy(ostr[index:], []byte{byte('\'')})
				i += 1
			} else if istr[i+1] == byte('"') {
				copy(ostr[index:], []byte{byte('"')})
				i += 1
			} else if istr[i+1] == byte('\\') {
				copy(ostr[index:], []byte{byte('\\')})
				i += 1
			}
		} else {
			copy(ostr[index:], istr[i:i+1])
		}
		index++
	}
	return d.unpadding(ostr)
}

func (d *dec) unpadding(bstr []byte) []byte {
	for i := len(bstr) - 1; ; i-- {
		if bstr[i] != 0 {
			return bstr[:i+1]
		}
	}
}

func (d *dec) decrypt(enfile string) {
	f_read, _ := os.Open(enfile)
	defer f_read.Close()
	fi, _ := f_read.Stat()
	atmp := make([]byte, 8)
	f_read.Read(atmp)
	f_read.Seek(8, 0)
	enc_header_size := d.bytes2int(atmp)
	text := make([]byte, enc_header_size)
	f_read.Read(text)

	base64_decrypted, _ := base64.StdEncoding.DecodeString(string(text))
	AES := newAESTool([]byte(d.key), 16)
	dec_header, _ := AES.Decrypt(base64_decrypted)
	dec_header = d.decBytes(dec_header)

	f_read.Seek(int64(enc_header_size)+8, 0)
	newByte2 := make([]byte, fi.Size()-int64(enc_header_size)-8)
	f_read.Read(newByte2)
	outImg := append(dec_header, newByte2...)
	os.WriteFile(strings.Replace(enfile, ".img", "_decrypted.img", 1), outImg, 0777)
}

func main() {
	enfile := "enc.img"
	for !pathExists(enfile) {
		fmt.Print("请输入需要解密的 Recovery 文件的路径：")
		fmt.Scanln(&enfile)
	}
	decrypt := newDec()
	decrypt.decrypt(enfile)
}
