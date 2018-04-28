import requests
import http.client
import sys

fake_headers = { 'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
                }

def file_download(url):
    try:
        size = 0
        filename = "test.mp4"
        r = requests.get(url,headers=fake_headers,stream=True)
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