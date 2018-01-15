# A Python Port for loaderCDN video downloading service

# It's a free CDN service to get downdable links for many online video sites. You can download OTHER FORMATS too!
Visit https://loadercdn.io/ to sign up for your free API.

# Supported website: bilibili.com, youtube.com, and more
# Supported format: mp3, flv, mp4(partial), ogg, avi and more

# Usage

**python3 lcd-downloader.py [OPTIONS] -k apikey -F flv URLs**

*You must supply your loaderCDN api key with -k/--k. Get your key [here](https://loadercdn.io/)*
*mp4 currently is not downdoadable from bilibili.com/ It's probably encrypted; loaderCDN cann't decipher it*

```
A loaderCDN API port to python, default format: mp3

optional arguments:
  -h, --help            Print this help message and exit
  -F FORMAT, --format FORMAT
                        specify downloading format
  -f, --force           force overwrite existing file
  -H HEADER_FILE, --headers HEADER_FILE
                        Load headers.txt
  -I FILE, --input-file FILE
                        Read non-playlist URLs from FILE
  -k KEY, --key KEY     supply loadercdn api key, or key.txt
  -s START, --start START
                        starting position of URLs list: 1-len(URLs)
  -e END, --end END     end position of URLs list: 1-len(URLs)

Dry-run options:
  (no actual downloading)

  -d, --dry             Print extracted information (headers)
  -u, --url             Print extracted URLs (only)
```

## load a file of url list
`python3 lcd-downloader.py -I listfilfe`

## use custom header file
`python3 lcd-downloader.py -H headers.txt URLs`

header files must be format:
```
Key: value,
Key: value,
Key: value
```
*key,value strings can be single/double quoted \'\"key\'\"*
*comma(,) after value not necessary*

## force overwrite existing files: -f/--force

# Download from existing files/multithreading: NOT SUPPORTED by LoaderCDN service
Please contact me if you know any ways around :D

# Legal
This code is distributed under [MIT license]

Video extraction service is provided by [LoaderCDN @ 2017](https://loadercdn.io/). The code merely wraps it in Python and provides a downloading function through [requests](http://docs.python-requests.org/en/master/).

In particular,
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

> In case your use of the software forms the basis of copyright infringement, or you use the software for any other illegal purposes, the authors cannot take any responsibility for you.

# Acknowledgement
[LoaderCDN @ 2017](https://loadercdn.docs.apiary.io) for video extraction service.
[This blog](https://www.leavesongs.com/PYTHON/resume-download-from-break-point-tool-by-python.html) for continue-downloading code reference.
[soimort/you-get](https://github.com/soimort/you-get) for inspiration and Legal text.
