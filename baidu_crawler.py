#!/usr/bin/env python
# -*- coding:UTF-8 -*-
# AUTHOR: Ryan Hu
# DATE: 2020/10/28 Wed
# TIME: 18:36:39
# DESCRIPTION: 百度爬虫
from utils import get_page_code, save_page, parser
import time
import random
import fire

def baidu_crawler(keyword:str, outfile, max_page=10):
    for page in range(1, max_page+1):
        html = get_page_code(keyword, page)
        item_list, next_page = parser(html)

        print("{} {}".format(keyword, page))
        with open(outfile, 'a', encoding='utf-8') as f:
            for item in item_list:
                f.write("{}\n".format(item))
        if not next_page:
            break
        time.sleep(random.randint(1, 4))


if __name__ == "__main__":
    fire.Fire(baidu_crawler)