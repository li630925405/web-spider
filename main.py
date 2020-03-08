# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QPushButton,QWidget, QLabel, QLineEdit, QTextEdit, QGridLayout,QApplication
from  PyQt5.QtGui import QPixmap
from html.parser import HTMLParser
from html.entities import name2codepoint
from urllib.request import urlopen, Request,urlparse
import http
import json
from numpy import *
from fractions import Fraction
import jieba
from scipy.misc import imread  # scipy.misc.imread() 用于处理图像,返回多维数组对象
from wordcloud import WordCloud, ImageColorGenerator
import matplotlib.pyplot as plt

class Myparser_body(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._parse = ''
        self._print = False

    def handle_starttag(self, tag, attrs):
        if ('class', 'main-title') in attrs or ('class', 'titleArea') in attrs or ('id', 'artibodyTitle') in attrs:
            self._parse = 'title'
        elif ('name', 'description') in attrs or ('class', 'subTitleP') in attrs or ('if', 'artibody') in attrs:
            self._parse = 'body'
            for item in attrs:
                if item[0] == 'content':
                    content.append(item[1])
        elif tag != 'h1' and tag != 'p':
            self._parse = False
        if tag == 'p' or tag == 'h1':
            self._print = True

    def handle_data(self, data):
        if self._parse == 'title' and self._print:   #为何进来好几次
            info = data.strip()
            if info and info[0] != '\n':
                title.append(info)
        elif self._parse == 'body' and self._print:
            info = data.strip()
            if info and info[0] != '\n':
                content.append(info)

class Example(QWidget): 
    def __init__(self): # 初始化
        super().__init__()
        self.initUI()
    
    def initUI(self):
        #GUI布局及控件放置
        search_label1 = QLabel("请输入搜索网址：")
        search_item1 = QLineEdit()
        search_label2 = QLabel("请输入背景图片名称：")
        search_item2 = QLineEdit()
        btn1 = QPushButton("开始搜索", self)
        btn2 = QPushButton("清空", self)
        l1 = QLabel()
        grid = QGridLayout()
        grid.setSpacing(9)
        grid.addWidget(search_label1, 1, 0)
        grid.addWidget(search_item1, 2, 0)
        grid.addWidget(search_label2, 3, 0)
        grid.addWidget(search_item2, 4, 0)
        grid.addWidget(btn1, 5, 0)
        grid.addWidget(btn2, 5, 1)
        grid.addWidget(l1, 6, 0, 20, 0)
        self.setLayout(grid)

        def searching():
            try:
                net = search_item1.text()
                picture = search_item2.text()
                word_cloud(net, picture)
                png = QPixmap('wordcloud.png')
                l1.setScaledContents(True)
                l1.setPixmap(png)
            except:
                print(sys.exc_info())
                l1.setText('url or picture not found... orz')
        btn1.clicked.connect(searching)
        
        def clear():
            l1.setPixmap(QPixmap(""))
        btn2.clicked.connect(clear)
        
        #設置窗口
        self.setGeometry(500, 100, 800, 800)
        self.setWindowTitle("搜索云图GUI")

def parse_article(url):
    global title
    global content
    content = []
    title = []
    parser = Myparser_body()
    r = urlopen(Request(url, headers = {'User-agent': 'Mozilla 5.10'}), timeout = 4)
    parser.feed(r.read().decode('utf8'))
    res = title[0] + '\n  ' + ''.join(content)[0:100] + '......'
    return res
        
def ini_Pr(c):
    pr = zeros((c.shape[0], 1), dtype = float)
    for i in range(c.shape[0]):
        pr[i] = float(1) / c.shape[0]
    return pr

def PR(p, m, v):
    while ((v - (p * dot(m, v) + (1 - p) * v) < 0.0000001).all() == False):
        v = p * dot(m, v) + (1 - p) * v
    return v

class Myparser_net(HTMLParser):
    def __init__(self, base_url):
        HTMLParser.__init__(self)
        self._parse = False
        self.base_url = base_url  

    def handle_starttag(self, tag, attrs):
        global count
        global total
        global d
        if ('class', 'newslist') in attrs:
            self._parse = True
        if tag == 'a':
            for name, link in attrs:
                if name == 'href':
                    pr = urlparse(link)
                    if pr.netloc != 'news.sina.com.cn' and link != self.base_url[:-1]:
                        return
                    if len(pr.path) > 5 and pr.path[1:4] == 'gov':
                        return
                    #print(len(pr.path))  开始写成了print path,直接return了但是没报错
                    if len(pr.path) < 5 and link != self.base_url[:-1]:
                        return
                    if (pr.path[-5 : -1] + pr.path[-1]) != 'shtml' and link != self.base_url:
                        return
                    if pr.scheme == '' or pr.path[0:3] == 'http':
                        while link[0] == '.':
                            j = link.find('/')
                            link = link[j + 1:]
                        link = self.base_url + link
                    #elif pr.scheme != 'http':  因为是https. but不写成分函数就可以？
                    #    return
                    if link[-1] == '/':
                        link = link[0:-1]
                    elif link == '':
                        link = self.base_url
                    link = link.strip()
                    queue.append(link)
                    if not link in index:
                        index.append(link)
                        count += 1
                    d[link] = d.get(link, 0) + 1
                    total += 1

def parse_news(base_url):
    global depth
    global count
    global d
    global total
    net = []
    graph = {}
    prob = {}
    index.append(base_url)
    queue.append(base_url)
    while queue and depth > 0:
        for i in range(len(queue)):
            url = queue.pop(0)
            d = {}
            total = 0
            outlink[url] = {}
            try:
                r = urlopen(Request(url, headers={'User-agent': 'Mozilla 5.10'}))
            except:
                outlink[url][base_url] = 1
                print('1', sys.exc_info())
                continue
            parser = Myparser_net(url)
            try:
                parser.feed(r.read().decode('utf8', 'ignore'))
            except http.client.IncompleteRead as e:
                parser.feed(e.partial.decode('utf8', 'ignore'))
            if not d:
                outlink[url][base_url] = 1
            for link in d:
                outlink[url][link] = d[link] / total
            depth -= 1

    while queue:
        url = queue.pop(0)
        if not url in outlink:
            outlink[url] = {}
            outlink[url][base_url] = 1

    markov = [[0] * count for i in range(count)]
    for link in index:
        for out_link in outlink[link]:
            markov[index.index(out_link)][index.index(link)] = outlink[link][out_link]
    markov_array = (array(markov))
    
    f = open('aaa.txt', 'w')
    out = json.dumps(markov_array)
    f.write(out)
    f.close()
    
    pr = ini_Pr(markov_array)
    p = 0.85
    res = PR(p, markov_array, pr).tolist()


    for i in range(count):
        prob[index[i]] = res[i][0] #res每一项都是数组？。。
    prob = sorted(prob.items(), key = lambda x: x[1], reverse = True)
    for i in range(1, 6):
        try:
            net.append(prob[i][0])
        except:
            pass
            #print(prob)
    return net

def get_words(texts):
    exclude = ['北京', '记者', '标题', '一个','一种','什么','这个','太过','先','永远','虽然','但是','因为','想要','这种','有人','或者','可以','一下','没有']
    words_list = []
    word_generator = jieba.cut(texts, cut_all = False)
    for word in word_generator:
        if word.strip() not in exclude:
            words_list.append(word)
    return ' '.join(words_list)

def word_cloud(base_url, picture):
    text = []
    back_color = imread(picture)  #背景颜色为指定图
    wc = WordCloud(background_color = 'white',
                   max_words = 100,
                   mask = back_color,
                   max_font_size = 200,
                   font_path = "C:/Windows/Fonts/STFANGSO.ttf",
                   random_state = 100)
    net = parse_news(base_url)
    for i in range(5):
        text.append(parse_article(net[i]))
    text = ''.join(text)
    wc.generate(get_words(text)) #词频统计函数
    image_colors = ImageColorGenerator(back_color)
    plt.imshow(wc)
    plt.axis('off')
    plt.figure()
    plt.imshow(wc.recolor(color_func = image_colors))
    plt.axis('off')
    wc.to_file('wordcloud.png')

if __name__ == "__main__":
    queue = []
    index = []
    outlink = {}
    d = {}
    total = 0
    depth = 1
    count = 1
    content = []
    title = []    
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec_())
