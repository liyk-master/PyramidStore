# coding=utf-8
# !/usr/bin/python
import json
import sys
import time

import requests
from bs4 import BeautifulSoup

sys.path.append('..')
from base.spider import Spider
import base64,re
from urllib.parse import urlencode

class Spider(Spider):  # 元类 默认的元类 type
    def regStr(self, reg, src, group=1):
        m = re.search(reg, src)
        src = ''
        if m:
            src = m.group(group)
        return src
    
    def getName(self):
        return "tianyi"

    def init(self, extend=""):
        self.get189Url = "http://112.116.126.25:7007"
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        pass

    def homeVideoContent(self):
        at_content = []
        # rsp = self.fetch("https://t.me/s/tianyirigeng")
        rsp = self.fetch("https://bh9527.pages.dev/")
        if rsp.status_code == 200:
            soup = BeautifulSoup(rsp.text, 'html.parser')
            # 尝试查找消息容器，根据实际网页调整class
            message_containers = soup.find_all('div', class_='text-box content')
            for container in message_containers:
                aList = {}   # 为每条消息创建一个新的字典

                # 1. 提取图片
                img_tag = container.find('img')
                if img_tag:
                    # style = img_tag.get('style')
                    # aList['vod_pic'] = re.search(r'url\((.*?)\)', style).group(1)
                    aList['vod_pic'] = img_tag.get('src').replace('/static/', '')
                # 获取标题（通常在b标签内）
                b_tag = container.find('b')
                if b_tag:
                    title = b_tag.text
                    clean_title = re.sub(r'\s+', '', title)  # 去除空格等
                    clean_title = re.split(r'[（(]', clean_title)[0].strip()
                    aList['vod_name'] = clean_title
                else:
                    continue

                # 获取所有的a标签，并筛选云盘链接
                links = []
                for a in container.find_all('a'):
                    href = a.get('href')
                    if href and 'cloud.189.cn' in href:
                        links.append(href)

                if links:
                    # 取第一个链接
                    cleaned_link = links[0].replace('https://cloud.189.cn/t/', '')
                    aList['vod_id'] = cleaned_link

                # 其他字段
                aList['vod_remarks'] = ""
                at_content.append(aList)
        result = {
            'list': at_content
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = 'https://www.94mt.cc/index.php/vod/type/id/{0}.html'.format(tid)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        a_tag = root.xpath('//ul[@class="pagination"]//a[text()="尾页"]')[0].get('href')
        # a_tag = "/index.php/vod/type/id/1/page/121.html"
        last_page = self.regStr("/index.php/vod/type/id/1/page/(\\S+).html", a_tag)
        # total_val = root.xpath("/html/body/div[@class='container']/div[@class='row'][2]/div[@class='col-lg-wide-75 col-xs-1 padding-0']/div[@class='stui-pannel stui-pannel-bg clearfix']/div[@class='stui-pannel-box']/div[@class='stui-pannel_hd']/div[@class='stui-pannel__head active bottom-line clearfix']/span[@class='more text-muted pull-right']")[0].text
        # total = re.search(r'“([^”]+)”', total_val).group(1)
        aList = root.xpath("//section[@class='main-container']/div[@class='row-five']//div[@class='box-item']")
        videos = []
        for a in aList:
            name = a.xpath(".//a")[0].get("title")
            pic = a.xpath(".//a/img")[0].get("src")
            mark = a.xpath(".//span")[0].text
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("/index.php/vod/play/id/(\\S+)/sid/1/nid/1.html", sid)
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = last_page
        result['limit'] = 30
        result['total'] = 99999
        return result

    # 定义一个键函数来提取集数
    def get_episode_number(self,item_string):
        # 尝试匹配 "S01EXX" 或 "第 XX 集" 形式的数字
        # 这个正则表达式会捕获第一个或第二个数字组
        match = re.search(r'S01E(\d+)|第 (\d+) 集', item_string)
        if match:
            # 如果 S01E 匹配到了，用第一个捕获组，否则用第二个 (第 XX 集)
            return int(match.group(1) or match.group(2))
        return 0 # 如果没找到集数，返回0或其他默认值，确保程序不会崩溃

    def detailContent(self, array):
        tid = array[0]
        url = '{1}/getShareInfo?code={0}'.format(tid, self.get189Url)
        rsp = self.fetch(url).json()
        # 检查响应是否包含所需字段
        if not rsp or 'res_code' not in rsp or 'creator' not in rsp:
            print("数据异常：响应结构不正确")
            return []
        # 正确的访问方式：使用字典键而不是属性
        if int(rsp.get('res_code', -1)) != 0 or rsp.get('creator') is None:
            print("数据异常：res_code不是0或creator为None")
            return []
        # 获取所需的值
        fileName = rsp.get('fileName', '')
        shareId = rsp.get('shareId', '')
        shareMode = rsp.get('shareMode', '')
        accessCode = rsp.get('accessCode', '')
        fileId = rsp.get('fileId','')
        vod_play_from = ''
        vod_play_url_str = ''
        # 如果文件夹则进一步获取文件列表
        if rsp.get('isFolder') is True:
            file_list_url = '{0}/getFileList'.format(self.get189Url)
            file_list_params = {
                "shareId": shareId,
                "shareMode": shareMode,
                "accessCode": accessCode,
                "fileId": fileId
            }
            
            file_list_response = self.fetch(file_list_url, params=file_list_params)
            resp = file_list_response.json()
            if (resp['res_code'] == 0):
                if len(resp['fileListAO']['fileList']) > 0:
                    vod_play_url = []
                    for file in resp['fileListAO']['fileList']:
                        # 过滤出非视频的类型
                        if not file['name'].endswith(('.mp4', '.mkv', '.avi', '.rmvb', '.flv', '.mov', '.wmv', '.mpg', '.mpeg', '.3gp', '.ts', '.m3u8', '.iso')):
                            continue
                        vod_play_from = '默认线路$$$'
                        vod_play_url.append(
                            file['name'] + '$' + file['id'] + "|"+ str(shareId)
                        )
                    # 使用 sorted() 函数和 key 参数进行排序
                    vod_play_url = sorted(vod_play_url, key=self.get_episode_number)
                    vod_play_url_str += '#'.join(vod_play_url) + "$$$"
                if len(resp['fileListAO']['folderList']) > 0:
                    for folder in resp['fileListAO']['folderList']:
                        vod_play_from += "{0}$$$".format(folder['name'])
                        folder_file_list_url = '{0}/getFileList'.format(self.get189Url)
                        folder_file_list_params = {
                            "shareId": shareId,
                            "shareMode": shareMode,
                            "accessCode": accessCode,
                            "fileId": folder['id']
                        }
                        folder_file_list_response = self.fetch(folder_file_list_url, params=folder_file_list_params)
                        folder_file_list_rsp = folder_file_list_response.json()
                        if (folder_file_list_rsp['res_code'] == 0):
                            vod_play_url = []
                            for file in folder_file_list_rsp['fileListAO']['fileList']:
                                # 过滤出非视频的类型
                                if not file['name'].endswith(('.mp4', '.mkv', '.avi', '.rmvb', '.flv', '.mov', '.wmv', '.mpg', '.mpeg', '.3gp', '.ts', '.m3u8', '.iso')):
                                    continue
                                vod_play_url.append(
                                    file['name'] + '$' + file['id'] + "|"+ str(shareId)
                                )
                            # 使用 sorted() 函数和 key 参数进行排序
                            vod_play_url = sorted(vod_play_url, key=self.get_episode_number)
                        vod_play_url_str += '#'.join(vod_play_url) + "$$$"
        else:
            vod_play_from = '默认线路'
            vod_play_url.append(
                '#'.join([file['name'] + '$' + file['id'] + "|"+ str(shareId)])
            )
        vod_play_from = vod_play_from.strip('$$$')
        vod_play_url_str = vod_play_url_str.strip('$$$')
        vod = {
            "vod_id": shareId,
            "vod_name": fileName,
            "vod_pic": "",
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            'vod_play_from': vod_play_from,
            'vod_play_url': vod_play_url_str
        }
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick, page):
        at_content = []
        url = 'https://bh9527.pages.dev/search/result?q={0}'.format(key)
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        rsp = self.fetch(url,headers=headers)
        
        if rsp.status_code == 200:
            soup = BeautifulSoup(rsp.text, 'html.parser')
            # 尝试查找消息容器，根据实际网页调整class
            message_containers = soup.find_all('div', class_='text-box content')
            for container in message_containers:
                aList = {}   # 为每条消息创建一个新的字典

                # 1. 提取图片
                img_tag = container.find('img')
                if img_tag:
                    # style = img_tag.get('style')
                    # aList['vod_pic'] = re.search(r'url\((.*?)\)', style).group(1)
                    aList['vod_pic'] = img_tag.get('src').replace('/static/', '')
                # 获取标题（通常在b标签内）
                b_tag = container.find('b')
                if b_tag:
                    title = b_tag.text
                    clean_title = re.sub(r'\s+', '', title)  # 去除空格等
                    clean_title = re.split(r'[（(]', clean_title)[0].strip()
                    aList['vod_name'] = clean_title
                else:
                    continue

                # 获取所有的a标签，并筛选云盘链接
                links = []
                for a in container.find_all('a'):
                    href = a.get('href')
                    if href and 'cloud.189.cn' in href:
                        links.append(href)

                if links:
                    # 取第一个链接
                    cleaned_link = links[0].replace('https://cloud.189.cn/t/', '')
                    aList['vod_id'] = cleaned_link

                # 其他字段
                aList['vod_remarks'] = ""
                at_content.append(aList)
        result = {
            'list': at_content
        }
        return result
    config = {
        "player": {},
        "filter": {}
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }

    def playerContent(self, flag, id, vipFlags):
        # id根据|分割
        fileId = id.split('|')[0]
        shareId = id.split('|')[1]
        url = "{2}/getDownloadUrl?fileId={0}&shareId={1}".format(fileId, shareId,self.get189Url)
        response = self.fetch(url)
        if response.status_code == 200:
            play_url = response.text
        else:
            play_url = ''

        return {"url": play_url, "header": self.header, "parse": 0, "jx": 0}

    def loadVtt(self, url):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def localProxy(self, param):
        action = {}
        return [200, "video/MP2T", action, ""]

    def destroy(self):
        pass

    def searchContentPage(self):
        pass