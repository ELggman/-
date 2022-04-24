import requests
from lxml import etree
import os
import time
from multiprocessing.dummy import Pool
from newspaper import Article
import re

global ready_list
global list_len
ready_list = []
list_len = 2000


def get_pagetext(url):
    global headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/94.0.4606.71 Safari/537.36 Edg/94.0.992.38'
    }
    resp = requests.get(url, headers)
    resp.encoding = 'utf-8'
    return resp.text


def get_url_list(url):
    try:
        resp = get_pagetext(url)
        tree = etree.HTML(resp)
        url_list = tree.xpath('//a/@href')
    except:
        return
    for page_url in url_list:
        if len(ready_list) >= list_len:
            break
        if page_url.startswith(
                'http') and page_url not in ready_list:  # and 'news' in page_url:
            ready_list.append(page_url)


def remove_empty_line(content):
    r = re.compile(r"^\s+$", re.M | re.S)  # 代表匹配全是空白字符的行
    s = r.sub('', content)
    r = re.compile(r"\n+", re.M | re.S)  # 代表匹配至少一个空行
    s = r.sub('\n', s)
    return s


def remove(str):
    str = str.replace('\n', '')
    str = str.replace(' ', '')
    str = str.replace('\t', '')
    str = str.replace('\r', '')
    return str


def remove_content(content):
    content = re.sub(r"[A-Za-z\：\·\—\，\。\“ \”\？\/\（\）\！]", "", content)
    return content


# 用newspaper对正文以及标题进行提取
def get_t(url):
    global co
    try:
        news = Article(url, language='zh')
        news.download()
        news.parse()
    except:
        return
    # 获取正文
    content = news.text.strip().replace('\n\n', '\n')
    # 对正文长度进行初步筛选
    if len(content) < 80:
        return
    # 删除空行以及换行符
    content = remove(remove_empty_line(content))
    content = remove_content(content)
    # 获取标题
    title = news.title.strip()
    # 写入网页的 链接 标题 正文
    text_path = './download_file/' + str(co) + '.txt'
    fp = open(text_path, 'w+', encoding='utf-8')
    fp.write(url + '\t\t' + title + '\t\t' + content)
    fp.close()
    co += 1


if __name__ == '__main__':

    start_time = time.time()
    if not os.path.exists('./download_file/'):
        os.mkdir('./download_file/')
    url = 'https://news.sina.com.cn/'
    ready_list.append(url)

    get_url_list(ready_list[0])
    for page_url in ready_list:
        get_url_list(page_url)
        if len(ready_list) >= list_len:
            break
    end_time1 = time.time()
    global co
    co = 20000
    print(end_time1 - start_time)


    pool = Pool(30)
    pool.map(get_t, ready_list)
    pool.close()
    pool.join()

    end_time2 = time.time()

    print(end_time2 - start_time)
