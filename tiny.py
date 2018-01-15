import os
from urllib.parse import urlparse
import re
import requests
import time
import sys
from bs4 import BeautifulSoup

# 得到bilibili视频名称和分ｐ名称
def bilibili_namer(bili_url):
    """
    Find out the real video name
    """
    request_timeout = 60
    titile=subtitle=""

    if "www.bilibili.com/video/av" in bili_url:
        start_time = time.time()
        while True:
            try:
                r = requests.get(bili_url)
                break
            except:
                if time.time() - start_time > request_timeout:
                    print("bilibili_namer timeout: unable to connect after %s s" % request_timeout)
                    return [title,subtitle]
                else:
                    time.sleep(1)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text,"lxml")
        title = soup.findAll('div',{'class':'v-title'})[0].text

        if soup.findAll('option'):
            if re.search(r'.*/video/av(\d+)(/)?$', bili_url):
                bili_url = (bili_url + '/index_1.html' if re.search(r'av(\d+)$', bili_url)
                            else bili_url + 'index_1.html')

            p_str = urlparse(bili_url).path # get /video/av/index.html
            search = soup.findAll('option',{"value":p_str})
            if search:
                subtitle = soup.findAll('option',{"value":p_str})[0].text[2:]
            else:
                print("%s out of range. 无效链接" % p_str)
                return [title,subtitle]

        return [title,subtitle]
    else:
        print("Not valid bilibili video link")
        return [title,subtitle]

# 给所有已下载的ｂ站视频添加info log,记录名称、分ｐ名称、网址
def log_all(inputfile):
    input_file = open(inputfile,'r')
    URLs = []
    URLs.extend([x for x in input_file.read().splitlines() if x])

    for uri in URLs:
        print(uri)
        rtitle,rsub_title = bilibili_namer(uri)
        newtitle = rtitle + ' ' + rsub_title if rsub_title else rtitle

        old_dir = os.getcwd() + os.path.sep + "downloaded" + os.path.sep + rtitle

        if os.path.isdir(old_dir):
            _log = open(old_dir + os.path.sep + "info.log", 'r')
            _log.write(rtitle + '\n')
            _log.write(rsub_title + '\n')
            _log.write(uri)
            _log.close()


# 给已下载b站视频重新命名: "视频名称" <---> "视频名称 分P名称"
def rename_all(inputfile):
    input_file = open(inputfile,'r')
    URLs = []
    URLs.extend([x for x in input_file.read().splitlines() if x])

    for uri in URLs:
        print(uri)
        rtitle,rsub_title = bilibili_namer(uri)
        newtitle = rtitle + ' ' + rsub_title if rsub_title else rtitle

        old_dir = os.getcwd() + os.path.sep + "downloaded" + os.path.sep + rtitle
        new_dir = os.getcwd() + os.path.sep + "downloaded" + os.path.sep + newtitle

        if os.path.isdir(old_dir):
            old_file = old_dir + os.path.sep + rtitle + '.ogg'
            new_file = old_dir + os.path.sep + newtitle + '.ogg'
            if os.path.isfile(new_file):
                print("renaming %s > %s" % (old_file.split('/')[-1],new_file.split('/')[-1]))
                #input()
                os.rename(old_file,new_file)

            print("renaming folder %s > %s" % (old_dir.split('/')[-1], new_dir.split('/')[-1]))
            #input()
            os.rename(old_dir, new_dir)

if __name__ == "__main__":
    list_file = "listaa"
    # rename_all(list_file)
    log_all(list_file)
