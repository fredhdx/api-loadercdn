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
import json
import logging
import argparse
import subprocess
from glob import glob
from logging import config
from subprocess import PIPE
from datetime import datetime
supported_format = ['mp3','ogg','mp4','mkv','m4a','wma','wmv','avi']

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_meta_from_file(mfile):
    global logger
    logger.debug("read_meta_from_file")
    meta = {'title':'','artist':'','album':'','creation_time':'','comment':'', 'year':''}
    if os.path.isfile(mfile):
        with open(mfile) as f:
            lines = f.readlines()

            main = lines[0].strip() # 【SNH48】Team X 《梦想的旗帜》第四十九场 全场 cut (20170328) (2)
            sub = lines[1].strip() # MC1:最爱吃的失误
            # url = lines[2].strip() # url

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
            meta['year'] = str(date[:4])
            meta['comment'] = date
            if sub:
                sub = sub.split('：')[-1].strip() # MC：去掉
                meta['title'] = date + ' ' + chang + ' ' + sub
            else:
                meta['title'] = "《梦想的旗帜》" + chang + ' ' + date
            # meta['copyright'] = 'SNH48'
        f.close()
    return meta

def encode_ffmpeg(inputfile,outputfile,meta=None):
    global logger
    if inputfile and inputfile != outputfile:
        logger.debug("encode ffmpeg %s",os.path.basename(inputfile))
        command = ['ffmpeg', '-i', '%s' % inputfile]
        if meta is not None:
            logger.debug(str(meta))
            meta_part = []
            for key,value in meta.items():
                part = ['-metadata']
                part.extend(["%s=%s" % (key, value)])
                meta_part.extend(part)
            command.extend(meta_part)
        command.extend(['-loglevel','info'])
        command.extend(['-y','-hide_banner', '%s' % outputfile])
        logger.info(" ".join(command))

        try:
            proc = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
            errs = ""
            for line in iter(proc.stderr.readline, b''):
                line = line.decode('utf-8').rstrip()
                errs += line
                # logger.info(">>> " + line)
            outs, _errs = proc.communicate()
            outs = outs.decode('utf-8')
            errs = errs + '\n' + _errs.decode('utf-8')
            logger.debug("ffmpeg out: %s", outs)
            if errs:
                logger.warning("ffmpeg warning: %s",errs)
            else:
                logger.debug("ffmpeg stdout: %s\nffmpeg stderr: %s",outs, errs)
            logger.info("ffmpeg encode success")
        except FileNotFoundError:
            logger.exception("encode_ffmpeg")
            logger.exception("ffmpeg: input file not found. continue")
        except subprocess.SubprocessError as e:
            logger.exception("encode_ffmpeg")
            logger.exception("ffmpeg: failed %s",e)

def writemeta_ffmpeg(inputfile,meta, outputfile=""):
    global logger
    logger.debug("ffmpeg: writemeta only %s",os.path.basename(inputfile))
    if not meta:
        logger.info("No meta data")
        return
    logger.debug(str(meta))

    if not outputfile or inputfile == outputfile:
        _filename,_ext = inputfile.split(os.path.sep)[-1].split('.')
        writefile = os.path.sep.join(inputfile.split(os.path.sep)[:-1]) + os.path.sep + _filename + "-tmp." + _ext
    else:
        writefile = outputfile
    logger.debug("%s >> %s",inputfile,writefile)

    command = ['ffmpeg', '-i', '%s' % inputfile]
    meta_part = []
    for key,value in meta.items():
        part = ['-metadata']
        part.extend(["%s=%s" % (key, value)])
        meta_part.extend(part)
    command.extend(meta_part)
    command.extend(['-loglevel','warning'])
    command.extend(['-c','copy','-y','-hide_banner', '%s' % writefile])

    logger.info(" ".join(command))

    try:
        # call ffmpeg
        proc = subprocess.Popen(command, stdout=PIPE, stderr=PIPE)
        errs = ""
        for line in iter(proc.stderr.readline, b''):
            line = line.decode('utf-8').rstrip()
            errs += line
            # logger.info(">>> " + line)
        outs, _errs = proc.communicate()
        outs = outs.decode('utf-8')
        errs = errs + '\n' + _errs.decode('utf-8')
        logger.debug("ffmpeg out: %s", outs)
        if errs:
            logger.warning("ffmpeg warning: %s",errs)
        else:
            logger.debug("ffmpeg errs: %s", errs)
        logger.info("ffmpeg meta success")
        if not outputfile or inputfile == outputfile :
            try:
                os.replace(writefile,inputfile)
            except PermissionError:
                logger.exception("writemeta_ffmpeg")
                logger.exception("Write permission denied: Please check filesystem permission.\nExit.")
                sys.exit(1)
            except IsADirectoryError:
                logger.exception("writemeta_ffmpeg")
                logger.exception("Is directory. Continue")
            except OSError as e:
                logger.exception("writemeta_ffmpeg")
                logger.exception(e)
    except FileNotFoundError:
        logger.exception("writemeta_ffmpeg")
        logger.exception("ffmpeg: input file not found. continue")
    except subprocess.SubprocessError as e:
        logger.exception("writemeta_ffmpeg")
        logger.exception("ffmpeg: failed %s",e)

