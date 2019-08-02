# weibo-comment-crawler

## 功能：
- 爬取单条微博的评论内容
- 把爬取的内容保存到csv文件中
- 对评论内容进行词频分析并画出词云图
- 分析评论的文本情感，统计积极评论与消极评论的数量

## 运行环境
- Python3
- Windows/Linux/MacOS

## 程序依赖
- jieba==0.39
- matplotlib==3.1.1
- pandas==0.25.0
- wordcloud==1.5.0

也可直接通过以下命令行安装依赖
```bash
pip install -r requirements.txt
```
## 使用方法
### 获取cookie
使用Chrome打开<https://www.weibo.cn>, 登陆以后按F12键进入开发者模式，如下图方式找到cookie，把后面的内容复制到cookie.txt文件夹中。
### 获取微博id
使用Chrome打开<https://m.weibo.cn>, 点开自己想要分析的微博，此时url中<https://m.weibo.cn/detail/>后面的数字就是我们需要的id
### 运行程序
```bash
python weibo_comment_crawler.py -n [评论数量] -id [微博id]
```
评论数量即是你需要爬取的数量，微博id在第二步中已获得。
