#!/usr/bin/python3
import requests
from ctypes import *
from bs4 import BeautifulSoup as bs4
import argparse
import os.path
import os
from datetime import datetime
import concurrent.futures
from queue import Queue
import threading
import msvcrt


class _CursorInfo(Structure):
    _fields_ = [("size", c_int),
                ("visible", c_byte)]


class COORD(Structure):
    _fields_ = [("x", c_short), ("y", c_short)]


parser = argparse.ArgumentParser(description='''
__   __             _           _                                
\ \ / /            | |         | |                               
 \ V / ___   _   _ | |_  _   _ | |__    ___                      
  \ / / _ \ | | | || __|| | | || '_ \  / _ \                     
  | || (_) || |_| || |_ | |_| || |_) ||  __/                     
  \_/ \___/  \__,_| \__| \__,_||_.__/  \___|                     
______                        _                    _             
|  _  \                      | |                  | |            
| | | | ___ __      __ _ __  | |  ___    __ _   __| |  ___  _ __ 
| | | |/ _ \\\ \ /\ / /| '_ \ | | / _ \  / _` | / _` | / _ \| '__|
| |/ /| (_) |\ V  V / | | | || || (_) || (_| || (_| ||  __/| |   
|___/  \___/  \_/\_/  |_| |_||_| \___/  \__,_| \__,_| \___||_|   

v 0.1.0
''', formatter_class=argparse.RawTextHelpFormatter)

group = parser.add_mutually_exclusive_group()
parser.add_argument('-s', "--song-name")
parser.add_argument('-l', '--list-path')
parser.add_argument('-o', '--output-path', default="YoutubeDownloaderAudio")
group.add_argument("-q", "--quiet", action="store_true")
parser.add_argument('-w', "--worker-threads", default=3, type=int)


def save_html_youtube(html):
    with open("youtuberesult.html", 'wb') as f:
        f.write(html)
    f.close()


def save_html_mp3io(html):
    with open("mp3ioreslt.html", 'wb') as f:
        f.write(html)
    f.close()


def get_url_vid(name):
    search_results = requests.get(youtube_results_url, params={'search_query': name})
    html_doc = search_results.content
    # save_html_youtube(html_doc)
    soup = bs4(html_doc.decode('utf-8', 'ignore'), "lxml")
    vid_id = soup.findAll("button", {"title": "Watch later"})[0].get("data-video-ids")
    return 'https://www.youtube.com/watch?v=' + vid_id


def get_download_url(yb_url):
    mp3_results = requests.get(mp3io_download_url, params={'video': yb_url})
    html_doc = mp3_results.content
    # save_html_mp3io(html_doc)
    soup = bs4(html_doc, 'lxml')
    href_id = soup.findAll('a', {"id": "download"})[0].get("href")
    return 'http://www.convertmp3.io' + href_id


def save_file(song_id, name, d_url):
    with open(os.path.join(args.output_path, name) + '.mp3', 'wb') as f:
        response = requests.get(d_url, stream=True)
        if args.quiet:
            f.write(response.content)
        else:
            total_length = response.headers.get('content-length')
            if total_length is None:
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    if stop:
                        return
                    dl += len(data)
                    f.write(data)
                    done = (dl / total_length) * 50
                    print_queue.put((song_id * 5 + 3, "[%s%s]" % ('=' * int(done), ' ' * (50 - int(done)))))


def merger(song_id_list, song_name):
    if stop:
        return
    if args.quiet:
        print('Downloading: ' + song_name)
    else:
        print_queue.put((song_id_list * 5,
                         datetime.now().strftime('%H:%M:%S') + " Starting download - " + str(
                             song_id_list + 1) + "/" + str(
                             amount)
                         + ": " + song_name))
    youtube_url = get_url_vid(song_name.replace(" ", "+"))
    if args.quiet is False:
        print_queue.put((song_id_list * 5 + 1, 'Getting the youtube URL: ' + youtube_url))
    mp3io_to_download = get_download_url(youtube_url)
    if args.quiet is False:
        print_queue.put((song_id_list * 5 + 2, 'Getting the mp3io URL: ' + mp3io_to_download))
    save_file(song_id_list, song_name, mp3io_to_download)


def printer():
    h = windll.kernel32.GetStdHandle(-11)
    ci = _CursorInfo()
    windll.kernel32.GetConsoleCursorInfo(h, byref(ci))
    ci.visible = False  # hide cmd cursor
    windll.kernel32.SetConsoleCursorInfo(h, byref(ci))
    offset = 3
    for y, st in iter(print_queue.get, None):
        windll.kernel32.SetConsoleCursorPosition(h, COORD(0, offset + y))
        print(st)
        print_queue.task_done()
    if args.quiet:
        windll.kernel32.SetConsoleCursorPosition(h, COORD(0, offset + amount + 1))
    else:
        windll.kernel32.SetConsoleCursorPosition(h, COORD(0, offset + amount * 5 + 1))
    if stop is False:
        print("YoutubeDownloader done at: " + datetime.now().strftime('%H:%M:%S'))
    windll.kernel32.GetConsoleCursorInfo(h, byref(ci))
    ci.visible = True  # visible cmd cursor
    windll.kernel32.SetConsoleCursorInfo(h, byref(ci))


def stop_by_user():
    global stop
    if msvcrt.getch() == b'\x03':
        stop = True
    print_queue.put((amount*5, "Stopped by user"))


youtube_results_url = "https://www.youtube.com/results"
mp3io_download_url = 'http://www.convertmp3.io/download/'
args = parser.parse_args()
print_queue = Queue()
amount = 1
stop = False

os.system('cls')
os.system('mode 800')
print("Running '{}'\n"
      "Worker threads are: {}".format(__file__, args.worker_threads))

print_thread = threading.Thread(target=printer)
stop_thread = threading.Thread(target=stop_by_user)
stop_thread.daemon = True
print_thread.start()
stop_thread.start()

if args.output_path is not None:
    if os.path.isdir(args.output_path):
        pass
    else:
        os.makedirs(args.output_path)


if args.song_name is not None:
    merger(0, args.song_name)
elif args.list_path is not None:
    if os.path.exists(args.list_path):  # works on songs list
        with open(args.list_path, "r", encoding="utf8") as f:
            songs_list = set(f.read().split('\n'))  # unique list
        amount = len(songs_list)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.worker_threads) as executor:
            executor.map(merger, range(0, amount), songs_list)
    else:
        print('''
              *** Wrong path list.. ***
              ''')
else:
    print('''
    *****************************************
    ***  Bad Args, try to run --help   ***
    *****************************************
    ''')

print_queue.put(None)