def run_folders(working_dir, overwrite=False, metaonly=True, encodeonly=False, iformat="", oformat=""):
    global logger
    if working_dir and os.path.isdir(working_dir):
        video_list = [x[:-1] for x in glob(working_dir + "/*/")]
        count = 1
        for video in video_list:
            logger.info("Dir: %s", video)
            logger.info("PROCESSING %d/%d", count, len(video_list))
            info_file = video + os.path.sep + "info.log"
            media_files = [x for x in glob(video + "/*") if os.path.isfile(x)]

            global supported_format
            all_formats = [iformat] if iformat else supported_format
            media_files = [x for x in media_files if x.split(os.path.sep)[-1].split('.')[-1] in all_formats]

            for inputfile in media_files:
                meta = read_meta_from_file(info_file) if not encodeonly else {}
                basename, ext = inputfile.split(os.path.sep)[-1].split('.')

                if metaonly and meta:
                    writemeta_ffmpeg(inputfile, meta)
                elif not metaonly and ext!= oformat:
                    outputfile = (os.path.sep.join(inputfile.split(os.path.sep)[:-1])
                        + os.path.sep + basename + '.' + oformat)
                    file_exist = os.path.isfile(outputfile)
                    logger.debug("File exist? %s", str(file_exist))
                    if (not file_exist) or (file_exist and overwrite):
                        if encodeonly:
                            encode_ffmpeg(inputfile,outputfile)
                        else:
                            encode_ffmpeg(inputfile,outputfile,meta)

                # import json
                # logger.info(json.dumps(meta,indent=4,ensure_ascii=False,sort_keys=True))
            count += 1


def main():
    parser = argparse.ArgumentParser(
        prog='process meta and encoding',
        usage='meta-transcode [OPTION] working_dir',
        description='default: mode="meta" overwrite=False',
        add_help=False,
    )
    parser.add_argument(
        '-h', '--help', action='store_true',
        help='logger.info this help message and exit'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='debug mode. Enables debug.log'
    )
    encode_grp = parser.add_argument_group(
        'Encoding options', '(convert formats)'
    )
    encode_grp = encode_grp.add_mutually_exclusive_group()
    encode_grp.add_argument(
        '-c', '--encode', action='store_true', help='Encode with meta change'
    )
    encode_grp.add_argument(
        '-C', '--encodeonly', action='store_true',
        help='Encode without meta change'
    )
    parser.add_argument(
        '-o', '--oformat', type=str, default="",
        help='output format'
    )
    parser.add_argument(
        '-i', '--iformat', type=str, default="",
        help='input format'
    )
    parser.add_argument(
        '-f', '--force', action='store_true',
        help='input format'
    )
    parser.add_argument('dirs', nargs='*', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        sys.exit()

    working_dirs = []
    working_dirs.extend(args.dirs)

    if not working_dirs:
        print("Please enter at least 1 working_dir")
        parser.print_help()
        sys.exit()

    # default configuration
    metaonly = True
    encodeonly = False
    overwrite = False
    iformat = ""
    oformat = ""
    global supported_format

    if args.encodeonly:
        metaonly = False
        encodeonly = True
    elif args.encode:
        metaonly = False

    if args.force:
        overwrite = True

    iformat = args.iformat if args.iformat else iformat
    oformat = args.oformat if args.oformat else oformat

    if not metaonly and not oformat:
        print("encode mode requires output format")
        parser.print_help()
        sys.exit()

    print(working_dirs)
    input("You are going to rewrite your files. CAUTION!\nPress anykey to continue.")

    # Logging
    global logger
    if args.debug:
        logger = logging.getLogger("debug_logger")
        logger.info("debugging mode")
    else:
        logger = logging.getLogger()

    logger.debug("Python ffmpeg metadata encode batch processor")
    logger.info("date-time: %s", datetime.now().strftime('%Y-%m-%d-%H-%M'))
    logger.debug("Supported format: %s",str(supported_format))
    logger.debug("Options: ")
    logger.debug("meta: %s, encodeonly: %s, overwrite: %s, iformat: %s, oformat: %s"
            ,str(metaonly), str(encodeonly), str(overwrite), iformat, oformat)

    for working_dir in working_dirs:
        logger.info("Parent_dir: %s\n",working_dir)
        # working_dir = os.path.abspath(working_dir)
        run_folders(working_dir, overwrite=overwrite, metaonly=metaonly,
                encodeonly=encodeonly, iformat=iformat,oformat=oformat)

    logger.info("Clean/Done!")

if __name__ == '__main__':

    if os.path.isfile("logging.json"):
        with open("logging.json", "r", encoding="utf-8") as fd:
            config = json.load(fd)
            log_dir = os.getcwd() + os.path.sep + "log"
            if not os.path.isdir(log_dir):
                os.makedirs(log_dir)
            config['handlers']['file_handler']['filename'] = (log_dir + os.path.sep + "debug-"
                                + os.path.basename(__file__).split('.')[0]) + ".log"
            config['handlers']['warn_handler']['filename'] = (log_dir + os.path.sep + "warn-"
                                + os.path.basename(__file__).split('.')[0]) + ".log"
            logging.config.dictConfig(config)

    main()
