# encoding:UTF-8
import re, time, requests, random, argparse
import pandas as pd
from pandas import Series, DataFrame
import jieba
import jieba.analyse
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from text_emotion import get_sentiment_score, count_sentiment
import pymysql

plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus']=False

# 读取过滤词，用于生成词云
stopwords = set([line.strip() for line in open('./dictionary/Chinese_stop_words.txt', 'r').readlines()])
with open('cookie.txt', 'r') as f:
    cookie = {'Cookie': f.readline().strip()}  # 读取cookie，用于模拟登陆微博，cookie存储在cookie.txt文件
time_str = time.strftime("%Y%m%d%H%M%S", time.localtime())  # 生成时间字符串


class WeiboCommentCrawer(object):
    def __init__(self, max_num, weibo_id):
        self.weibo_id = weibo_id  # 单条微博的id
        self.cookie = cookie
        self.page_index = 0  # 评论的页码
        self.comment_list = []
        self.txt = ''
        self.txt_list = []
        self.score_list = []
        self.max_num = max_num  # 爬取评论数的上限
        self.r_data = {}
        self.stop_flag = False
        self.data_frame = DataFrame(columns=['id', 'text', 'user', 'time'])  # 存储评论内容(微博id，文本，用户名，时间)
        self.url = 'https://m.weibo.cn/api/comments/show?id=' + self.weibo_id + '&page={}'  # 评论地址（按时间）
        self.hot_url = 'https://m.weibo.cn/comments/hotflow?id=' + self.weibo_id + '&mid=' + self.weibo_id + \
                       '&max_id_type=0'  # 热门评论的网址(按热度排序)

    def crawl_comment(self):
        # 按时间顺序爬取评论内容，并存入csv文件
        while True:
            url = self.url.format(self.page_index)
            self.get_comment_from_url(url)

            if len(self.comment_list) >= self.max_num or len(self.comment_list) >= self.r_data['total_number'] or self.stop_flag:
                print(' -------------------')
                print('| Finished crawling |')
                print(' -------------------')
                break
            time.sleep(random.randint(3, 10))  # 随机等待3-10秒，模拟人的操作
            self.page_index += 1  # 用于更新url

        self.data_frame.to_csv('./weibo-comments-csv/{}-weibo.csv'.format(time_str))  # 存入csv

    def crawl_hot_comment(self):
        # 按热度爬取评论内容，并存入csv文件
        while True:
            url = self.hot_url
            self.get_comment_from_url(url)

            if len(self.comment_list) >= self.max_num or len(self.comment_list) >= self.r_data['total_number'] or self.stop_flag:
                print(' -------------------')
                print('| Finished crawling |')
                print(' -------------------')
                break
            if self.r_data['max_id'] != 0:
                # 更新url
                self.hot_url = 'https://m.weibo.cn/comments/hotflow?id=' + self.weibo_id + '&mid=' + self.weibo_id +'&max_id='+ str(self.r_data['max_id']) + '&max_id_type=0'
            time.sleep(random.randint(3, 10))

        self.data_frame.to_csv('./weibo-comments/{}-weibo.csv'.format(time_str))

    def get_comment_from_url(self, url):
        # 爬取单个url的评论内容
        try:
            r = requests.get(url=url, cookies=self.cookie)
            r_data = r.json()['data']
            self.r_data = r_data
            comment_page = r_data['data']
        except:
            print('Error in request')
            print('Return json:', r.json())
            print('Error url:', url)
            self.stop_flag = True
            return

        for j in range(len(comment_page)):
            comment = comment_page[j]
            comment_id = comment['id']

            if comment_id not in self.comment_list:
                self.comment_list.append(comment_id)
                user_name = comment['user']['screen_name']
                comment_time = comment['created_at']
                comment_text = re.sub('<.*?>|回复<.*?>:|[\U00010000-\U0010ffff]|[\uD800-\uDBFF][\uDC00-\uDFFF]',
                                      '',
                                      comment['text'])  # 滤除评论文本的emoji等内容

                self.txt = self.txt + comment_text + ' '  # 评论文本，用于打印词云和情绪分析
                score = get_sentiment_score(comment_text)
                self.score_list.append(score)

                series = Series([str(comment_id), user_name, comment_time, comment_text],
                                index=['id', 'user', 'time', 'text'])
                self.data_frame = self.data_frame.append(series, ignore_index=True)
                print('第 {} / {} 条评论 '.format(str(len(self.comment_list)).zfill(4), self.r_data['total_number']),
                      '|', str(score).center(5), '| ', comment_text, ' | ', user_name, ' | ',comment_time)

    def plot_word_cloud(self):
        # 打印词云
        text = []
        for word in jieba.cut(self.txt):
            if word in stopwords:
                continue
            if len(word) < 2:
                continue
            text.append(word)
        text = ''.join(text)
        self.tags = jieba.analyse.extract_tags(text,
                                               topK=100,
                                               withWeight=True)
        tf = dict((a[0], a[1]) for a in self.tags)
        wc = WordCloud(
            background_color='white',
            font_path='C:\Windows\Fonts\STZHONGS.TTF',
            max_words=2000,  # 设置最大现实的字数
            stopwords=STOPWORDS,  # 设置停用词
            max_font_size=200,  # 设置字体最大值
            random_state=30,
            width=1080,
            height=720)
        wc.generate_from_frequencies(tf)
        plt.figure(1)
        plt.imshow(wc)
        plt.axis('off')
        plt.show()

    def get_text_emotion(self):
        pos_num, neg_num = count_sentiment(self.score_list)
        print('\n 积极评论数：{} | 消极评论数：{} \n'.format(pos_num, neg_num))

    def visual_data(self, csv_path):
        # 读取csv文件的内容，并打印词云、分析词频(TF-IDF)
        frame = pd.read_csv(csv_path, index_col=0)
        txt_list = frame['text'].values
        self.txt = ' '.join(txt_list)
        plt.figure(1)
        self.plot_word_cloud()
        words = [i[0] for i in self.tags[0:10]]
        freq = [i[1] for i in self.tags[0:10]]

        plt.figure(2)
        plt.bar(words, freq)
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--comment_num', type=int, help='the number of comments you want',
                        default=100)
    parser.add_argument('-id', '--weibo_id', type=str, help='the weibo id to be crawled',
                        default='4400832105676005')
    args = parser.parse_args()

    comment_num = args.comment_num
    weibo_id = args.weibo_id
    weibo_crawler = WeiboCommentCrawer(comment_num, weibo_id)

    weibo_crawler.crawl_hot_comment()  # 抓取热门评论
    weibo_crawler.plot_word_cloud()    # 打印词云
    weibo_crawler.get_text_emotion()   # 分析评论情绪

    # csv_path = 'weibo-comments/20190801133207-weibo.csv'
    # weibo_crawler.visual_data(csv_path)

