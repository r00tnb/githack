# githack
自己用python写的git目录泄漏利用工具，有错请大佬们指出。

很早之前自己写的，拿出来分享。

usage:python githack.py hosturl [rootdir] [fromlogs]
                    params：hosturl为包含git目录的url
                            rootdirgit目录会下载到该目录
                            fromlogs可以为任意值即可变为第二个模式。
                    本脚本有两个模式（默认1）：1.下载暂存区的文件。2.从logs中遍历所有对象