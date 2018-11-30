'''
    Author: Ribbon Huang
    Date :2018 - 11 -19
    Desc:
        进行中文分词， 提取关键词， 并做成词云
'''

__author__ = 'Ribbon Huang'
from wordcloud import WordCloud
import jieba
import re
from jieba.analyse import *
from conf.settings import FONT_PATH
import numpy as np
from PIL import Image
def part(info, newsTitle):
    # 分词并且提取关键词
    # alice_mask = np.array(Image.open("utils/1.jpg"))
    pattern = re.compile(u'\t|\n|\.|-|—|:|;|\)|\(|\?|"|、|。|，')
    string_data = re.sub(pattern, '', info)
    string_data = re.sub('\d', '', string_data)
    seg_list_exact = jieba.cut(string_data, cut_all=False)
    object_list = []
    remove_words = []
    with open('utils\stopwords.txt', 'rb') as f:
        for line in f:
            line = line.decode('utf8')
            remove_words.append(line.strip())

    for word in seg_list_exact:
        if word not in remove_words and len(word) > 1 and not word.isdigit():
            object_list.append(word)
    words = ''.join(object_list)
    topWord = ' '.join(extract_tags(words, topK=20, withWeight=False))

    # 生成词云
    pngName = '词云/' + ''.join(extract_tags(words, topK=20, withWeight=False)) + '.png'
    wc = WordCloud(background_color='white',  # 设置背景颜色
                   max_words=200,  # 设置最大现实的字数
                   font_path=FONT_PATH,  # 设置字体格式，如不设置显示不了中文
                   max_font_size=60,  # 设置字体最大值
                   color_func=None,  # 设置关键字的字体颜色
                   random_state=42,  # 设置有多少种随机生成状态，即有多少种配色方案
                   # mask=alice_mask,
                   )
    wc.generate(topWord)
    wc.to_file(pngName)

    print(newsTitle)
    return topWord