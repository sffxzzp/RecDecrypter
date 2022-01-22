import base64, os
from tempfile import NamedTemporaryFile
from Crypto.Cipher import AES

class dec:

	def add_to_16(self, value):
		while len(value) % 16 != 0:
			value += '\x00'
		return str.encode(value)

	def file_content(self, file, read_type):
		with open(file, read_type) as (targetfile):
			for line in targetfile:
				yield line

	def decrypt_oralce(self, encrypt_file):
		with NamedTemporaryFile('w+b', delete=False) as (f1):
			header = f1.name
		with NamedTemporaryFile('w+b', delete=False) as (dec1):
			dec_header = dec1.name
		f_read = open(encrypt_file, 'rb')
		header_write = open(header, 'wb')
		atmp = f_read.read(8)
		enc_header_size = int.from_bytes(atmp, byteorder='little', signed=True)
		f_read.seek(8)
		newByte1 = f_read.read(enc_header_size)
		header_write.write(newByte1)
		header_write.close()
		key = 'aanxinci2sh3en4g'
		text = ''
		for i in self.file_content(header, 'r'):
			text += str(i)

		aes = AES.new(self.add_to_16(key), AES.MODE_ECB)
		base64_decrypted = base64.decodebytes(text.encode(encoding='cp936'))
		decrypted_text = str((aes.decrypt(base64_decrypted)), encoding='gbk').replace('\x00', '')
		decrypted_text2 = eval(decrypted_text)
		with open(dec_header, 'wb+') as (f):
			f.write(decrypted_text2)
		f_read = open(encrypt_file, 'rb')
		dec_write = open('dec.img', 'wb')
		d_read = open(dec_header, 'rb')
		newByte = d_read.read()
		dec_write.write(newByte)
		d_read.close()
		f_read.seek(enc_header_size + 8, 0)
		newByte2 = f_read.read(os.path.getsize(encrypt_file) - enc_header_size - 8)
		dec_write.write(newByte2)
		dec_write.close()
		if os.path.exists(header):
			os.remove(header)
		if os.path.exists(dec_header):
			os.remove(dec_header)

decrypt = dec()
decrypt.decrypt_oralce(input('请输入文件名：'))