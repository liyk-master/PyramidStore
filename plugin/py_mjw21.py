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
            "美剧": "all",
            "今日更新": "last-update",
            "排行榜": "alltop_hit",
            "热门电影": "category/dianying",
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
        rsp = self.fetch("https://mjw21.com/")
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//article[@class='u-movie']")
        videos = []
        for a in aList:
            name = a.xpath(".//a//h2/text()")[0]
            pic = a.xpath(".//a/div[@class='list-poster']/img")[0].get("data-original")
            pingfen = a.xpath(".//div[@class='pingfen']/span/text()")
            zhuangtai = a.xpath(".//div[@class='zhuangtai']/span/text()")
            meta = a.xpath(".//div[@class='meta']/span/text()")
            mark = (pingfen[0] if pingfen else '') + "/" + (zhuangtai[0] if zhuangtai else '') + "/" + (meta[0] if meta else '')
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("https://mjw21.com/w/(\\S+).html",sid)
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
        url = f'https://mjw21.com/{tid}/{pg}'
        if pg == 1 :
            url = f'https://mjw21.com/{tid}'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        a_tag = root.xpath('//div[@class="pagination pagination-multi"]//a[text()="尾页"]')
        a_tag = (a_tag[0].get('href') if a_tag else '')
        last_page = self.regStr(f"https://mjw21.com/all/page/(\\S+)", a_tag)
        aList = root.xpath("//article[@class='u-movie']")
        videos = []
        for a in aList:
            name = a.xpath(".//a//h2/text()")[0]
            pic = a.xpath(".//a/div[@class='list-poster']/img")[0].get("data-original")
            pingfen = a.xpath(".//div[@class='pingfen']/span/text()")
            zhuangtai = a.xpath(".//div[@class='zhuangtai']/span/text()")
            meta = a.xpath(".//div[@class='meta']/span/text()")
            mark = (pingfen[0] if pingfen else '') + "/" + (zhuangtai[0] if zhuangtai else '') + "/" + (
                meta[0] if meta else '')
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("https://mjw21.com/w/(\\S+).html", sid)
            videos.append({
                "vod_id": sid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": mark
            })
        result['list'] = videos
        result['page'] = pg
        result['pagecount'] = last_page
        result['limit'] = 42
        result['total'] = 99999
        return result

    def detailContent(self, array):
        tid = array[0]
        url = f'https://mjw21.com/w/{tid}.html'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        pic = root.xpath("//div[@class='video_img']/img")[0].get("src")
        title = root.xpath("//h1[@class='article-title']/a/text()")[0]
        detail = root.xpath("//p[@class='jianjie']/span/text()")[0]
        # 获取线路
        detail_url = root.xpath("//div[@class='vlink']/a")[0].get("id")
        response = self.fetch("https://mjw21.com/dp/" + detail_url + '.html')
        response_root = self.html(self.cleanText(response.text))
        nav_list = response_root.xpath("//nav[@id='playnav']//li/a/text()")
        vod_play_from = '$$$'.join(nav_list)
        play_list = response_root.xpath('//div[@id="playcontainer"]/section[@class="tab"]')
        vod_play_url = []
        for i in play_list:
            name_list = i.xpath('./a/text()')
            url_list = i.xpath('./a/@href')
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
        url = f'https://mjw21.com/?s={key}'
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        vodList = root.xpath("//article[@class='u-movie']")
        videos = []
        for vod in vodList:
            name = vod.xpath('.//h2/text()')[0]
            pic = vod.xpath('.//img[@class="thumb"]/@data-original')[0]
            href = vod.xpath('.//a/@href')[0]
            tid = self.regStr('https://mjw21.com/w/(\\S+).html',href)
            pingfen = vod.xpath(".//div[@class='pingfen']/span/text()")
            zhuangtai = vod.xpath(".//div[@class='zhuangtai']/span/text()")
            meta = vod.xpath(".//div[@class='meta']/span/text()")
            remark = (pingfen[0] if pingfen else '') + "/" + (zhuangtai[0] if zhuangtai else '') + "/" + (
                meta[0] if meta else '')
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
        url = f'https://mjw21.com{id}'
        response = requests.get(url, headers=self.header)
        res = re.sub("\\s", "", response.text)
        now = re.findall('varvid=("(.*?)");', res)[0]
        m3u8Url = now[0].replace('"', '')

        return {"url": m3u8Url, "header": self.header, "parse": 0, "jx": 0}

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