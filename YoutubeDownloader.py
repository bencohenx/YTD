#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs4
import argparse
import os.path
import sys

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
    soup = bs4(html_doc, 'lxml')
    vid_id = soup.findAll("button", {"title": "Watch later"})[0].get("data-video-ids")
    return 'https://www.youtube.com/watch?v=' + vid_id


def get_download_url(yb_url):
    mp3_results = requests.get(mp3io_download_url, params={'video': yb_url})
    html_doc = mp3_results.content
    # save_html_mp3io(html_doc)
    soup = bs4(html_doc, 'lxml')
    href_id = soup.findAll('a', {"id": "download"})[0].get("href")
    return 'http://www.convertmp3.io' + href_id


def save_file(name, d_url):
    with open(os.path.join(args.output_path, name) + '.mp3', 'wb') as f:
        response = requests.get(d_url, stream=True)
        if args.quiet:
            f.write(response.content)
        else:
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                f.write(response.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
                print('\n')


def final(song_name, song_id_list, list_amount):
    if args.quiet:
        print('Download: '+song_name)
    else:
        print("Start download "+str(song_id_list)+"/"+str(list_amount)+": " + song_name)
    youtube_url = get_url_vid(song_name.replace(" ", "+"))
    mp3io_to_download = get_download_url(youtube_url)
    save_file(song_name, mp3io_to_download)
    songs_dict[song_name] = [youtube_url, mp3io_to_download]


youtube_results_url = "https://www.youtube.com/results"
mp3io_download_url = 'http://www.convertmp3.io/download/'
songs_dict = {}
args = parser.parse_args()

print("Running '{}'\n".format(__file__))

if args.output_path is not None:
    if os.path.isdir(args.output_path):
        pass
    else:
        os.makedirs(args.output_path)

if args.song_name is not None:
    final(args.song_name, '1', '1')
elif args.list_path is not None:
    if os.path.exists(args.list_path):  # works on songs list
        with open(args.list_path, "r", encoding="utf8") as f:
            songs_list = f.read().split('\n')
        i = 1
        amount = len(songs_list)
        for song in songs_list:
            final(song, i, amount)
            i = i + 1
    else:
        print('''
              *** Wrong path list.. ***
              ''')
else:
    print('''
    *****************************************
    ***  Bad Args, try the help, --help   ***
    *****************************************
    ''')
