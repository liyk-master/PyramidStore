#coding=utf-8
#!/usr/bin/python
from importlib.machinery import SourceFileLoader
import argparse

def loadFromDisk(fileName):
    name = fileName.split('/')[-1].split('.')[0]
    sp = SourceFileLoader(name, fileName).load_module().Spider()
    return sp

def run(path,name):
# def run(path,name,extend):
    rPath = path
    if len(name) > 0:
        rPath = 'plugin/py_{0}.py'.format(name)
    sp = loadFromDisk(rPath)
    sp.init()
    # res = sp.homeContent(True)
    # res = sp.homeVideoContent()
    # res = sp.categoryContent(13,1,True,"")
    res = sp.detailContent(["muyiaau6fAfu"])
    # res = sp.detailContent([15203])
    # res = sp.detailContent(["/tianyi1/我的视频/电影/打黑"])
    # res = sp.playerContent("线路1","723061197894259651|12350116506468","")
    # res = sp.searchContent("风骚律师","",1)
    print(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='choose your crawler')
    parser.add_argument('--path', type=str, default='plugin/py_94mt.py')
    parser.add_argument('--name', type=str, default='94mt')
    # parser.add_argument('--extend', type=str,default='{"server": "http://192.168.1.148:5244", "username": "admin", "password": "jdmliyk1"}')
    args = parser.parse_args()
    # run(args.path,args.name,args.extend)
    run(args.path,args.name)