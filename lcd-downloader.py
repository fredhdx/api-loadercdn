#!/usr/bin/env python3
import urllib
import json
import os
import re
import sys
import time
import argparse
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from datetime import datetime
import requests

# default parameter
dry_run = False
format = 'mp3'
quality = 1
overwrite_lock = False
fake_headers = { 'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
                }
custom_headers = {}

"""example content
continue_download is not supported!

{
  "id": "6QJsqtl9V",
  "hostname": "site-which-embeds-vimeo-videos.com",
  "link": "https://vimeo.com/165547092",
  "title": "Character: Tuoni: Point",
  "uploader": "Gemma Hanley",
  "track": "Tunoi: Point",
  "resolution": "1280x720",
  "size": "6.4 MB",
  "fps": 30,
  "originalFormat": "mp4",
  "wantedFormat": "mp4",
  "originalType": "video",
  "wantedType": "video",
  "url": "http://dashboard/download?id=6QJs04i92",
  "thumbnail": "http://dashboard/thumbnail?id=6QJs04i92",
  "directThumbnail": "http://dashboard/thumbnail?id=6QJs04i92&direct=true",
  "subtitles": [
    {
      "language": "English",
      "exts": [
        {
          "ext": "srt",
          "url": "http://dashboard/subtitle?id=6QJs04i92&key=English&index=0"
        }
      ]
    }
  ],
  "formats": [
    {
      "format": "mp4",
      "url": "http://dashboard/download?id=6QJs04i92&type=mp4",
      "filename": "My file.mp4"
    },
    {
      "format": "mp3",
      "url": "http://dashboard/download?id=6QJs04i92&type=mp3",
      "filename": "My file.mp3"
    }
  ],
  "qualities": [
    {
      "url": "http://dashboard/download?id=6QJs04i92&quality=1",
      "note": "Ogg Vorbis",
      "format": "ogg",
      "size": "4.4 MB",
      "vcodec": "none"
    },
    {
      "url": "http://dashboard/download?id=6QJs04i92&quality=2",
      "note": "MP3 V0",
      "format": "mp3",
      "size": "5.8 MB",
      "fps": 30,
      "vcodec": "none"
    },
    {
      "url": "http://dashboard/download?id=6QJs04i92&quality=3",
      "note": "1080p",
      "format": "mp4",
      "vcodec": "h264",
      "acodec": "aac",
      "size": ""
    },
    {
      "url": "http://dashboard/download?id=6QJs04i92&quality=4",
      "note": "540x311",
      "format": "flv"
    }
  ]
}
"""


class loaderCDN():
    stream_types = ['mp4','flv','avi','mp3','wav','ogg','flac']
    api_url = "https://loadercdn.io/api/v1/create"
    api_key = "" # please apply for your own free copy

    def set_key(self,api_key):
        if api_key:
            self.api_key = api_key
        else:
            print("Empty api_key. Exit.")
            sys.exit()

    def api_req(self, url, format="", direct=False, seek="", duration="", headers=fake_headers):
        """
        Use loaderCDN api to parse video url and get direct links
        Documentation: https://loadercdn.docs.apiary.io/
        Return value: dict(response_header,response_content,response_url)
        """
        queries = {'format':format, 'direct':'true' if direct else '','seek':seek,'duration':duration}
        url = url + '?' + urlencode(queries)
        values = """
                  {{
                    "key": {api_key},
                    "link": {query_url}
                  }}
                """.format(api_key='"' + self.api_key + '"', query_url='"' + url + '"')

        try:
            request = Request(self.api_url, data=bytes(values,encoding='utf-8'), headers=headers)
            response = urlopen(request)
        except urllib.error.URLError as e:
            print(e)
            sys.exit(1)

        status_code = response.getcode()
        if status_code == 201:
            response_header = response.getheaders()
            response_content = response.read().decode("utf-8")
            response_url = response.geturl()
            return {'response_header':response_header,'response_content':response_content, 'response_url':response_url}
        elif status_code == 200:
            print("This video does not exist: %s" % url)
            return None
        elif status_code == 400:
            print("Parameter missing / wrong data type")
            print("Parameters:\n%s" % str(args))
            print("Data:\n%s" % values)
            return None
        elif status_code == 401:
            print("Invalid API key")
            return None
        else:
            print("Unknown error running api_req\n")
            return None

    def parse_response_content(self,response_matrix):
        """
        response_matrix: dict(response_header,response_content,response_url)
        """
        # check
        if not isinstance(response_matrix,dict):
            print("parse_response_content error: input not dict")
            sys.exit(1)

        headers = dict(response_matrix['response_header']) # input: list
        content = json.loads(response_matrix['response_content']) # input: string
        requested_url = response_matrix['response_url'] # input: string

        return {'headers':headers, 'content':content, 'url':requested_url}

