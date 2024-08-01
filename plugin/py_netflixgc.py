# coding=utf-8
# !/usr/bin/python
import json
import sys

import requests

sys.path.append('..')
from base.spider import Spider
import base64,re
from datetime import datetime, timedelta

class Spider(Spider):  # 元类 默认的元类 type
    def regStr(self, reg, src, group=1):
        m = re.search(reg, src)
        src = ''
        if m:
            src = m.group(group)
        return src
    def getName(self):
        return "meiju996"

    def init(self, extend=""):
        print("============{0}============".format(extend))
        pass

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "韩剧": "2"
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
        pass
        exit()
        try:
            flixgc_token = self.getAccessToken()
        except:
            return {'msg': '获取access_token错误'}
        # flixgc_token = {"php_session": "guplsm69onu6op05opj5o4a07m", "token": "94244f482fb987e89d620c65afcab7112572c197360071f537168022d0ba8c2d"}
        if flixgc_token:
            flixgc_token = json.loads(flixgc_token)
        else:
            return {'msg': '获取access_token错误'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
            'Referer': "https://www.netflixgc.com/vodshow/2-----------.html",
            '_funcdn_token': flixgc_token["token"],
        }
        current_time = datetime.now()
        timestamp = current_time.timestamp()
        # params = {
        #     "type": 2,
        #     "area": "韩国",
        #     "page": 1,
        #     "time": timestamp,
        #     "key":
        # }
        rep = requests.post("https://www.netflixgc.com/index.php/api/vod",headers=headers)
        print(rep.json())
        exit()
        aList = root.xpath("/html/body/div[@class='container']/div[@class='row']/div[@class='stui-pannel stui-pannel-bg clearfix'][2]/div[@class='stui-pannel-box clearfix']/div[@class='stui-pannel_bd clearfix']/div[@class='col-lg-wide-75 col-xs-1 padding-0']/ul[@class='stui-vodlist clearfix']/li")
        videos = []
        for a in aList:
            name = a.xpath(".//a")[0].get("title")
            pic = a.xpath(".//a")[0].get("data-original")
            mark = a.xpath(".//p")[0].text
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("/j/(\\S+).html",sid)
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
        url = 'http://www.meiju669.com/m/{0}-{1}.html'.format(tid, pg)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        a_tag = root.xpath('//ul[@class="stui-page text-center cleafix"]//a[text()="尾页"]')[0].get('href')
        last_page = self.regStr("/m/(\\S+).html", a_tag)[2:]
        total_val = root.xpath("/html/body/div[@class='container']/div[@class='row'][2]/div[@class='col-lg-wide-75 col-xs-1 padding-0']/div[@class='stui-pannel stui-pannel-bg clearfix']/div[@class='stui-pannel-box']/div[@class='stui-pannel_hd']/div[@class='stui-pannel__head active bottom-line clearfix']/span[@class='more text-muted pull-right']")[0].text
        total = re.search(r'“([^”]+)”', total_val).group(1)
        aList = root.xpath("/html/body/div[@class='container']/div[@class='row'][2]/div[@class='col-lg-wide-75 col-xs-1 padding-0']/div[@class='stui-pannel stui-pannel-bg clearfix']/div[@class='stui-pannel-box']/div[@class='stui-pannel_bd']/ul/li")
        videos = []
        for a in aList:
            name = a.xpath(".//a")[0].get("title")
            pic = a.xpath(".//a")[0].get("data-original")
            mark = a.xpath(".//p")[0].text
            mark = mark.replace("&nbsp", " ")
            sid = a.xpath(".//a")[0].get("href")
            sid = self.regStr("/j/(\\S+).html", sid)
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
        result['total'] = total
        return result

    def detailContent(self, array):
        tid = array[0]
        url = 'http://www.meiju669.com/j/{0}.html'.format(tid)
        rsp = self.fetch(url)
        root = self.html(self.cleanText(rsp.text))
        # node = root.xpath("//div[@class='dyxingq']")[0]
        pic = root.xpath("//a[@class='stui-vodlist__thumb picture v-thumb']/img[@class='lazyload']/@data-original")[0]
        title = root.xpath("//div[@class='stui-content__detail']/h1[@class='title']")[0].text
        detail = root.xpath("//div[@class='stui-pannel_bd']/div[@class='col-pd']")[0].text
        # 获取线路
        vod_play_from = '$$$'.join(root.xpath("//h3[@class='title']/font/text()"))
        play_list = root.xpath('//ul[@class="stui-content__playlist column8 clearfix"]')
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
        url = 'http://192.168.1.16:5000/search'
        headers = {'Content-Type': 'application/json'}
        rsp = requests.post(url,json={"val": key},headers=headers)
        root = self.html(self.cleanText(rsp.text))
        vodList = root.xpath("//div[@class='row-right']/")
        print(vodList)
        exit()
        videos = []
        for vod in vodList:
            name = vod.xpath('.//a[@class="v-thumb stui-vodlist__thumb lazyload"]/@title')[0]
            pic = vod.xpath('.//a[@class="v-thumb stui-vodlist__thumb lazyload"]/@data-original')[0]
            href = vod.xpath('.//a[@class="v-thumb stui-vodlist__thumb lazyload"]/@href')[0]
            tid = self.regStr('j/(\\S+).html',href)
            res = vod.xpath(".//div[@class='detail']//p/text()")
            res = [item.strip() for item in res if item.strip()]
            remark = ' '.join(res)
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
        video_flag = {"光速云": 1,"红牛云": 2,"无尽云": 3}
        url = 'http://www.meiju669.com{0}'.format(id)
        response = requests.get(url, headers=self.header)
        res = re.sub("\\s", "", response.text)
        now = re.findall('varnow="(.*?)";', res)[0]

        return {"url": now, "header": self.header, "parse": 0, "jx": 0}

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

    def getAccessToken(self):
        # flixgcInfos = self.getCache("flixgc_token")
        # if flixgcInfos:
        #     return flixgcInfos
        res = requests.post("http://192.168.1.16:5000/verify-captcha")
        res = res.json()
        if res["token"] != "":
            result = json.dumps(res["token"])
            # current_time = datetime.now()
            # future_time = current_time + timedelta(minutes=1)
            # timestamp = future_time.timestamp()
            # self.setCache("flixgc_token",{0: result,"expiresAt": timestamp})
            return result
        else:
            return ""