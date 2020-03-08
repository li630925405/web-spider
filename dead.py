from outlink_m import outlink
from PR_m import pagerank

if __name__ == "__main__":
    #print(outlink('http://www.baidu.com'))
    dic = outlink('https://news.sina.com.cn/')
    
    print(dic)
