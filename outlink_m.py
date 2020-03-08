#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from html.parser import HTMLParser
from urllib.request import urlopen, Request, urlparse
import http
import json

class Myparser(HTMLParser):
    def __init__(self, url):
        HTMLParser.__init__(self)
        self.base_url = url

    def handle_starttag(self, tag, attrs):
        global queue
        global index
        global d
        global count
        base_netloc = self.base_url[self.base_url.find(':') + 3 : -1]
        if tag == 'a':
            for name, link in attrs:
                if name == 'href':
                    pr = urlparse(link)
                    i = pr.path.find('.')
                    if i > 0 and pr.path[i + 1:] in ['jpg', 'jpeg', 'gif', 'bmp', 'flv', 'mp4', 'wmv','swf','css', 'rar', 'exe']:
                        return
                    if '#' in link:  # HTTP请求不包括#
                        j = link.find('#')
                        link = link[:j]
                    if link == '':  # attrs:('href', '')
                        return
                    if pr.scheme == '' and 'http' in pr.path:
                        link = pr.path[1:]
                    elif pr.scheme == '': 
                        while link[0] == '.':
                            j = link.find('/')
                            link = link[j + 1:]
                        link = self.base_url + link
                    elif pr.scheme != 'http' or pr.netloc != base_netloc:
                        return
                    if link[-1] == '/':
                        link = link[0:-1]
                    link = link.strip()
                    queue.append(link)
                    if not link in index:
                        index.append(link)
                        count += 1
                    d[link] = d.get(link, 0) + 1
                    
#http://scse.buaa.edu.cn/
def outlink(base_url):
    global queue
    queue.append(base_url)
    global index
    index = []
    index.append(base_url)
    global d
    global depth
    global count
    outlink = {}
    depth = 2
    count = 1
    print('parse begin...')
    while queue and depth > 0:
        for i in range(len(queue)):
            url = queue.pop(0)
            print(url + '...', end=' ')
            d = {}
            parser = Myparser(url)
            r = urlopen(Request(url, headers={'User-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}))
            try:
                parser.feed(r.read().decode('utf8', 'ignore'))
            except http.client.IncompleteRead as e:
                parser.feed(e.partial.decode('utf8', 'ignore'))
            outlink[url] = {}
            if not d:
                outlink[url][base_url] = 1
            for link in d:
                outlink[url][link] = d[link]
            print('Done!')
        depth -= 1
        
    while queue:
        url = queue.pop(0)
        if not url in outlink:
            outlink[url] = {}
            outlink[url][base_url] = 1
    return outlink

if __name__== "__main__":
    index = []
    queue = []
    d = {}
    url = input()
    count = 1
    depth = 2

    dic = outlink(url)

    print('Opening the file \'temp.txt\' ...')
    with open('temp.txt', 'w') as f:
        print('Writing...', end='')
        f.write(json.dumps(dic))
        print('Finish')

    print("Everything's ok. Happy hacking!")
    
