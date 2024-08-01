# coding=utf-8
# !/usr/bin/python
import json
import sys

import requests

sys.path.append('..')
from base.spider import Spider
import base64,re
import urllib.parse

class Spider(Spider):  # 元类 默认的元类 type
    def regStr(self, reg, src, group=1):
        m = re.search(reg, src)
        src = ''
        if m:
            src = m.group(group)
        return src
    def getName(self):
        return "hjkk"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "韩剧": "1",
            "韩影": "2",
            "韩综": "3",
            "其他": "4",
            "推荐": "5",
            "泰剧": "6",
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        rsp = self.fetch("https://www.hanjukankan.com/")
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//ul[@class='myui-vodlist clearfix']/li[@class='col-lg-6 col-md-6 col-sm-4 col-xs-3']")
        videos = []
        for a in aList:
            name = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("title")
            pic = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("data-original")
            mark = ""
            if a.xpath(".//p"):
                mark = a.xpath(".//p")[0].text
            sid = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("href")
            sid = self.regStr("/movie/index(\\S+).html",sid)
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result = {
            'list': videos
        }
        return result

    def categoryContent(self, tid, pg, filter, extend):
        result = {}
        url = f'https://www.hanjukankan.com/frim/index{tid}-{pg}.html'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        a_tag = root.xpath('//ul[@class="myui-page text-center clearfix"]//a[text()="尾页"]')[0].get('href')
        last_page = self.regStr(f"/frim/index{tid}-(\\S+).html", a_tag)
        aList = root.xpath("//div[@class='myui-panel_bd']/ul[@class='myui-vodlist clearfix']/li[@class='col-lg-6  col-md-6 col-sm-4 col-xs-3']")
        videos = []
        for a in aList:
            name = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("title")
            pic = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("data-original")
            mark = a.xpath(".//p")[0].text
            sid = a.xpath(".//a[@class='myui-vodlist__thumb lazyload']")[0].get("href")
            sid = self.regStr("/movie/index(\\S+).html", sid)
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

    def detailContent(self, array):
        tid = array[0]
        url = f'https://www.hanjukankan.com/movie/index{tid}.html'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        pic = root.xpath("//a[@class='myui-vodlist__thumb img-md-220 img-xs-130 picture']/img[@class='lazyload']/@data-original")[0]
        title = root.xpath("//div[@class='myui-content__detail']/h1[@class='title text-fff']")[0].text
        detail = root.xpath("//div[@id='jq']/div[@class='myui-panel-box clearfix']/div[@class='tab-content myui-panel_bd']")[0].text
        # 获取线路
        vod_play_from = 'hk$$$'
        play_list = root.xpath('//ul[@class="myui-content__list sort-list clearfix"]')
        vod_play_url = []
        for i in play_list:
            name_list = i.xpath('./li/a/text()')
            url_list = i.xpath('./li/a/@href')
            vod_play_url.append(
                '#'.join([_name + '$' + _url for _name, _url in zip(name_list, url_list)])
            )
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": pic,
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": detail,
            'vod_play_from': vod_play_from,
            'vod_play_url': '$$$'.join(vod_play_url)
        }
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        url = f'https://www.hanjukankan.com/search.php?searchword={key}'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        vodList = root.xpath("//ul[@class='myui-vodlist__media clearfix']/li")
        videos = []
        for vod in vodList:
            name = vod.xpath('.//a[@class="myui-vodlist__thumb img-lg-150 img-xs-100 lazyload"]/@title')[0]
            pic = vod.xpath('.//a[@class="myui-vodlist__thumb img-lg-150 img-xs-100 lazyload"]/@data-original')[0]
            href = vod.xpath('.//a[@class="myui-vodlist__thumb img-lg-150 img-xs-100 lazyload"]/@href')[0]
            tid = self.regStr('/movie/index(\\S+).html',href)
            remark = vod.xpath(".//p[@class='hidden-xs']/text()")[0]
            videos.append({
                "vod_id": tid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })
        result = {
            'list': videos
        }
        return result
    config = {
        "player": {},
        "filter": {}
    }
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36"
    }
    def parseCBC(self, enc, key, iv):
        keyBytes = key.encode("utf-8")
        ivBytes = iv.encode("utf-8")
        cipher = AES.new(keyBytes, AES.MODE_CBC, ivBytes)
        msg = cipher.decrypt(enc)
        paddingLen = msg[len(msg) - 1]
        return msg[0:-paddingLen]

    def playerContent(self, flag, id, vipFlags):
        print("id",id)
        url = f'https://www.hanjukankan.com/{id}'
        response = requests.get(url, headers=self.header)
        res = re.sub("\\s", "", response.text)
        now = re.findall('varnow=unescape\\("(.*?)"\\);', res)[0]
        decoded_url = urllib.parse.unquote(now)

        return {"url": decoded_url, "header": self.header, "parse": 0, "jx": 0}

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