import random
import requests
from bs4 import BeautifulSoup
import re
import json
import time


def get_headers():
    user_agent = [
        {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept - Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep - alive'
        }
    ]
    return user_agent[random.randint(0, len(user_agent)-1)]


def get_page_code(keyword:str, page:int):
    """获取页面源代码"""
    url_base = 'https://www.baidu.com/s?ie=utf-8&cl=2&medium=0&rtt=1&bsst=1&rsv_dl=news_b_pn&tn=news&word={}&x_bfe_rqs=03E80&tngroupname=organic_news&newVideo=12&pn={}'
    url = url_base.format(keyword, (page-1)*10)
    headers = get_headers()
    proxy = None
    response = requests.get(url, headers=headers, timeout=5, proxies=proxy)
    page_code = response.content.decode('utf-8')
    return page_code


def save_page(page_code, name='page.html'):
    with open(name, 'w', encoding='utf-8') as f:
        f.write(page_code)


def parser(page_code:str):
    """
    html代码解析器
    return: 
        item_list: 当前页面元素集合
        next_page: 是否有下一页
    """
    soup = BeautifulSoup(page_code, features='html.parser')

    item_list = []
    news_html_list = soup.select('div#content_left div.result-op')
    for news_html_tag in news_html_list:
        news_html_soup = BeautifulSoup(news_html_tag.prettify(), features='html.parser')

        title_tag = news_html_soup.select('h3 > a')[0]
        news_url = title_tag['href']
        news_title = re.sub(re.compile(r'[\s]{2,}'), '', title_tag.get_text().strip()) # 匹配连续超过两个空白符就去掉

        author_tag = news_html_soup.select('span.c-gap-right')[0]
        news_author = re.sub(re.compile(r'[\s]+'), ' ', author_tag.get_text().strip())
        time_tag = news_html_soup.select('span.c-color-gray2')[0]
        news_time = re.sub(re.compile(r'[\s]+'), ' ', time_tag.get_text().strip())
        if re.search('前', news_time):
            nowtime = time.time()
            try:
                hour = int(re.search(re.compile(r'(\d+)小时前'), news_time).group(1)[0])
            except:
                hour = 0
            try:
                minute = int(re.search(re.compile(r'(\d+)分钟前'), news_time).group(1)[0])
            except:
                minute = 0
            real_time = nowtime - hour * 60 * 60 - minute * 60
            local_time = time.localtime(real_time)
            news_time = '{}年{}月{}日 {}:{}'.format(local_time.tm_year, local_time.tm_mon, local_time.tm_mday,
                                                    local_time.tm_hour, local_time.tm_min)

        # test = news_html_soup.select('p.c-author')[0].parent
        # summary_str = re.sub(re.compile(r'<p[\s\S]*?/p>'), '', news_html_soup.select('p.c-author')[0].parent.prettify())
        # summary_str = re.sub(re.compile(r'<span[\s\S]*?/span>'), '', summary_str)
        # news_summary = BeautifulSoup(summary_str, features='html.parser').get_text()
        # news_summary = re.sub(re.compile(r'[\s]{2,}'), '', news_summary.strip())
        summary_tag = news_html_soup.select('span.c-color-text')[0]
        news_summary = summary_tag.get_text().replace(' ', '').replace('\n', '')

        news_dict = {}
        # news_dict['keyword'] = keyword
        news_dict['url'] = news_url
        news_dict['title'] = news_title
        news_dict['author'] = news_author
        news_dict['time'] = news_time
        news_dict['summary'] = news_summary
        json_str = json.dumps(news_dict, ensure_ascii=False)
        item_list.append(json_str)

    # 判断是否有下一页
    next_page_element = soup.select('a.n')
    next_page = False
    if len(next_page_element) == 2:
        next_page = True
    elif len(next_page_element) == 1:
        a = next_page_element[0]
        res = re.search('下一页', next_page_element[0].get_text())
        if res != None:
            next_page = True
    
    return item_list, next_page