#!/bin/python3
import argparse
from core import GitHack

def main():
    parser = argparse.ArgumentParser(description="获取.git目录敏感信息")
    parser.add_argument("hosturl",help="git目录地址，如'http://127.0.0.1/.git/'")
    parser.add_argument("-r","--root",default='githack',help="本地保存的目录，默认当前目录下的gitback")
    parser.add_argument("-m","--mod",default='index',choices=['index', 'logs'],help="使用哪种方式来获取信息.index(默认)：通过index文件开始泄露信息；logs：通过logs/HEAD开始泄露信息")
    
    args = parser.parse_args()
    g = GitHack(args.hosturl,args.root)
    sucDic = {}
    if args.mod == 'index':
        sucDic = g.fromIndex()
    elif args.mod == 'logs':
        sucDic = g.fromLogs()
        
    g.saveFile(sucDic)

if __name__  == '__main__':
    main()
