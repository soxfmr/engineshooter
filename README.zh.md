# Engineshooter
基于 Scrapy 框架的 Google 搜索引擎爬虫

## 使用
```
scrapy crawl engineshooter -a keyword=Github
```
keyword 是目标关键词（-a 由 scrapy 解析，表示后面为参数）。

## 搜索结果
Engineshooter 会爬取每个搜索结果的链接和标题，并使用如下的结果进行存储：

```
{'title' : 'How people build software · GitHub', 'url' : 'https://github.com'}
```

默认情况下数据会保存到 MongoDB 数据库，数据库配置位于 settings.py 文件:
```
MONGODB_HOST = ''
MONGODB_PORT = 23333
MONGODB_DB = ''
MONGODB_COLL = ''
```

## 代理
在设置文件中可设置 HTTP/HTTPS 代理：
```
HTTP_PROXY = 'https://127.0.0.1:1080'
```

## 验证码
Google 本身有防爬虫机制，当遇到验证码时，控制台会发出蜂鸣并弹出验证码，需要手动输入。

## License
Publish under MIT
