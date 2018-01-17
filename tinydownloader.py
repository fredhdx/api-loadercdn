import requests
import traceback
import re
import os
import time
from datetime import datetime
import sys
import argparse

request_timeout = 60
supported_scheme = ['ftp','http','https','file']

class downloader:

    def __init__(self,chunk_size=1024, headers={}):
        self.url = ""
        self.chunk_size = chunk_size
        self.size = 0 # bytes
        self.total = 0 # bytes
        self.headers = headers # headers
        self.filename = ""
        self.download_dir = ""

    def set_download_dir(self,location=""):
        if location:
            self.download_dir = location
            if not os.path.isdir(self.download_dir):
                os.makedirs(self.download_dir)

    def remove_nonchars(self, name):
        (name,_) = re.subn(r'[\\\/\:\*\?\"\<\>\|]', '', name)
        return name

    def touch(self, filename):
            with open(filename, 'w') as fin:
                    pass

    def get_filename(self,url):
        global supported_scheme

        from urllib.parse import urlparse
        if not url.split('//')[0] in supported_scheme: # force scheme for parsing
            url = "http://" + url
        uri = urlparse(url)
        domain = '{uri.scheme}://{uri.netloc}'.format(uri=uri)
        path = uri.path

        # direct file
        if len(path.split('/')[-1].split('.')) > 1:
            return path.split('/')[-1]

        # link does not contain direct file, try analyze by domain
        found = False
        headers = self.headers
        headers['Range'] ='bytes=0-4'
        if domain == "https://loadercdn.io/":
            try:
                r = requests.get(url,headers=headers, stream=True)
                cheaders = r['headers']['content-disposition']
                from urllib.parse import unquote
                found = True
                filename = re.sub(r'.*filename\*=UTF-8\'\'','',unquote(cheaders)).strip()  # example.ext
                filename = self.remove_nonchars(filename)
                r.close()
            except Exception as e:
                print(e)
        else:
            print("%s domain not currently supported" % domain)
            print("....using universal filename download-%Y-%m-%d-%H-%M-%S.raw")

        if found:
            return filename
        else:
            return "download" + '-' + datetime.now().strftime('%Y-%m-%d-%H-%M')

    def support_continue(self, url):
        headers = self.headers
        headers['Range'] ='bytes=0-4'
        start_time = time.time()
        while True:
            try:
                r = requests.head(url, headers = headers)
                crange = r.headers['content-range']
                self.total = int(re.match(r'^bytes 0-4/(\d+)$', crange).group(1))
                return True
            except requests.exceptions.ConnectionError:
                if time.time() - start_time > request_timeout:
                    print("support_continue: Exceeding maximum timeout after %s seconds" % request_timeout)
                    return False
                else:
                    print(e)
                    time.sleep(1)

        return False


    def simple_download(self):
        finished = False

        self.set_download_dir(self.download_dir)

        filename = self.download_dir + os.path.sep + self.filename
        start_time = time.time()
        size = 0
        if r.status_code == 200:
            with open(filename,'wb') as f:
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)
                        f.flush()
                    print('Now: %d KB' % size/1024)
                finished = True
        else:
            print("Request returned bad status code %d" % r.status_code)
            print("%f downloading failed. Continue to next download." % filename.split(os.path.sep)[-1])
            return

        if finished:
            spend = int(time.time() - start_time)
            if spend:
                speed = int(size/spend/1024)
            else:
                speed = 'n/a'
            print("Download finished.\nTotal time: %d seconds, Download speed: %sk/s\n" % (spend, str(speed)))
        else:
            print("Download not finished. %d KB saved." % (size/1024))

    def download_continue(self):
        finished = False
        headers = self.headers

        self.set_download_dir(self.download_dir)

        tmp_file = (self.download_dir + os.path.sep +
                self.filename.split(os.path.sep)[-1].split('.')[0] + '.downtmp')
        filename = self.download_dir + os.path.sep + self.filename

        if self.support_continue(self.url):
            try:
                with open(tmp_file,'rb') as fin:
                    self.size = int(fin.read()) + 1
                    print("continue downloading %s from %d\n" % (self.filename,self.size))
            except:
                self.touch(tmp_file)
            finally:
                headers['Range'] = "bytes=%d-" % (self.size, )
        else:
            self.touch(tmp_file)
            self.touch(filename)

        size = self.size
        total = self.total

        try:
            headers = self.headers
            r = requests.get(self.url, stream=True, headers=headers)
        except Exception:
            print(e)
            print("%s downloading failed. Continue to next task." % filename.split(os.path.sep)[-1])
            return

        print("Total file size: %d KB" % (total/1024))
        start_time = time.time()
        with open(filename,'ab') as f:
            try:
                for chunk in r.iter_content(chunk_size=self.chunk_size):
                    if chunk:
                        f.write(chunk)
                        size += len(chunk)
                        f.flush()
                    print("Now: %d, Total: %d" % (size,total))
                finished = True
                os.remove(tmp_file)
                spend = int(time.time() - start_time)
                if spend:
                    speed = int(size/spend/1024)
                else:
                    speed = 'n/a'
                print("Download finished.\nTotal time: %d seconds, Download speed: %sk/s\n" % (spend, str(speed)))
            except:
                traceback.print_exc()
                print("Download paused.")
            finally:
                if not finished:
                    with open(tmp_file,'w') as ftmp:
                        print(size)
                        ftmp.write(str(size))

    def downloader_wrapper(self,url="",headers={},custom_filename="",custom_dir=""):

        # assing url
        if not url:
            print("No url entered. Continue to next task.")
            return
        else:
            self.url = url

        # assign header
        self.headers = headers
        # assign filename
        self.filename = custom_filename if custom_filename else self.get_filename(self.url)
        # assign download_dir
        self.download_dir = custom_dir if custom_dir else os.getcwd() + os.path.sep + "tiny-downloader"

        # download
        self.download_continue()


