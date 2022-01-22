package main

import (
	"bytes"
	"crypto/aes"
)

type (
	AESTool struct {
		Key       []byte
		BlockSize int
	}
)

func newAESTool(key []byte, blockSize int) *AESTool {
	return &AESTool{Key: key, BlockSize: blockSize}
}

func (a *AESTool) padding(src []byte) []byte {
	padlen := aes.BlockSize - len(src)%aes.BlockSize
	if padlen == 16 {
		return src
	} else {
		return append(src, bytes.Repeat([]byte{byte(0)}, padlen)...)
	}
}

func (a *AESTool) unpadding(src []byte) []byte {
	for i := len(src) - 1; ; i-- {
		if src[i] != 0 {
			return src[:i+1]
		}
	}
}

func (a *AESTool) Encrypt(src []byte) ([]byte, error) {
	a.Key = a.padding(a.Key)
	block, err := aes.NewCipher([]byte(a.Key))
	if err != nil {
		return nil, err
	}
	src = a.padding(src)
	encryptData := make([]byte, len(src))
	tmpData := make([]byte, a.BlockSize)
	for i := 0; i < len(src); i += a.BlockSize {
		block.Encrypt(tmpData, src[i:i+a.BlockSize])
		copy(encryptData[i:i+a.BlockSize], tmpData)
	}
	return encryptData, nil
}

func (a *AESTool) Decrypt(src []byte) ([]byte, error) {
	a.Key = a.padding(a.Key)
	block, err := aes.NewCipher([]byte(a.Key))
	if err != nil {
		return nil, err
	}
	decryptData := make([]byte, len(src))
	tmpData := make([]byte, a.BlockSize)
	for i := 0; i < len(src); i += a.BlockSize {
		block.Decrypt(tmpData, src[i:i+a.BlockSize])
		copy(decryptData[i:i+a.BlockSize], tmpData)
	}
	return a.unpadding(decryptData), nil
}
