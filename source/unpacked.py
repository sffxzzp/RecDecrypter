# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:01:55) [MSC v.1900 32 bit (Intel)]
# Embedded file name: 残芯刷twrp工具.py
import base64, os, subprocess, sys, time
from datetime import datetime
from tempfile import NamedTemporaryFile
from Crypto.Cipher import AES
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from xinkidui import Ui_Dialog
import shutil, subprocess, traceback, tempfile, os, stat, shutil, binascii
from Crypto.Cipher import AES
import zipfile
from os.path import basename
import collections, numpy as np

def resource_path(filaeName):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filaeName)
    return os.path.join(filaeName)


fastboot = resource_path('fastboot.exe')
qqcode = resource_path('qqun2.png')
recovery_misc = resource_path('misc.bin')
adb = resource_path('adb.exe')
scrcpy = resource_path('scrcpy-noconsole.vbs')
AdbWinApi = resource_path('AdbWinApi.dll')
AdbWinUsbApi = resource_path('AdbWinUsbApi.dll')
superfile = resource_path('superfile')
payload_extractor = resource_path('tools/payload_extractor.exe')

class MyWindow(Ui_Dialog, QDialog):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setupUi(self)
        self.lineEdit.setReadOnly(True)
        self.chose_zip.setReadOnly(True)
        self.logcat.setReadOnly(True)
        self.choose_image.clicked.connect(self.msg_choose)
        self.choose_romfile.clicked.connect(self.msg_choose_rom)
        self.reboot_fastboot.clicked.connect(self.msg_adb_reboot_fastboot)
        self.reboot_system.clicked.connect(self.msg_fastboot_reboot)
        self.start_flash.clicked.connect(self.msg_flash_rom)
        self.flash_image.clicked.connect(self.msg_flash_image)
        self.flash_boot.clicked.connect(self.msg_flash_boot)
        self.fastboot_boot.clicked.connect(self.msg_fastboot_boot)
        self.reboot1.clicked.connect(self.msg_reboot1)
        self.reboot2.clicked.connect(self.msg_reboot2)
        self.phone_scrcpy.clicked.connect(self.msg_adb_scrcpy)
        img_path = qqcode
        image = QtGui.QPixmap(img_path).scaled(156, 156)
        self.qqun.setPixmap(image)

    def ozip2zip(self, file_arg):
        keys = [
         'D6EECF0AE5ACD4E0E9FE522DE7CE381E',
         'D6ECCF0AE5ACD4E0E92E522DE7C1381E',
         'D6DCCF0AD5ACD4E0292E522DB7C1381E',
         'D7DCCE1AD4AFDCE2393E5161CBDC4321',
         'D7DBCE2AD4ADDCE1393E5521CBDC4321',
         'D7DBCE1AD4AFDCE1393E5121CBDC4321',
         'D4D2CD61D4AFDCE13B5E01221BD14D20',
         '261CC7131D7C1481294E532DB752381E',
         '1CA21E12271335AE33AB81B2A7B14622',
         'D4D2CE11D4AFDCE13B3E0121CBD14D20',
         '1C4C1EA3A12531AE491B21BB31613C11',
         '1C4C1EA3A12531AE4A1B21BB31C13C21',
         '1C4A11A3A12513AE441B23BB31513121',
         '1C4A11A3A12589AE441A23BB31517733',
         '1C4A11A3A22513AE541B53BB31513121',
         '2442CE821A4F352E33AE81B22BC1462E',
         '14C2CD6214CFDC2733AE81B22BC1462C',
         '1E38C1B72D522E29E0D4ACD50ACFDCD6',
         '12341EAAC4C123CE193556A1BBCC232D',
         '2143DCCB21513E39E1DCAFD41ACEDBD7',
         '2D23CCBBA1563519CE23C1C4AA1E3412',
         '172B3E14E46F3CE13E2B5121CBDC4321',
         'ACAA1E12A71431CE4A1B21BBA1C1C6A2',
         'ACAC1E13A72531AE4A1B22BB31C1CC22',
         '1C4411A3A12533AE441B21BB31613C11',
         '1C4416A8A42717AE441523B336513121',
         '55EEAA33112133AE441B23BB31513121',
         'ACAC1E13A12531AE4A1B21BB31C13C21',
         'ACAC1E13A72431AE4A1B22BBA1C1C6A2',
         '12CAC11211AAC3AEA2658690122C1E81',
         '1CA21E12271435AE331B81BBA7C14612',
         'D1DACF24351CE428A9CE32ED87323216',
         'A1CC75115CAECB890E4A563CA1AC67C8',
         '2132321EA2CA86621A11241ABA512722',
         '22A21E821743E5EE33AE81B227B1462E']

        def keytest(data):
            for key in keys:
                ctx = AES.new(binascii.unhexlify(key), AES.MODE_ECB)
                dat = ctx.decrypt(data)
                if dat[0:4] == b'PK\x03\x04':
                    print('Found correct AES key: ' + key)
                    return binascii.unhexlify(key)
                    if dat[0:4] == b'AVB0':
                        print('Found correct AES key: ' + key)
                        return binascii.unhexlify(key)
                    if dat[0:4] == b'ANDR':
                        print('Found correct AES key: ' + key)
                        return binascii.unhexlify(key)

            return -1

        def del_rw(action, name, exc):
            os.chmod(name, stat.S_IWRITE)
            os.remove(name)

        def rmrf(path):
            if os.path.exists(path):
                if os.path.isfile(path):
                    del_rw('', path, '')
                else:
                    shutil.rmtree(path, onerror=del_rw)

        def decryptfile(key, rfilename):
            with open(rfilename, 'rb') as (rr):
                with open(rfilename + '.tmp', 'wb') as (wf):
                    rr.seek(16)
                    dsize = int(rr.read(16).replace(b'\x00', b'').decode('utf-8'), 10)
                    rr.seek(4176)
                    print('Decrypting ' + rfilename)
                    flen = os.stat(rfilename).st_size - 4176
                    ctx = AES.new(key, AES.MODE_ECB)
                    while dsize > 0:
                        if flen > 16384:
                            size = 16384
                        else:
                            size = flen
                        data = rr.read(size)
                        if dsize < size:
                            size = dsize
                        if len(data) == 0:
                            break
                        dr = ctx.decrypt(data)
                        wf.write(dr[:size])
                        flen -= size
                        dsize -= size

            os.remove(rfilename)
            os.rename(rfilename + '.tmp', rfilename)

        def decryptfile2(key, rfilename, wfilename):
            with open(rfilename, 'rb') as (rr):
                with open(wfilename, 'wb') as (wf):
                    ctx = AES.new(key, AES.MODE_ECB)
                    bstart = 0
                    goon = True
                    while goon:
                        rr.seek(bstart)
                        header = rr.read(12)
                        if len(header) == 0:
                            break
                        if header != b'OPPOENCRYPT!':
                            return 1
                        rr.seek(16 + bstart)
                        bdsize = int(rr.read(16).replace(b'\x00', b'').decode('utf-8'), 10)
                        if bdsize < 262144:
                            goon = False
                        rr.seek(80 + bstart)
                        while bdsize > 0:
                            data = rr.read(16)
                            if len(data) == 0:
                                break
                            size = 16
                            if bdsize < 16:
                                size = bdsize
                            dr = ctx.decrypt(data)
                            wf.write(dr[:size])
                            bdsize -= 16
                            data = rr.read(16368)
                            if len(data) == 0:
                                break
                            bdsize -= 16368
                            wf.write(data)

                        bstart = bstart + 262144 + 80

            return 0

        def mode2(filename):
            temp = os.path.join(os.path.abspath(os.path.dirname(filename)), 'temp')
            out = os.path.join(os.path.abspath(os.path.dirname(filename)), 'out')
            with open(filename, 'rb') as (fr):
                magic = fr.read(12)
                if magic[:2] == b'PK':
                    with zipfile.ZipFile(file_arg, 'r') as (zipObj):
                        if os.path.exists(temp):
                            rmrf(temp)
                        os.mkdir(temp)
                        if os.path.exists(out):
                            rmrf(out)
                        os.mkdir(out)
                        print('Finding key...  ' + file_arg)
                        for zi in zipObj.infolist():
                            orgfilename = zi.filename
                            if 'boot.img' in orgfilename:
                                zi.filename = 'out'
                                zipObj.extract(zi, temp)
                                zi.filename = orgfilename
                                with open(os.path.join(temp, 'out'), 'rb') as (rr):
                                    magic = rr.read(12)
                                    if magic == b'OPPOENCRYPT!':
                                        rr.seek(80)
                                        data = rr.read(16)
                                        key = keytest(data)
                                        if key == -1:
                                            print('Unknown AES key, reverse key from recovery first!')
                                            return 1
                                        break
                                    else:
                                        print("Unknown mode2, boot.img wasn't encrypted")
                                        return 1

                        print('Extracting...  ' + file_arg)
                        outzip = filename[:-4] + 'zip'
                        if os.path.exists(outzip):
                            os.remove(outzip)
                        with zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED) as (WzipObj):
                            for zi in zipObj.infolist():
                                orgfilename = zi.filename
                                zi.filename = 'out'
                                zipObj.extract(zi, temp)
                                zi.filename = orgfilename
                                with open(os.path.join(temp, 'out'), 'rb') as (rr):
                                    magic = rr.read(12)
                                    if magic == b'OPPOENCRYPT!':
                                        print('Decrypting ' + orgfilename)
                                        if decryptfile2(key, os.path.join(temp, 'out'), os.path.join(temp, 'out') + '.dec') == 1:
                                            return 1
                                        WzipObj.write(os.path.join(temp, 'out') + '.dec', orgfilename)
                                        os.remove(os.path.join(temp, 'out'))
                                        os.remove(os.path.join(temp, 'out') + '.dec')
                                    else:
                                        WzipObj.write(os.path.join(temp, 'out'), orgfilename)
                                        os.remove(os.path.join(temp, 'out'))

                        rmrf(temp)
                        print('DONE... file decrypted to: ' + outzip)
                        self.msg_log('DONE... file decrypted to: ' + outzip)
                        return 0

        print('ozipdecrypt 1.3 (c) B.Kerler 2017-2021')
        filename = file_arg
        with open(filename, 'rb') as (fr):
            magic = fr.read(12)
            if magic == b'OPPOENCRYPT!':
                pk = False
            else:
                if magic[:2] == b'PK':
                    pk = True
                else:
                    print('ozip has unknown magic, OPPOENCRYPT! expected!')
                    self.log('ozip has unknown magic, OPPOENCRYPT! expected!')
                    return 1
            if pk == False:
                fr.seek(4176)
                data = fr.read(16)
                key = keytest(data)
                if key == -1:
                    print('Unknown AES key, reverse key from recovery first!')
                    self.msg_log('Unknown AES key, reverse key from recovery first!')
                    return 1
                ctx = AES.new(key, AES.MODE_ECB)
                filename = file_arg[:-4] + 'zip'
                with open(filename, 'wb') as (wf):
                    fr.seek(4176)
                    print('Decrypting...')
                    while True:
                        data = fr.read(16)
                        if len(data) == 0:
                            break
                        wf.write(ctx.decrypt(data))
                        data = fr.read(16384)
                        if len(data) == 0:
                            break
                        wf.write(data)

                print('DONE!!')
                self.msg_log('转换完成!!')
            else:
                testkey = True
                filename = os.path.abspath(file_arg)
                path = os.path.abspath(os.path.dirname(filename))
                outpath = os.path.join(path, 'tmp')
                if os.path.exists(outpath):
                    shutil.rmtree(outpath)
                os.mkdir(outpath)
                with zipfile.ZipFile(filename, 'r') as (zo):
                    clist = []
                    try:
                        if zo.extract('oppo_metadata', outpath):
                            with open(os.path.join(outpath, 'oppo_metadata')) as (rt):
                                for line in rt:
                                    clist.append(line[:-1])

                    except:
                        print('Detected mode 2....')
                        return mode2(filename)
                        if testkey:
                            fname = ''
                            if 'firmware-update/vbmeta.img' in clist:
                                fname = 'firmware-update/vbmeta.img'
                            else:
                                if 'vbmeta.img' in clist:
                                    fname = 'vbmeta.img'
                                if fname != '':
                                    if zo.extract(fname, outpath):
                                        with open(os.path.join(outpath, fname.replace('/', os.sep)), 'rb') as (rt):
                                            rt.seek(4176)
                                            data = rt.read(16)
                                            key = keytest(data)
                                            if key == -1:
                                                print('Unknown AES key, reverse key from recovery first!')
                                                self.msg_log('Unknown AES key, reverse key from recovery first!')
                                                return 1
                                        testkey = False
                            if testkey == True:
                                print('Unknown image, please report an issue with image name!')
                                self.msg_log('Unknown image, please report an issue with image name!')
                                return 1
                        outzip = filename[:-4] + 'zip'
                        with zipfile.ZipFile(outzip, 'w', zipfile.ZIP_DEFLATED) as (WzipObj):
                            for info in zo.infolist():
                                print('Extracting ' + info.filename)
                                orgfilename = info.filename
                                info.filename = 'out'
                                zo.extract(info, outpath)
                                info.filename = orgfilename
                                if len(clist) > 0:
                                    if info.filename in clist:
                                        decryptfile(key, os.path.join(outpath, 'out'))
                                        WzipObj.write(os.path.join(outpath, 'out'), orgfilename)
                                    else:
                                        with open(os.path.join(outpath, 'out'), 'rb') as (rr):
                                            magic = rr.read(12)
                                        if magic == b'OPPOENCRYPT!':
                                            decryptfile(key, os.path.join(outpath, 'out'))
                                            WzipObj.write(os.path.join(outpath, 'out'), orgfilename)

                        print('DONE... files decrypted to: ' + outzip)
                        self.msg_log('DONE... files decrypted to: ' + outzip)
                        return 0

    def fastboot_device(self):
        p = subprocess.Popen(('"%s" "devices"' % fastboot), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        devlist = []
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)
            devlist = [line.strip()] + devlist

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

        if len(devlist) == 1:
            return True
        return False

    def fastboot_flash_recovery(self, image, isenc):
        if isenc is True:
            rec_image = self.decrypt_oralce(image)
            p = subprocess.Popen(('"%s" "flash" "recovery" "%s"' % (fastboot, rec_image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            if os.path.exists(rec_image):
                os.remove(rec_image)
        else:
            p = subprocess.Popen(('"%s" "flash" "recovery" "%s"' % (fastboot, image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

    def fastboot_flash_boot(self, image, isenc):
        if isenc is True:
            boot_image = self.decrypt_oralce(image)
            p = subprocess.Popen(('"%s" "flash" "boot" "%s"' % (fastboot, boot_image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            if os.path.exists(boot_image):
                os.remove(boot_image)
        else:
            p = subprocess.Popen(('"%s" "flash" "boot" "%s"' % (fastboot, image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

    def get_file_name(self, file_dir):
        L = []
        for root, dirs, files in os.walk(file_dir):
            for file in files:
                if os.path.splitext(file)[1] == '.img':
                    L.append(os.path.join(root, file))

        return L

    def rom2image(self, rom, stem):
        outdir = stem + '/images'
        flashallscript = stem + '/残芯专用_flash_all.bat'
        extrac_file = []
        p = subprocess.Popen(('"%s"  "%s"' % (payload_extractor, rom)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
          stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            image_file = str(msg.split()[2].strip())
            check_tmp = str(msg.split()[3].strip())
            if check_tmp == 'extracted':
                if image_file.endswith('.img'):
                    extrac_file = extrac_file + [image_file]
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            image_file = str(msg.split()[2].strip())
            check_tmp = str(msg.split()[3].strip())
            if check_tmp == 'extracted':
                if image_file.endswith('.img'):
                    extrac_file = extrac_file + [image_file]
            self.msg_log(msg)

        print(extrac_file)
        if os.path.exists(stem):
            print(stem + 'Exist!')
            shutil.rmtree(stem)
            os.makedirs(outdir)
        else:
            os.makedirs(outdir)
        for a in extrac_file:
            if not os.path.isfile(a):
                print('%s not exist!' % a)
            else:
                shutil.move(a, outdir)

        if os.path.isfile(flashallscript):
            shutil.rmtree(flashallscript)
        fo = open((f"{flashallscript}"), 'w')
        dt = datetime.now()
        chuo = dt.strftime('%Y.%m.%d %H:%M')
        fo.write('@echo off\n')
        title_str = 'title 残芯工具生成专用线刷脚本-' + chuo
        fo.write(f"{title_str}\n")
        fo.write('echo.\n')
        title_str2 = 'echo 欢迎使用残芯工具生成专用线刷脚本-' + chuo
        fo.write(f"{title_str2}\n")
        fo.write('echo 残芯精品资源QQ群：581220265\n')
        fo.write('echo.\n')
        fo.write('echo 请将手机进入到Fastboot模式\n')
        check_bootloader = 'fastboot %* getvar is-userspace 2>&1 | findstr /r /c:"^is-userspace: *no" || fastboot reboot bootloader'
        fo.write(f"{check_bootloader}\n")
        dynamic_p = [
         'system.img', 'vendor.img', 'odm.img', 'product.img', 'system_ext.img']
        x = np.array(extrac_file)
        y = np.array(dynamic_p)
        dynamic_real = np.intersect1d(x, y)
        partition_real = np.setdiff1d(x, y)
        print(dynamic_real)
        print(partition_real)
        for item in partition_real:
            stem2, suffix2 = os.path.splitext(item)
            partition = stem2 + '_ab'
            flashline = 'fastboot %* flash ' + partition + ' %~dp0images/' + item
            fo.write(f"{flashline}\n")

        flash_super = 'fastboot %* flash super %~dp0super.img'
        fo.write(f"{flash_super}\n")
        check_fastboot = 'fastboot %* getvar is-userspace 2>&1 | findstr /r /c:"^is-userspace: *yes" || fastboot reboot fastboot'
        fo.write(f"{check_fastboot}\n")
        for dtemp in dynamic_real:
            stem1, suffix1 = os.path.splitext(dtemp)
            partition1 = stem1 + '_a'
            partition2 = stem1 + '_b'
            eraseline1 = 'fastboot %* delete-logical-partition ' + partition1
            fo.write(f"{eraseline1}\n")
            print(eraseline1)
            eraseline2 = 'fastboot %* delete-logical-partition ' + partition2
            fo.write(f"{eraseline2}\n")

        for dtemp2 in dynamic_real:
            stem0, suffix0 = os.path.splitext(dtemp2)
            partitiona = stem0 + '_a'
            partitionb = stem0 + '_b'
            file_tmp = outdir + '/' + dtemp2
            partitiona_size = os.path.getsize(file_tmp)
            print(partitiona_size)
            creatline1 = 'fastboot %* create-logical-partition ' + partitiona + ' ' + str(partitiona_size)
            fo.write(f"{creatline1}\n")
            print(creatline1)
            creatline2 = 'fastboot %* create-logical-partition ' + partitionb + ' 0'
            fo.write(f"{creatline2}\n")

        for item in dynamic_real:
            stem2, suffix2 = os.path.splitext(item)
            partition = stem2 + '_a'
            flashline = 'fastboot %* flash ' + partition + ' %~dp0images/' + item
            fo.write(f"{flashline}\n")

        fo.write('fastboot %* set_active a \n')
        fo.write('fastboot %* reboot \n')
        fo.write('echo 刷机完成!\n')
        fo.write('echo.\n')
        fo.write('echo 残芯精品资源QQ群：581220265\n')
        fo.write('echo 发现问题请反馈给群主\n')
        fo.write(':Finish\n')
        fo.write('goto Finish\n')
        fo.close()
        tar_fastboot = stem + '/fastboot.exe'
        tar_AdbWinApi = stem + '/AdbWinApi.dll'
        tar_AdbWinUsbApi = stem + '/AdbWinUsbApi.dll'
        tar_adb = stem + '/adb.exe'
        tar_super = stem + '/super.img'
        shutil.copyfile(fastboot, tar_fastboot)
        shutil.copyfile(AdbWinApi, tar_AdbWinApi)
        shutil.copyfile(AdbWinUsbApi, tar_AdbWinUsbApi)
        shutil.copyfile(adb, tar_adb)
        shutil.copyfile(superfile, tar_super)
        self.msg_log('转换完成，生成的线刷包文件夹地址：' + stem)

    def fastboot_flash_rom(self, rom):
        outdir, suffix = os.path.splitext(rom)
        self.rom2image(rom, outdir)

    def fastboot_boot_image(self, image, isenc):
        if isenc is True:
            file_image = self.decrypt_oralce(image)
            print(image)
            print(file_image)
            p = subprocess.Popen(('"%s" "boot" "%s"' % (fastboot, file_image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            if os.path.exists(file_image):
                os.remove(file_image)
        else:
            p = subprocess.Popen(('"%s" "boot" "%s"' % (fastboot, image)), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

    def msg_log(self, log):
        self.logcat.append(log)

    def msg_log_error(self, log):
        self.logcat.append("<font color='red'>" + log + '<font>')

    def msg_fastboot_reboot_fastbootd(self):
        if self.fastboot_device():
            self.msg_log('检测到fastboot设备，重启到Fastbootd...')
            print('检测到fastboot设备，重启到Fastbootd...')
            p = subprocess.Popen(('"%s" "reboot" "fastboot"' % fastboot), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

        else:
            self.msg_log_error('未检测到fastboot设备')
            print('未检测到fastboot设备')

    def msg_fastboot_reboot(self):
        if self.fastboot_device():
            self.msg_log('检测到fastboot设备，重启到系统...')
            print('检测到fastboot设备，重启到系统...')
            p = subprocess.Popen(('"%s" "reboot"' % fastboot), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

        else:
            self.msg_log_error('未检测到fastboot设备')
            print('未检测到fastboot设备')

    def msg_reboot1(self):
        if self.fastboot_device():
            self.msg_log('检测到fastboot设备，按方法一重启到recovery...')
            print('检测到fastboot设备，按方法一重启到recovery...')
            p = subprocess.Popen(('"%s" "reboot-recovery"' % fastboot), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL),
              stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

        else:
            self.msg_log_error('未检测到fastboot设备')
            print('未检测到fastboot设备')

    def msg_reboot2(self):
        if self.fastboot_device():
            self.msg_log('检测到fastboot设备，按方法二重启到recovery...')
            print('检测到fastboot设备，按方法二重启到recovery...')
            subprocess.Popen(('"%s" "flash" "misc" "%s"' % (fastboot, recovery_misc)), stdout=(subprocess.PIPE), stderr=(subprocess.PIPE),
              stdin=(subprocess.DEVNULL),
              shell=True,
              bufsize=1)
            p = subprocess.Popen(('"%s" "reboot"' % fastboot), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
              shell=True,
              bufsize=1)
            for line in iter(p.stdout.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

            for line in iter(p.stderr.readline, b''):
                msg = line.strip().decode('utf-8')
                self.msg_log(msg)

        else:
            self.msg_log_error('未检测到fastboot设备')
            print('未检测到fastboot设备')

    def msg_adb_reboot_fastbootd(self):
        print('重启到用户fastbootd')
        p = subprocess.Popen(('"%s" "devices"' % adb), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

        p = subprocess.Popen(('"%s" "reboot" "fastboot"' % adb), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

    def msg_adb_reboot_fastboot(self):
        print('重启到fastboot')
        p = subprocess.Popen(('"%s" "devices"' % adb), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

        p = subprocess.Popen(('"%s" "reboot" "bootloader"' % adb), stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

    def msg_adb_scrcpy(self):
        print('启动手机镜像投屏到电脑')
        self.msg_log('正在启动手机镜像投屏到电脑，若长时间未显示手机镜像请再次检查手机USB调试')
        p = subprocess.Popen(scrcpy, stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

        p = subprocess.Popen(scrcpy, stdout=(subprocess.PIPE), stdin=(subprocess.DEVNULL), stderr=(subprocess.PIPE),
          shell=True,
          bufsize=1)
        for line in iter(p.stdout.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log(msg)

        for line in iter(p.stderr.readline, b''):
            msg = line.strip().decode('utf-8')
            self.msg_log_error(msg)

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
        with NamedTemporaryFile('w+b', delete=False) as (f2):
            decrypt_file = f2.name
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
        dec_write = open(decrypt_file, 'wb')
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
        return decrypt_file

    def check_enc(self, file_check):
        i_read = open(file_check, 'rb')
        a = i_read.read(8)
        i_read.close()
        if a == bytes('ANDROID!', encoding='utf8'):
            isenc = False
        else:
            isenc = True
        return isenc

    def msg_flash_boot(self):
        choose_image = self.lineEdit.text()
        exists = os.path.isfile(choose_image)
        if exists:
            if os.path.getsize(choose_image) > 6303743:
                self.msg_log('正在刷入boot文件：' + choose_image)
                isenc = self.check_enc(choose_image)
                if self.fastboot_device():
                    print(choose_image)
                    self.fastboot_flash_boot(choose_image, isenc)
                else:
                    self.msg_log_error('未检测到fastboot设备,无法刷入boot文件')
                    print('未检测到fastboot设备，无法刷入boot文件')
            else:
                self.msg_log_error('文件非法，请先选择正确的boot文件')
                print('文件非法，请先选择正确的boot文件')
        else:
            self.msg_log_error('请先选择boot文件')
            print('请先选择boot文件')

    def msg_fastboot_boot(self):
        choose_image = self.lineEdit.text()
        exists = os.path.isfile(choose_image)
        if exists:
            if os.path.getsize(choose_image) > 6303743:
                self.msg_log('正在临时启动镜像文件：' + choose_image)
                isenc = self.check_enc(choose_image)
                if self.fastboot_device():
                    print(choose_image)
                    self.fastboot_boot_image(choose_image, isenc)
                else:
                    self.msg_log_error('未检测到fastboot设备,无法临时启动镜像文件')
                    print('未检测到fastboot设备，无法临时启动镜像文件')
            else:
                self.msg_log_error('文件非法，请先选择正确的镜像文件')
                print('文件非法，请先选择正确的镜像文件')
        else:
            self.msg_log_error('请先选择镜像文件')
            print('请先选择镜像文件')

    def msg_flash_image(self):
        choose_image = self.lineEdit.text()
        exists = os.path.isfile(choose_image)
        if exists:
            if os.path.getsize(choose_image) > 6303743:
                self.msg_log('正在刷入recovery文件：' + choose_image)
                isenc = self.check_enc(choose_image)
                if self.fastboot_device():
                    print(choose_image)
                    self.fastboot_flash_recovery(choose_image, isenc)
                else:
                    self.msg_log_error('未检测到fastboot设备,无法刷入twrp recovery文件')
                    print('未检测到fastboot设备，无法刷入twrp recovery文件')
            else:
                self.msg_log_error('文件非法，请先选择正确的twrp recovery文件')
                print('文件非法，请先选择正确的twrp recovery文件')
        else:
            self.msg_log_error('请先选择twrp recovery文件')
            print('请先选择twrp recovery文件')

    def msg_flash_rom(self):
        choose_rom = self.chose_zip.text()
        exists = os.path.isfile(choose_rom)
        if exists:
            if os.path.getsize(choose_rom) > 63037430:
                self.msg_log('正在转换ROM文件：' + choose_rom)
                self.fastboot_flash_rom(choose_rom)
            else:
                self.msg_log_error('文件非法，请先选择正确的ROM文件')
                print('文件非法，请先选择正确的ROM文件')
        else:
            self.msg_log_error('请先选择正确的ROM文件')
            print('请先选择正确的ROM文件')

    def msg_ozip2zip(self):
        choose_rom = self.chose_ozip.text()
        exists = os.path.isfile(choose_rom)
        if exists:
            if os.path.getsize(choose_rom) > 63037430:
                self.msg_log('正在转换ozip文件：' + choose_rom)
                self.ozip2zip(choose_rom)
            else:
                self.msg_log_error('文件非法，请先选择正确的ozip文件')
                print('文件非法，请先选择正确的ozip文件')
        else:
            self.msg_log_error('请先选择ozip文件')
            print('请先选择ozip文件')

    def msg_choose(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, '选取文件', './')
        print(fileName_choose)
        self.lineEdit.setText(fileName_choose)
        exists = os.path.isfile(fileName_choose)
        if exists:
            self.msg_log('选中文件：' + fileName_choose)
        else:
            print(f"Error: [{fileName_choose}] was not found")
            self.msg_log_error(fileName_choose + ' 不存在')

    def msg_choose_rom(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, '选取文件', './')
        print(fileName_choose)
        self.chose_zip.setText(fileName_choose)
        exists = os.path.isfile(fileName_choose)
        if exists:
            self.msg_log('选中ROM文件：' + fileName_choose)
            self.msg_log('点击开始制作线刷包后，会先解包ROM，解包过程较慢，请耐心等待，期间请勿强制关闭程序...')
        else:
            print(f"Error: [{fileName_choose}] was not found")
            self.msg_log_error(fileName_choose + ' 不存在')

    def msg_choose_ozip(self):
        fileName_choose, filetype = QFileDialog.getOpenFileName(self, '选取文件', './')
        print(fileName_choose)
        self.chose_ozip.setText(fileName_choose)
        exists = os.path.isfile(fileName_choose)
        if exists:
            self.msg_log('选中ozip文件：' + fileName_choose)
        else:
            print(f"Error: [{fileName_choose}] was not found")
            self.msg_log_error(fileName_choose + ' 不存在')


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    myshow = MyWindow()
    myshow.show()
    sys.exit(app.exec_())