# toodoWechat
# 实例化应用
```python
import ToodoWechat
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
```