class ProgressBar(object):
    def __init__(self, title, count=0.0, run_status=None, fin_status=None, total=100.0,    unit='', sep='/', chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "[%s] %s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.statue)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status, self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end_str)


def load_headers(headerfile):
    """
    load header options from headers.txt
    format: key: value \n key: value \n " and ' are allowed
    """
    global custom_headers

    try:
        f = open(headerfile,'r')
    except Exception as e:
        print("headers.txt open failed. Revert to default fake-headers")

    _headers = {}
    text = f.readlines()
    for line in text:
        if line.strip():
            key, value = line.split(':')
            key = re.sub(r'^\"|^\'|\"$|\'$', '', key.strip())
            value = re.sub(r'^\"|^\'|\"$|\'$|,$|(\'|\"),$','',value.strip())
            _headers[key] = value

    must = False
    for key, value in _headers.items():
        print(key, value)
        if key == 'Content-Type' and value == 'application/json':
            must = True

    if must:
        print("Custom headers.txt loaded")
        custom_headers = _headers
    else:
        print("Headers must contain entry: Content-Type: application/json\nCustom headers.txt not loaded")

    return

def download_main(myloader, URLs=[], info_only=False, format=format,quality=quality):
    global custom_headers
    global fake_headers
    global dry_run

    _headers = custom_headers if custom_headers else fake_headers

    try:
        if URLs:
            print("共%d条视频" % len(URLs))
            count = 0
            save_dir = os.getcwd() + os.path.sep + 'downloaded'
            if not os.path.isdir(save_dir):
                os.makedirs(save_dir)

            for url in URLs:
                # use loaderCDN API to get downloadable response
                response = myloader.api_req(url,headers=_headers)

                if response:
                    print("开始解析第%d/%d条视频" % (count+1,len(URLs)))
                    # parse and download requested file
                    parsed_response = myloader.parse_response_content(response)
                    content = parsed_response['content']

                    avail_formats = [x['format'] for x in content['formats']]
                    if format in avail_formats:
                        index = avail_formats.index(format)
                        title = content['formats'][index]['filename'].strip()
                        url = content['formats'][index]['url'].strip()
                        print("解析成功: " + url)

                        if not dry_run and not info_only:
                            if format == content['originalFormat']:
                                url = url + '&quality=' + str(quality)

                            if format == 'mp4' and "bilibili" in url:
                                print(".mp4 download is not currently supported on bilibili.com")
                                print("Please choose another format")
                                sys.exit()

                            print("开始下载第%d/%d个视频" % (count+1,len(URLs)))
                            print("名称:%s" % title)
                            filepath = save_dir + os.path.sep + title.split('.')[0]

                            # from downloader import downloader
                            # downloader().downloader_wrapper(url,headers=_headers,custom_dir=filepath,custom_filename=title)

                            if not os.path.isdir(filepath):
                                os.makedirs(filepath)

                            filename = filepath + os.path.sep + title

                            global overwrite_lock
                            if os.path.isfile(filename):
                                if overwrite_lock:
                                    backupfile = (filepath + os.path.sep + "backup-" + title.split('.')[0]
                                            + datetime.now().strftime('%Y-%m-%d-%H-%M') + '.' + title.split('.')[1])
                                    os.rename(filename, backupfile)
                                else:
                                    print("视频已存在: %s" % title)
                                    count += 1
                                    continue

                            try:
                                size = 0
                                r = requests.get(url,headers=_headers,stream=True)
                                chunk_size = 512*1024 # 单次请求最大值
                                with open(filename,'wb') as f:
                                    for chunk in r.iter_content(chunk_size=chunk_size):
                                        if chunk:
                                            f.write(chunk)
                                            size += len(chunk)
                                            f.flush()
                                        sys.stdout.write('\b'*64 + 'Now: %d' % size)
                                        sys.stdout.flush()
                            except Exception as e:
                                print(e)
                                sys.exit(1)

                            print("%s下载完毕\n" % title)

                time.sleep(5)
                count += 1

    except Exception as e:
        print(e)
        sys.exit(1)

def main():

    parser = argparse.ArgumentParser(
        prog='loadercdn api',
        usage='load-bili [OPTION]... URL...',
        description='A loaderCDN API port to python, default format: mp3',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help message and exit'
    )

    dry_run_grp = parser.add_argument_group(
        'Dry-run options', '(no actual downloading)'
    )
    dry_run_grp = dry_run_grp.add_mutually_exclusive_group()
    dry_run_grp.add_argument(
        '-i', '--info', action='store_true', help='Print extracted information'
    )
    dry_run_grp.add_argument(
        '-u', '--url', action='store_true',
        help='Print extracted information with URLs'
    )

    parser.add_argument(
        '-F', '--format', type=str,
        help='specify downloading format'
    )
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='force overwrite existing file'
    )
    parser.add_argument(
        '-H', '--headers', metavar="HEADER_FILE",
        help='Load headers.txt'
    )
    parser.add_argument(
        '-I', '--input-file', metavar='FILE', type=argparse.FileType('r'),
        help='Read non-playlist URLs from FILE'
    )
    parser.add_argument(
        '-k', '--key', type=str,
        help='supply loadercdn api key'
    )

    parser.add_argument('URL', nargs='*', help=argparse.SUPPRESS)

    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit()

    global dry_run
    global custom_headers
    global format
    global quality
    global api_key
    global overwrite_lock

    info_only = args.info
    if args.url:
        dry_run = True

    if args.headers:
        load_headers(args.headers)

    if args.format:
        format = str(args.format)

    if args.force:
        overwrite_lock = True

    URLs = []
    if args.input_file:
        print("You are loading urls from %s", args.input_file)
        URLs.extend([x for x in args.input_file.read().splitlines() if x])

    URLs.extend(args.URL)

    if not URLs:
        parser.print_help()
        sys.exit()

    if not args.key:
        print("Please enter your loaderCDN api key: -k/--key api_key")
        sys.exit()

    try:
        myloader = loaderCDN()
        myloader.set_key(args.key)
        download_main(myloader, URLs, info_only=info_only ,format=format,quality=quality)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()
