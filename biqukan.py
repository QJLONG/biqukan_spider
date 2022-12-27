# conding:UTF-8
"""
功能:输入笔趣看网小说的url, 下载小说的全部章节。
url: https://www.biqukan.la
"""

import requests
import re
from bs4 import BeautifulSoup
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time
import sys
import cn2an
"""
类声明：爬取笔趣看小说
target_url: 整部小说的URL   例: https://www.biqukan.la/book/128155
"""
class BiqukanDownloader(object):
    def __init__(self, target_url) -> None:
        self.target_url = target_url
        self.__headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
        self.chapters_dict = {}

    """
    函数声明：获取所有页中的章节目录
    Parameters:
        None
    Returns:
        int 存储章节的页数
    """
    def get_page_num(self):
        self.page_num = 0
        response = requests.get(self.target_url, headers=self.__headers)
        if response.text == None:
            print(">> 输入的URL有误！！！")
            sys.exit()
            
        select_soup = BeautifulSoup(response.text, "html.parser")
        return len(select_soup.find_all("option"))

    """
    函数声明: 获取所有章节的标题和url, time:16.030723094940186
    Parameters: page_num存储章节的页数
    Returns: chapters_dict {key:第x章_filename, value:url}
    """

    def get_all_urls(self, page_num):
        for i in range(page_num):
            print(">> 获取链接中... %d%%" % ((i+1)/page_num*100), end="\r")
            page_url = f"{self.target_url}/index_{i+1}.html"
            resp = requests.get(page_url)
            soup = BeautifulSoup(resp.text, "html.parser")
            dl = soup.find("dl", class_="panel-body panel-chapterlist")
            dds = dl.find_all("dd")
            for dd in dds:
                chapter_url = f"{self.target_url}/{dd.get('href')}"
                title = dd.get_text().replace(" ", "_")
                cn_number = re.search(r"[第弟](.+?)章", title)
                if cn_number != None:
                    cn_number = cn_number.group(1)
                    title = title.replace(cn_number, str(cn2an.cn2an(cn_number)))
                self.chapters_dict[title] = chapter_url
        print(">> 链接获取完成!")
        return self.chapters_dict
        
    """
    函数声明：爬取小说某一章节的内容
    Parameters:
        chapter_url:小说章节的URL
    Returns:
        content: 某一章小说的内容
    """
    def get_content(self, file_name, chapter_url):
        resp = requests.get(chapter_url, headers=self.__headers)
        content_soup = BeautifulSoup(resp.text, "html.parser")
        content_div = content_soup.find("div", class_="panel-body")
        content = str(content_div).replace("<br/>", "\n").replace("<br>", "\n")
        path = Path("./data")
        if not path.exists():
            print(">> 路径data不存在，已为您自动创建文件夹data")
            path.mkdir()
        with open(Path().joinpath("data", f"{file_name}.txt"), "w", encoding="utf-8") as f:
            f.write(content)
        

if __name__ == '__main__':
    start = time.time()
    target_url = input(">> 请输入要下载小说的URL: \n")
    downloader = BiqukanDownloader(target_url=target_url)
    page_num = downloader.get_page_num()
    url_dict = downloader.get_all_urls(page_num=page_num)
    pool = ThreadPoolExecutor(20)
    # print(url_dict)
    content = 1
    total = len(url_dict)
    print(">> 共%d章" % total)
    print(">> 文章下载中...")
    futures = []
    for title in url_dict:
        futures.append(pool.submit(downloader.get_content, file_name=title, chapter_url=url_dict[title]))
    pool.shutdown()
    print(">> 下载完成！")
    end = time.time()
    print(">> 耗时：", end-start)