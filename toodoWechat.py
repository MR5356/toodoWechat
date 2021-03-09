#!/usr/bin/python3
import os
import json
import time
import requests
from hashlib import md5


class ToodoWechatException(Exception):
    pass


def checkError(reqJson):
    """
    检测返回的json消息中是否有错误信息，如果有抛出错误，否则返回json信息
    :param reqJson: 返回的json数据
    :return: 如果有抛出错误，否则返回json信息
    """
    if "errcode" in reqJson and reqJson['errcode'] != 0:
        raise ToodoWechatException(
            f"{reqJson} 详细错误信息对比文档：https://developers.weixin.qq.com/doc/oplatform/Return_codes/Return_code_descriptions_new.html")
    return reqJson


class ToodoWechat:
    def __init__(self, appID, appSecret):
        self.appID = appID
        self.appSecret = appSecret
        self.basePath = os.path.dirname(__file__)
        self._session = requests.Session()
        # 确保多个公众号的缓存不会混乱
        self.tokenCache = md5(f"{self.appID}{self.appSecret}".encode()).hexdigest() + '.json'

    def _requests(self, method, url, decode_level=2, retry=10, timeout=15, **kwargs):
        if method in ["get", "post"]:
            for _ in range(retry):
                try:
                    response = getattr(self._session, method)(url, timeout=timeout, **kwargs)
                    return response.json() if decode_level == 2 else response.content if decode_level == 1 else response
                except Exception as e:
                    print(e)
                    print(f"[{_ + 1} / {retry}]网络请求失败正在重新尝试：method: {method}; url: {url}")
        raise ToodoWechatException(f"网络请求失败，请检查您的网络连接")

    def getNewToken(self):
        """
        从服务器获取新的access_token
        文件缓存token格式：{"access_token":"ACCESS_TOKEN","expires_in":7200,"expires_at": int}
        :return: access_token
        """
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appID}&secret={self.appSecret}"
        res = checkError(self._requests('get', baseUrl))
        res['expires_at'] = int(time.time()) + res['expires_in']
        with open(os.path.join(self.basePath, self.tokenCache), 'w') as f:
            f.write(json.dumps(res))
        return res['access_token']

    def getToken(self):
        """
        检测token是否过期，未过期直接返回，如果过期则生成新的access_token并返回
        如果脚本长时间运行，每次使用token前进行token检测是必须的
        文件缓存token格式：{"access_token":"ACCESS_TOKEN","expires_in":7200,"expires_at": int}
        :return: access_token
        """
        # 首次打开，没有缓存文件的话则直接获取新的access_token
        try:
            with open(os.path.join(self.basePath, self.tokenCache), 'r') as f:
                tokenInfo = json.loads(f.read())
                # 距离过期时间超过60秒则可继续使用
                if tokenInfo['expires_at'] - int(time.time()) > 60:
                    return tokenInfo['access_token']
                return self.getNewToken()
        except:
            return self.getNewToken()

    def uploadNews(self, data):
        """
        上传图文消息
        :param data: 图文列表，格式见：https://developers.weixin.qq.com/doc/offiaccount/Asset_Management/Adding_Permanent_Assets.html
        :return: {"media_id":MEDIA_ID}
        """
        data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        token = self.getToken()
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/material/add_news?access_token={token}"
        res = checkError(self._requests('post', baseUrl, data=data))
        return res

    def uploadNewsPicture(self, mediaPath):
        """
        上传图文信息中的图片获取URL
        本接口所上传的图片不占用公众号的素材库中图片数量的100000个的限制。图片仅支持jpg/png格式，大小必须在1MB以下。
        :param mediaPath: 图片文件地址，建议使用绝对路径
        :return: 图文中可用的图片网址
        """
        token = self.getToken()
        # 如果超过1M则自动改用永久图片素材上传
        if os.path.getsize(mediaPath) >= 1024 * 1024:
            print(f"图片大小超过1M，将采用永久图片素材上传：mediaPath: {mediaPath}")
            return self.uploadMedia(mediaType='image', mediaPath=mediaPath)['url']
        mediaFile = open(mediaPath, 'rb')
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={token}"
        res = checkError(self._requests('post', baseUrl, files={"media": mediaFile}))
        return res['url']

    def uploadMedia(self, mediaType, mediaPath, **kwargs):
        """
        新增其他永久素材，包括图片(image)、语音(voice)、视频(video) 和略缩图
        小视频可以上传成功，但是文件大小比较大的视频不能上传
        :param mediaPath: 素材地址，建议使用绝对路径
        :param mediaType: 素材类型
        :return: {"media_id":MEDIA_ID,"url":URL}
        """
        token = self.getToken()
        baseUrl = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type={mediaType}"
        mediaFile = open(mediaPath, 'rb')
        if mediaType == 'video':
            title = kwargs.get('title')
            introduction = kwargs.get('introduction')
            if not title or not introduction:
                raise ToodoWechatException(
                    "上传视频需要额外提供title和introduction参数，如：uploadMedia('video', '1.mp4', title='标题', introduction='简介')")
            data = {"description": json.dumps({"title": title, "introduction": introduction})}
            res = checkError(self._requests('post', baseUrl, timeout=10000, data=data, files={"media": mediaFile}))
        else:
            res = checkError(self._requests('post', baseUrl, files={"media": mediaFile}))
        return res


if __name__ == '__main__':
    # 实例化应用
    a = ToodoWechat('appID', 'appSecret')
    # 上传图文中的图片，返回图片src地址，可直接在图文中使用
    picUrl = a.uploadNewsPicture('test.png')
    # 上传图片素材
    media_id1 = a.uploadMedia('image', 'test.png').get('media_id')
    # 上传视频素材
    media_id2 = a.uploadMedia('video', 'test.mp4', title="这个是视频的标题", introduction="测试视频").get('media_id')
    # 图文列表，可以在articles里面放置多个图文数据(最多8个)，其中content字段为正文，支持HTML语法
    data = {
        "articles": [{
            "title": f"图文标题",
            "thumb_media_id": "封面的media_id",
            "author": '图文作者',
            "digest": f"图文简介",
            "show_cover_pic": 1,
            "content": "图文正文(支持HTML语法)",
            "content_source_url": '阅读原文的链接地址',
            "need_open_comment": 1,
            "only_fans_can_comment": 1
        }
        ]
    }
    # 上传图文
    a.uploadNews(data)
