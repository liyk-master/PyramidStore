# coding=utf-8
# !/usr/bin/python
import json
import sys
import time

import requests

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
        return "94mt"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "麻豆视频": "1",
            "hongkongdell": "13",
            "萝莉社": "10",
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
        rsp = self.fetch("https://www.94mt.cc/")
        root = self.html(self.cleanText(rsp.text))
        aList = root.xpath("//section[@class='main-container']/div[@class='row-six']//div[@class='box-item']")
        videos = []
        for a in aList:
            name = a.xpath(".//a")[0].get("title")
            pic = a.xpath(".//a/img")[0].get("src")
            mark = a.xpath(".//span")[0].text
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("/index.php/vod/play/id/(\\S+)/sid/1/nid/1.html",sid)
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

    def detailContent(self, array):
        tid = array[0]
        url = 'https://www.94mt.cc/index.php/vod/play/id/{0}/sid/1/nid/1.html'.format(tid)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        # node = root.xpath("//div[@class='dyxingq']")[0]
        title = root.xpath("//h1[@class='movie-title']/text()")[0]
        # 获取线路
        vod_play_from = '默认线路$$$'
        # play_list = root.xpath('//ul[@class="stui-content__playlist column8 clearfix"]')
        # vod_play_url = []
        # for i in play_list:
        #     name_list = i.xpath('./li/a/text()')
        #     url_list = i.xpath('./li/a/@href')
        #     vod_play_url.append(
        #         '#'.join([_name + '$' + _url for _name, _url in zip(name_list, url_list)])
        #     )
        vod = {
            "vod_id": tid,
            "vod_name": title,
            "vod_pic": "",
            "type_name": "",
            "vod_year": "",
            "vod_area": "",
            "vod_remarks": "",
            "vod_actor": "",
            "vod_director": "",
            "vod_content": "",
            'vod_play_from': vod_play_from,
            'vod_play_url': 'https://www.94mt.cc/index.php/vod/play/id/{0}/sid/1/nid/1.html$$$'.format(tid)
        }
        result = {
            'list': [
                vod
            ]
        }
        return result

    def searchContent(self, key, quick):
        url = 'https://www.94mt.cc/index.php/vod/search/page/1/wd/{0}.html'.format(key)
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': 'PHPSESSID=uq2251gkdf7oee20mpqhd91tt0',
            'priority': 'u=0, i',
            'referer': 'https://www.94mt.cc/index.php/vod/search/page/4/wd/%E7%8E%A9%E5%81%B6%E5%A7%90%E5%A7%90.html',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        rsp = self.post(url,data={"wd": key},headers=headers)
        root = self.html(self.cleanText(rsp.text))
        vodList = root.xpath("//div[@class='box-item']")
        # 获取尾页
        a_tag = root.xpath("//a[text()='尾页']")[0].get('href')
        last_page = self.regStr(r'/page/(\d+)/wd/', a_tag)
        videos = []
        for vod in vodList:
            name = vod.xpath('.//a[@class="movie-name"]/text()')[0]
            pic = vod.xpath('.//a[@class="item-link"]/img/@src')[0]
            href = vod.xpath('.//a[@class="movie-name"]/@href')[0]
            tid = self.regStr('/index.php/vod/detail/id/(\\S+).html',href)
            remark = vod.xpath(".//span")[0].text
            videos.append({
                "vod_id": tid,
                "vod_name": name,
                "vod_pic": pic,
                "vod_remarks": remark
            })

        # for i in range(2, last_page + 1):
        #     print("i:",i)
        #     url = f'https://www.94mt.cc/index.php/vod/search/page/{str(i)}/wd/{key}.html'
        #     rsp = self.post(url, data={"wd": key}, headers=headers)
        #     root = self.html(self.cleanText(rsp.text))
        #     vodList = root.xpath("//div[@class='box-item']")
        #
        #     for vod in vodList:
        #         name = vod.xpath('.//a[@class="movie-name"]/text()')[0]
        #         pic = vod.xpath('.//a[@class="item-link"]/img/@src')[0]
        #         href = vod.xpath('.//a[@class="movie-name"]/@href')[0]
        #         tid = self.regStr('/index.php/vod/detail/id/(\\S+).html', href)
        #         remark = vod.xpath(".//span")[0].text
        #         videos.append({
        #             "vod_id": tid,
        #             "vod_name": name,
        #             "vod_pic": pic,
        #             "vod_remarks": remark
        #         })
        #     time.sleep(2)
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
        url = id
        response = requests.get(url, headers=self.header)
        # 正则表达式
        regex = r'<script type="text\/javascript">var player_aaaa=(.*?)(?=<\/script>)'

        # 匹配
        match = re.search(regex, response.text, re.DOTALL)
        m3u8_url = ""
        if match:
            player_aaaa = json.loads(match.group(1))
            m3u8_url = player_aaaa['url']
        else:
            print("No match found")

        return {"url": m3u8_url, "header": self.header, "parse": 0, "jx": 0}

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