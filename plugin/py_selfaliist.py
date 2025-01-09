# -*- coding: utf-8 -*-
# @Author  : Doubebly
# @Time    : 2024/7/19 22:20
# @Function:

import sys
import requests
import json
from lxml import etree
import re

sys.path.append('..')
from base.spider import Spider
from urllib.parse import quote
import math


# import redis
#
# redis_cli = redis.Redis(host='localhost', port=6379, decode_responses=True)


class Spider(Spider):
    def getName(self):
        return "selfalist"

    def init(self, extend):
        try:
            extendDict = json.loads(extend)
            self.alistUrl = extendDict['server']
            self.baseUrl = extendDict['server'] + "/api/auth/login"
            self.fsUrl = extendDict['server'] + "/api/fs"
            self.username = extendDict['username']
            self.password = extendDict['password']
        except:
            self.baseUrl = ''
            self.username = ''
            self.password = ''

    def destroy(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        return {
            'class': [{'type_id': '/tianyi1/我的视频/电视剧/国产剧', 'type_name': '国产剧'},
                      {'type_id': '/tianyi1/我的视频/电视剧/美剧', 'type_name': '美剧'},
                      {'type_id': '/tianyi1/我的视频/电视剧/韩剧', 'type_name': '韩剧'},
                      {'type_id': '/tianyi1/我的视频/电影', 'type_name': '电影'}],
        }

    def homeVideoContent(self):
        video_list = []
        try:
            dir_path = "/tianyi1/我的视频/电影"
            token = self.getAccessToken()
            headers = {
                'Authorization': token
            }
            body = {
                "path": dir_path,
                "page": 1,
            }
            i = 0
            while True:
                if i >= 2:
                    print("alist token获取失败~")
                    break
                res = requests.post(self.fsUrl + "/list", headers=headers, json=body).text
                data_list = json.loads(res)
                if data_list.get('code') != 200:
                    i += 1
                    token = self.getAccessToken(True)
                    headers = {
                        'Authorization': token
                    }
                    continue
                if data_list.get("data").get("content"):
                    for item in data_list.get("data").get("content"):
                        # 判断是文件夹还是文件
                        # if item.get("is_dir"):
                        #     body = {
                        #         "path": f"{dir_path}/{item.get("name")}",
                        #         "page": 1,
                        #     }
                        #     item_res = requests.post(self.fsUrl + "/list", headers=headers, json=body).text
                        #     item_list = json.loads(item_res)
                        #     if item_list.get('code') != 200:
                        #         video_list.append({
                        #             "vod_id": "",
                        #             "vod_name": "",
                        #             "vod_pic": "",
                        #             "vod_remarks": ""
                        #         })
                        #         continue
                        #     if item_list.get("data").get("content"):
                        #         for v in item_list.get("data").get("content"):
                        #             video_list.append({
                        #                 "vod_id": f"{dir_path}/{item.get("name")}/{v.get("name")}",
                        #                 "vod_name": item.get("name"),
                        #                 "vod_pic": v.get("thumb"),
                        #                 "vod_remarks": item.get("name")
                        #             })

                        video_list.append({
                            "vod_id": dir_path + "/" + item.get("name"),
                            "vod_name": item.get("name"),
                            "vod_pic": item.get("thumb"),
                            "vod_remarks": item.get("name")
                        })
                break
        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {'list': video_list}

    def categoryContent(self, tid, pg, filter, extend):
        print("tid-------------------------",tid)
        print("pg-------------------------",pg)
        print("extend-------------------------",extend)
        result = {}
        try:
            token = self.getAccessToken()
            headers = {
                'Authorization': token
            }
            body = {
                "path": tid,
                "page": int(pg)
            }
            video_list = []
            res = requests.post(self.fsUrl + "/list", headers=headers, json=body).text
            data_list = json.loads(res)
            if data_list.get('code') != 200:
                print("接口获取失败~~~")
            if data_list.get("data").get("content"):
                for item in data_list.get("data").get("content"):
                    video_list.append({
                        "vod_id": tid + "/" + item.get("name"),
                        "vod_name": item.get("name"),
                        "vod_pic": item.get("thumb"),
                        "vod_remarks": item.get("name")
                    })
                result["list"] = video_list
                result['page'] = pg
                result['pagecount'] = math.ceil(data_list.get("data").get("total") / 9)
                result['limit'] = 9
                result['total'] = data_list.get("data").get("total")
        except requests.RequestException as e:
            return {'list': [], 'msg': e}

        return result

    def detailContent(self, did):
        print("detailContent------------------------", did)
        video_list = []
        token = self.getAccessToken()
        headers = {
            'Authorization': token
        }
        body = {
            "path": did[0],
            "page": 1,
        }
        try:
            res = requests.post(self.fsUrl + "/list", headers=headers, json=body).text
            data_list = json.loads(res)
            if data_list.get('code') != 200:
                print("获取detail失败")
                return
            vod_list = []
            play_list = []
            if data_list.get("data").get("content"):
                for item in data_list.get("data").get("content"):
                    vod_list.append(item.get("name"))
                    play_list.append(f'{item.get("name")}${self.alistUrl}/d{quote(did[0])}/{quote(item.get("name"))}?sign={item.get("sign")}')
            vod_play_from = '$$$'.join(vod_list)
            vod_play_url = '#'.join(play_list)
            video_list.append(
                {
                    'type_name': '',
                    'vod_id': did[0],
                    'vod_name': '',
                    'vod_remarks': '',
                    'vod_year': '',
                    'vod_area': '',
                    'vod_actor': '',
                    'vod_director': 'liyk',
                    'vod_content': '暂无简介',
                    'vod_play_from': vod_play_from,
                    'vod_play_url': vod_play_url
                }
            )
            print("打印日志--------------------------")
            print(video_list)

        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {"list": video_list}

    def searchContent(self, keywords, quick, page):
        video_list = []
        try:
            res = requests.get(f'https://dm84.org/s----------.html?wd={keywords}')
            root = etree.HTML(res.text)
            data_list = root.xpath('//li/div[@class="item"]')
            for i in data_list:
                video_list.append(
                    {
                        'vod_id': i.xpath('./a[2]/@href')[0].split('/')[-1].split('.')[0],
                        'vod_name': i.xpath('./a[2]/@title')[0],
                        'vod_pic': i.xpath('./a[1]/@data-bg')[0],
                        'vod_remarks': i.xpath('./span/text()')[0]
                    }
                )


        except requests.RequestException as e:
            return {'list': [], 'msg': e}
        return {'list': video_list}

    def playerContent(self, flag, pid, vipFlags):
        print("flag------------", flag)
        print("pid-------------", pid)
        return {"url": pid, "parse": 0, "jx": 0}

    def getAccessToken(self, refresh=False):
        key = f"alist_{self.baseUrl}_{self.username}_{self.password}"
        if refresh:
            print("删除缓存token~~~")
            self.delCache(key)
            # redis_cli.delete(key)
        token = self.getCache(key)
        # token = redis_cli.get(key)
        if token:
            return token
        d = {
            'Username': self.username,
            'Password': self.password
        }
        r = requests.post(self.baseUrl, data=d)
        data = json.loads(r.text)
        token = data.get('data').get('token')
        self.setCache(key, token)
        # redis_cli.set(key, token)
        return token

    def localProxy(self, params):
        pass

    header = {"User-Agent": "okhttp/3.12.0"}


if __name__ == '__main__':
    pass
