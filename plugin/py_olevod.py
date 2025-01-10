# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2024/7/19 22:20
# @Function:

import sys
import requests
import json
from lxml import etree
import time
import hashlib

sys.path.append('..')
from base.spider import Spider
from urllib.parse import quote
import math


class Spider(Spider):
    def getName(self):
        return "olevod"

    def init(self, extend):
        self.header = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'origin': 'https://www.olevod.com',
            'priority': 'u=1, i',
            'referer': 'https://www.olevod.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return {
            'class': [{'type_id': '/3/0/0/2/202/0/update/', 'type_name': '国产剧'},
                      {'type_id': '/3/0/0/2/201/0/update/', 'type_name': '英美剧'},
                      {'type_id': '/3/0/0/2/204/0/update/', 'type_name': '日韩剧'},
                      {'type_id': '/3/0/0/2/203/0/update/', 'type_name': '港台剧'},
                      {'type_id': '/3/0/0/1/101/0/update/', 'type_name': '电影'},
                      {'type_id': '/3/0/0/4/401/0/update/', 'type_name': '日漫'},
                      {'type_id': '/3/0/0/4/402/0/update/', 'type_name': '国漫'},
                      {'type_id': '/3/0/0/4/403/0/update/', 'type_name': '美漫'},
                      {'type_id': '/3/0/0/3/301/0/update/', 'type_name': '综艺'},
                      ]}

    def homeVideoContent(self):
        url = "https://api.olelive.com/v1/pub/vod/list/true/3/0/0/1/101/0/update/1/12?_vv="
        video_list = []
        try:
            t = self.getKey()
            res = requests.get(f"{url}{t}", headers=self.header).text
            data_list = json.loads(res)
            if data_list.get('code') != 0:
                print("请求失败~~~~")
                return {'list': video_list}
            if data_list.get('data').get('list'):
                for item in data_list.get('data').get('list'):
                    video_list.append({
                        "vod_id": item.get('id'),
                        "vod_name": item.get("name"),
                        "vod_pic": f"https://static.olelive.com/{item.get('pic')}",
                        "vod_remarks": item.get("score")
                    })

        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {'list': video_list}

    def categoryContent(self, tid, pg, filter, extend):
        print("tid-------------------------", tid)
        print("pg-------------------------", pg)
        print("extend-------------------------", extend)
        result = {}
        url = f"https://api.olelive.com/v1/pub/vod/list/true{tid}{pg}/12?_vv="
        try:
            video_list = []
            t = self.getKey()
            res = requests.get(f"{url}{t}", headers=self.header).text
            data_list = json.loads(res)
            if data_list.get('code') != 0:
                print("请求失败~~~~")
                return {'list': []}
            if data_list.get('data').get('list'):
                for item in data_list.get('data').get('list'):
                    video_list.append({
                        "vod_id": item.get('id'),
                        "vod_name": item.get("name"),
                        "vod_pic": f"https://static.olelive.com/{item.get('pic')}",
                        "vod_remarks": item.get("score")
                    })
                result["list"] = video_list
                result['page'] = pg
                result['pagecount'] = math.ceil(data_list.get("data").get("total") / 12)
                result['limit'] = 12
                result['total'] = data_list.get("data").get("total")
        except requests.RequestException as e:
            return {'list': [], 'msg': e}

        return result

    def detailContent(self, did):
        print("detailContent------------------------", did)
        video_list = []
        try:
            t = self.getKey()
            url = f"https://api.olelive.com/v1/pub/vod/detail/{did[0]}/true?_vv={t}"
            res = requests.get(url, headers=self.header).text
            data_list = json.loads(res)
            if data_list.get('code') != 0:
                print("请求失败~~~~")
                return {'list': []}
            play_list = []
            if data_list.get("data"):
                for item in data_list.get("data").get("urls"):
                    play_list.append(
                        f'{item.get("title")}${item.get("url")}')
                vod_play_from = "oleVod"
                vod_play_url = '#'.join(play_list)
                video_list.append(
                    {
                        'type_name': data_list.get("data").get('typeId1Name'),
                        'vod_id': data_list.get("data").get('id'),
                        'vod_name': data_list.get("data").get('name'),
                        'vod_remarks': data_list.get("data").get('remarks'),
                        'vod_year': data_list.get("data").get('year'),
                        'vod_area': data_list.get("data").get('area'),
                        'vod_actor': data_list.get("data").get('actor'),
                        'vod_director': data_list.get("data").get('director'),
                        'vod_content': data_list.get("data").get('content'),
                        'vod_play_from': vod_play_from,
                        'vod_play_url': vod_play_url
                    }
                )

        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {"list": video_list}

    def searchContent(self, keywords, quick, page):
        video_list = []
        try:
            t = self.getKey()
            url = f"https://api.olelive.com/v1/pub/index/search/{keywords}/vod/0/{page}/4?_vv={t}"
            res = requests.get(url, headers=self.header).text
            data_list = json.loads(res)
            if data_list.get('code') != 0:
                print("请求失败~~~~")
                return {'list': []}
            if data_list.get('data').get('data')[0].get('list'):
                for item in data_list.get('data').get('data')[0].get('list'):
                    video_list.append(
                        {
                            'vod_id': item.get('id'),
                            'vod_name': item.get('name'),
                            "vod_pic": f"https://static.olelive.com/{item.get('pic')}",
                            "vod_remarks": item.get("score")
                        }
                    )

        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {'list': video_list}

    def playerContent(self, flag, pid, vipFlags):
        print("flag------------", flag)
        print("pid-------------", pid)
        return {"url": pid, "parse": 0, "jx": 0}

    def ce(self, e):
        t = []
        for char in e:
            # 获取字符的ASCII码并转为二进制
            bin_value = bin(ord(char))[2:]  # bin(ord(char))会返回以'0b'开头，去掉'0b'部分
            t.append(bin_value)
        return ''.join(t)

    def fe(self, e):
        t = str(e)
        r = [[], [], [], []]

        for char in t:
            bin_val = self.ce(char)
            # 按照二进制位置切片并添加到不同的数组
            r[0].append(bin_val[2:3])
            r[1].append(bin_val[3:4])
            r[2].append(bin_val[4:5])
            r[3].append(bin_val[5:])

        # 将每个数组转换为二进制字符串
        result = []
        for i in range(4):
            # 连接数组并转换成二进制
            bin_str = ''.join(r[i])
            # 转换为十六进制，并保证格式
            hex_value = hex(int(bin_str, 2))[2:]  # 去掉'0x'前缀
            if len(hex_value) == 1:
                hex_value = '00' + hex_value
            elif len(hex_value) == 2:
                hex_value = '0' + hex_value
            result.append(hex_value)

        # 计算MD5值
        md5_hash = hashlib.md5(t.encode('utf-8')).hexdigest()

        # 按照要求组合MD5和其他字符
        final_result = md5_hash[:3] + result[0] + md5_hash[6:11] + result[1] + md5_hash[14:19] + result[2] + md5_hash[
                                                                                                             22:27] + \
                       result[3] + md5_hash[30:]

        return final_result

    def getKey(self):
        return self.fe(int(time.time()))

    def localProxy(self, params):
        pass

    header = {"User-Agent": "okhttp/3.12.0"}


if __name__ == '__main__':
    pass
