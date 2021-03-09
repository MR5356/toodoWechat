# toodoWechat 微信公众号开发框架

# 视频教程
<iframe src="//player.bilibili.com/player.html?aid=629610233&bvid=BV1eb4y197aZ&cid=308144856&page=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true"> </iframe>

# 安装
克隆GitHub源码至本地或者[点击下载源码包](https://github.com/MR5356/toodoWechat/archive/main.zip)，然后拷贝ToodoWechat.py至你的项目路径
```bash
git clone https://github.com/MR5356/toodoWechat.git
```

# 使用
## 实例化应用
```python
import ToodoWechat

a = ToodoWechat('appID', 'appSecret')
```
## 上传图文中的图片，返回图片src地址，可直接在图文中使用
```python
picUrl = a.uploadNewsPicture('test.png')
```
## 上传图片素材
```python
media_id = a.uploadMedia('image', 'test.png').get('media_id')
```
## 上传视频素材
```python
media_id = a.uploadMedia('video', 'test.mp4', title="这个是视频的标题", introduction="测试视频").get('media_id')
```
## 上传图文，需传入图文列表，可以在articles里面放置多个图文数据(最多8个)，其中content字段为正文，支持HTML语法

```python
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
a.uploadNews(data)
```