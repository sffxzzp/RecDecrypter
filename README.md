RecDecrypter
======
Golang 写的残芯 Rec 解密工具，使解密后的 img 可以用 adb 直接刷入。

之前一直 Private，听说现在跑路了，就改成公开好了。

原理来源于对所谓「残芯专用工具」的逆向，具体见 `source` 目录下的文件。

其中 `unpacked.py` 是直接解包工具得到的文件，`dec.py` 是对此文件提取出的部分，在 Python 环境下可直接进行对 Rec 的解密。

本仓库是 `dec.py` 的 Golang 版本移植。
