# A Python Port for loaderCDN.io

Download videos from video-hosting sites.

Example: bilibili.com (limited), youtube.com, vimeo.com

Supported formats: mp3, flv, mp4, ogg, avi, more

# Usage

*You must supply your loaderCDN api key with -k/--k. Get your key [here](https://loadercdn.io/)*

*required packages: python3, requests*

```bash
python3 lcdownloader.py [OPTIONS] -k apikey URLs

# to load a text file of urls: -I listfilfe

# to use custom header file: -H headers.txt URLs

# to overwrite existing files:: -f/--force

# select starting/end position within supplied listfile: -s/-e

# more options: -h/--help
```

header file format requirement:
```
Key: value,
Key: value,
Key: value

# key,value strings can be single/double quoted with `' or `"
# comma after value is not necessary but recommended
```

default behavior: downloading .mp3

&nbsp;

## logging options

    + /log/debug-lcddownloader.log
    + /log/warn-lcddownloader.log
old log files will be overwritten.

## dry-run option
if you wish to only extract information on videos, use `-u` or `-i` option. However, the downloadable links will only be available on LoaderCDN server for a limited time.

Inforamtion will also be saved as `titl-` prepended text files under `downloaded` directory.

## Resuming downloading not supported
this is due to that the LoaderCDN service uses youtube-dl for link resoluation and format transcoding in real-time. It does not download any content on its server. So it is impossible for it and for me to estimate the size of the file, nor to support resuming download.

# Unsupported sites
since link resolutoin is provided by loaderCDN by youtube-dl, the availability of supported sites completely depends on youtube-dl, and is likely to change in time.

i will try to update the unsupported site list here. you can also submit issues to help me with it.

`bilibili.com`: partially unsupported. muti-part videos do not resolve; .flv download not work. But you can still download other formats with single part videos.

`https://www.dplay.se`: audio cannot be found on videos hosted on this website.

# Complete list of options
```
A loaderCDN API port to python, default format: mp3

-h, --help            Print this help message and exit
-F FORMAT, --format FORMAT
                    specify downloading format
-f, --force           force overwrite existing file
-H HEADER_FILE, --headers HEADER_FILE
                    Load headers.txt
-I FILE, --input-file FILE
                    Read non-playlist URLs from FILE
-k KEY, --key KEY     supply loadercdn api key: string or key.txt
-s START, --start START
                    starting position of URLs list: 1-len(URLs)
-e END, --end END     end position of URLs list: 1-len(URLs)
-d, --debug           debug mode. Enables debug.log

Dry-run options:
(no actual downloading)

-i, --info            Print extracted information (headers)
-u, --url             Print extracted URLs (only)
```

&nbsp;

# Legal
The code is distributed under [MIT license](https://opensource.org/licenses/MIT)

The code only uses service provided by [LoaderCDN @ 2018](https://loadercdn.io/) and [youtube-dl](https://github.com/rg3/youtube-dl). It complies with all their copyright disclaimers and other copyright laws.

In particular,
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

> In case your use of the software forms the basis of copyright infringement, or you use the software for any other illegal purposes, the authors cannot take any responsibility for you.

# Acknowledgement
[LoaderCDN @ 2018](https://loadercdn.docs.apiary.io)

[This blog](https://www.leavesongs.com/PYTHON/resume-download-from-break-point-tool-by-python.html) for continue-downloading code reference.

[soimort/you-get](https://github.com/soimort/you-get) for inspiration and Legal text.

# Special Thanks
[LoaderCDN developer](mailto:contact@loadercdn.io) for many detailed discussions and inquiries.
