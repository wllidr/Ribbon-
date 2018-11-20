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

def part(info, newsTitle):
    # 分词并且提取关键词
    pattern = re.compile(u'\t|\n|\.|-|—|:|;|\)|\(|\?|"|、|。|，')
    string_data = re.sub(pattern, '', info)
    string_data = re.sub('\d', '', string_data)
    seg_list_exact = jieba.cut(string_data, cut_all=False)
    object_list = []
    remove_words = [u'的', u'，', u'和', u'是', u'随着', u'对于', ' ', u'对', u'等', u'能', u'都', u'。',
                    u'、', u'中', u'与', u'在', u'其', u'了', u'可以', u'进行', u'有', u'更', u'需要', u'提供',
                    u'多', u'能力', u'通过', u'会', u'不同', u'一个', u'这个', u'我们', u'将', u'并',
                    u'同时', u'看', u'如果', u'但', u'到', u'非常', u'—', u'如何', u'包括', u'这', '》', '《',
                    '“', '”', ':', '年月日', '年', '月', '日', 'nbsp', 'ldquo', 'rdquo']

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
                   )
    wc.generate(topWord)
    wc.to_file(pngName)

    print(newsTitle)
    return topWord