def load_headers(headerfile):
    try:
        f = open(headerfile,'r')
    except Exception as e:
        print("headers.txt open failed. Revert to default fake-headers")
        sys.exit(1)

    _headers = {}
    for line in f.readlines():
        if line.strip():
            key, value = line.split(':')
            key = re.sub(r'^\"|^\'|\"$|\'$', '', key.strip())
            value = re.sub(r'^\"|^\'|\"$|\'$|,$|(\'|\"),$','',value.strip())
            _headers[key] = value
    return _headers

def main():
    parser = argparse.ArgumentParser(
        prog='simple downloader',
        usage='python3 downloader.py [OPTIONS] URLs',
        description='filename extraction supported: loaderCDN',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='Print this help message and exit'
    )
    parser.add_argument(
        '-u', '--url', type=str,
        help='url'
    )
    parser.add_argument(
        '-o', '--output', type=str,
        help='custom output filename'
    )
    parser.add_argument(
        '-D', '--dir', type=str,
        help='custom save dir'
    )
    parser.add_argument(
        '-a', '--agent', type=str,
        help='request user agent (default)'
    )
    parser.add_argument(
        '-r', '--referer', type=str,
        help='request referer'
    )
    parser.add_argument(
        '-c', '--cookie', type=str,
        help='request cookie (default)'
    )
    parser.add_argument(
        '-H', '--header', metavar="HEADER_FILE",
        help='Load headers.txt'
    )

    args = parser.parse_args()

    if args.help or len(sys.argv) == 1:
        parser.print_help()
        sys.exit()

    custom_dir = "" if not args.dir else args.dir
    custom_filename = "" if not args.output else args.output
    usercookie = "" if not args.cookie else args.cookie
    userreferer = "" if not args.referer else args.referer
    url = "" if not args.url else args.url
    useragent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36' if not args.agent else args.agent
    # default header
    if args.header:
        headers = load_headers(args.header)
    else:
        headers = {
                'User-Agent': useragent,
                'Referer': userreferer,
                'Cookie': usercookie
        }

    if "bilibili" in url:
        headers['User-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'

    if url:
        # def downloader_wrapper(self,url="",headers={},custom_filename="",custom_dir=""):
        downloader().downloader_wrapper(url=url,headers=headers,custom_filename=custom_filename,custom_dir=custom_dir)

if __name__ == "__main__":
    main()
