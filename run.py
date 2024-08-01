#coding=utf-8
#!/usr/bin/python
from importlib.machinery import SourceFileLoader
import argparse

def loadFromDisk(fileName):
    name = fileName.split('/')[-1].split('.')[0]
    sp = SourceFileLoader(name, fileName).load_module().Spider()
    return sp

def run(path,name):
    rPath = path
    if len(name) > 0:
        rPath = 'plugin/py_{0}.py'.format(name)
    sp = loadFromDisk(rPath)
    # sp.init(extend)  # 传递 extend 参数
    # res = sp.homeContent(True)
    # res = sp.homeVideoContent()
    # res = sp.categoryContent(1,1,True,"")
    # res = sp.detailContent([1475])
    # res = sp.detailContent([1645])
    # res = sp.playerContent("光速云","/play/729-0-0.html","")
    res = sp.searchContent("甜蜜家园","",1)
    print(res)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='choose your crawler')
    parser.add_argument('--path', type=str, default='plugin/py_hjkk.py')
    parser.add_argument('--name', type=str, default='hjkk')
    # parser.add_argument('--extend', type=str,default='{"server": "http://192.168.1.148:2345", "username": "liyk", "password": "jdmliyk1"}')
    args = parser.parse_args()
    # run(args.path,args.name,args.extend)
    run(args.path,args.name)