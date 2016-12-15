# Engineshooter
A Minimal Spider for Google Search Engine using Scrapy

## Usage
```
scrapy crawl engineshooter -a keyword=Github
```

## Search result
The MongoDB pipe is enable by default, all of search result will be store as the structure below:

```
{'title' : 'How people build software · GitHub', 'url' : 'https://github.com'}
```

Setting up your MongoDB configuration in settings.py:
```
MONGODB_HOST = ''
MONGODB_PORT = 23333
MONGODB_DB = ''
MONGODB_COLL = ''
```

## Proxy
Under the settings.py, define the HTTP_PROXY constant:
```
HTTP_PROXY = https://127.0.0.1:1080
```

## License
Publish under MIT
