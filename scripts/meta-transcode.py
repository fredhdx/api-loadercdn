"""
Assuming file structure: /downloaded/title/title.mp3
Read metadata from info.log in each media folder
Use ffmpeg to rewrite meta information and (optional) convert formats
! important: file overwritten enabled. delete "-y" option from ffmpeg command to enable prompt per case

feed parent downloading directory
edit read_meta_from_file to specify meta processing case-by-case
run !
"""
import os
import re
import sys
from glob import glob
from datetime import datetime
supported_format = ['mp3','ogg','mp4','mkv','m4a','wma','wmv','avi']

def read_meta_from_file(mfile):
    meta = {'title':'','artist':'','album':'','creation_time':'','comment':'', 'year':''}
    if os.path.isfile(mfile):
        with open(mfile) as f:
            lines = f.readlines()

            main = lines[0].strip() # 【SNH48】Team X 《梦想的旗帜》第四十九场 全场 cut (20170328) (2)
            sub = lines[1].strip() # MC1:最爱吃的失误
            url = lines[2].strip() # url

            if re.search(r'\d{8}|\d{7}|\d{6}',main):
                date = re.search(r'\d{8}|\d{7}|\d{6}',main).group(0)
            else:
                date = datetime.now().strftime('%Y%m%d')

            if len(date) == 6: # 170320
                date = "20" + date
            if len(date) == 7: #2017320
                date = date[:4] + '0' + date[4:]

            if re.search(r'第[^\s]*场',main):
                chang = re.search(r'第[^\s]*场',main).group(0)
            else:
                chang = ''

            meta['artist'] = "SNH48-Team X"
            meta['album'] = "【TeamX】《梦想的旗帜》MC合集"
            meta['creation_time'] = date
            meta['year'] = str(date[:4])
            meta['comment'] = ''
            if sub:
                sub = sub.split('：')[-1].strip() # MC：去掉
                meta['title'] = date + ' ' + chang + ' ' + sub
            else:
                meta['title'] = "《梦想的旗帜》" + chang + ' ' + date
            # meta['copyright'] = 'SNH48'

        f.close()

    return meta

def transcode_ffmpeg(ifile,parent_dir, meta, oformat, overwrite=False):
    if not meta:
        meta = {'title':'','artist':'','album':'','creation_time':'','comment':'', 'year':''}
        print("empty meta")

    if not oformat:
        oformat = ifile.split('.')[-1]

    try:
        outputfile = parent_dir + os.path.sep + ifile.split(os.path.sep)[-1].split('.')[0] + "." + oformat
        if os.path.isfile(outputfile) and not overwrite:
            return
        command = ("ffmpeg -i \"" + ifile + "\""
                + " -metadata title=\"" + meta['title']  + "\""
                + " -metadata artist=\"" + meta['artist'] + "\""
                + " -metadata album=\"" + meta['album'] + "\""
                + " -metadata year=\"" + meta['year'] + "\""
                + " -metadata comment=\"" + meta['creation_time'] + "\""
                + " -y \""
                + outputfile + "\""
                )
        os.system(command)
    except Exception as e:
        print(e)
        sys.exit(1)

def run_folders(working_dir, oformat="mp3", overwrite=False):
    # working_dir = os.getcwd() + os.path.sep + "downloaded"
    video_list = [x[:-1] for x in glob(working_dir + "/*/")]
    count = 1
    for video in video_list:
        print("PROCESSING %d/%d" % (count,len(video_list)))
        """
        current level: video == /downloaded/video/
        """
        info_file = video + os.path.sep + "info.log"
        media_files = [x for x in glob(video + "/*") if os.path.isfile(x)]
        media_files = [x for x in media_files if x.split('.')[-1] in supported_format]

        for _file in media_files:
            meta = read_meta_from_file(info_file)
            # import json
            # print(json.dumps(meta,indent=4,ensure_ascii=False,sort_keys=True))
            transcode_ffmpeg(_file, video, meta, oformat, overwrite)

        count += 1

# index = [1:]
def get_dirname_by_index(working_dir, position):
    video_list = [x[:-1] for x in glob(working_dir + "/*/")]
    return video_list[position-1]

def main():
    # working_dir = os.getcwd() + os.path.sep + "downloaded"
    if len(sys.argv) != 2:
        print("no working dir.\n only 1 arg allowed")
        sys.exit()
    else:
        working_dir = sys.argv[1]
    run_folders(working_dir, "mp3", overwrite=False)
    print("Clean/Done!")

if __name__ == '__main__':
    main()
