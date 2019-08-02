import jieba

path = './dictionary/'


def read_dict(filename):
    with open(path + filename, encoding='utf-8') as f:
        word=[w.strip() for w in f.readlines()]
    return word


def judge_odd(n):
    if (n % 2) == 0:
        return 'even'
    else:
        return 'odd'


# 读取各类词典为列表
deny_words = read_dict('deny_words.txt')
positive_words = read_dict('positive_words.txt')
negative_words = read_dict('negative_words.txt')
degree_words = read_dict('degree_words.txt')

# 区分不同的程度词，权重分别为：4,3,2,0.5
mostdict = degree_words[degree_words.index('extreme') + 1: degree_words.index('very')]
verydict = degree_words[degree_words.index('very') + 1: degree_words.index('more')]
moredict = degree_words[degree_words.index('more') + 1: degree_words.index('ish')]
ishdict = degree_words[degree_words.index('ish') + 1: degree_words.index('last')]


def get_sentiment_score(text):
    # 计算一句话的情绪分值，积极为正，消极为负
    sentence = jieba.lcut(text, cut_all=False)  # 把句子分词，变成列表
    emotion_index = 0  # 情感词位置索引
    pos_num = 0
    pos_score = 0
    neg_num = 0
    neg_score = 0

    for (word_index, word) in enumerate(sentence):
        if word in positive_words:  # 判断词语是否是积极情感词
            pos_num += 1
            deny_num = 0
            for w in sentence[emotion_index:word_index]:  # 扫描情感词前的程度词
                if w in mostdict:
                    pos_num *= 4.0
                elif w in verydict:
                    pos_num *= 3.0
                elif w in moredict:
                    pos_num *= 2.0
                elif w in ishdict:
                    pos_num *= 0.5
                elif w in deny_words:
                    deny_num += 1
            if judge_odd(deny_num) == 'odd':  # 扫描情感词前的否定词数
                neg_score += pos_num
            else:
                pos_score += pos_num
            pos_num = 0
            emotion_index = word_index + 1  # 记录情感词位置

        elif word in negative_words:  # 消极情感的分析，与上面一致
            neg_num += 1
            deny_num = 0
            for w in sentence[emotion_index:word_index]:
                if w in mostdict:
                    neg_num *= 4.0
                elif w in verydict:
                    neg_num *= 3.0
                elif w in moredict:
                    neg_num *= 2.0
                elif w in ishdict:
                    neg_num *= 0.5
                elif w in degree_words:
                    deny_num += 1
            if judge_odd(deny_num) == 'odd':
                pos_score += neg_num
            else:
                neg_score += neg_num
            neg_num = 0
            emotion_index = word_index + 1

    return pos_score-neg_score


def count_sentiment(score_list):
    pos_num = 0
    neg_num = 0
    for score in score_list:
        if score > 0:
            pos_num += 1
        elif score < 0:
            neg_num += 1

    return pos_num, neg_num


if __name__ == '__main__':
    text = '非常好用的'
    score = get_sentiment_score(text)
    print(score)



