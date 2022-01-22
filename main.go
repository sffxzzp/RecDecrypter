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

func (d *dec) b2b(bstr []byte) []byte {
	bstr = bstr[2 : len(bstr)-1]
	ostr := make([]byte, len(bstr))
	index := 0
	for i := 0; i < len(bstr); i++ {
		if bstr[i] == byte('\\') {
			if bstr[i+1] == byte('x') {
				otmp, _ := hex.DecodeString(string(bstr[i+2 : i+4]))
				copy(ostr[index:], otmp)
				i += 3
			} else if bstr[i+1] == byte('b') {
				copy(ostr[index:], []byte{0x08})
				i += 1
			} else if bstr[i+1] == byte('n') {
				copy(ostr[index:], []byte{0x0a})
				i += 1
			} else if bstr[i+1] == byte('r') {
				copy(ostr[index:], []byte{0x0d})
				i += 1
			} else if bstr[i+1] == byte('t') {
				copy(ostr[index:], []byte{0x09})
				i += 1
			} else if bstr[i+1] == byte('\'') {
				copy(ostr[index:], []byte{'\''})
				i += 1
			} else if bstr[i+1] == byte('"') {
				copy(ostr[index:], []byte{'"'})
				i += 1
			} else if bstr[i+1] == byte('\\') {
				copy(ostr[index:], []byte{'\\'})
				i += 1
			}
		} else {
			if bytes.Equal(bstr[i:i+3], []byte{'\'', 'b', '\''}) || bytes.Equal(bstr[i:i+3], []byte{'\'', 'b', '"'}) || bytes.Equal(bstr[i:i+3], []byte{'"', 'b', '\''}) || bytes.Equal(bstr[i:i+3], []byte{'"', 'b', '"'}) {
				i += 2
				index--
			} else {
				copy(ostr[index:], bstr[i:i+1])
			}
		}
		index++
	}
	for i := len(ostr) - 1; ; i-- {
		if ostr[i] != 0 {
			return ostr[:i+1]
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
	dec_header = d.b2b(dec_header)

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
