#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs4
import argparse
import os.path

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
group.add_argument("-v", "--verbose", action="store_true")

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
    tmp = requests.get(d_url)
    with open(os.path.join(args.output_path, name) + '.mp3', 'wb') as f:
        f.write(tmp.content)


def final(song,download_path):
    youtube_url = get_url_vid(song.replace(" ", "+"))
    mp3io_to_download = get_download_url(youtube_url)
    save_file(song, mp3io_to_download)
    songs_dict[song] = [youtube_url, mp3io_to_download]


youtube_results_url = "https://www.youtube.com/results"
mp3io_download_url = 'http://www.convertmp3.io/download/'
songs_dict = {}
args = parser.parse_args()


if args.output_path is not None:
    if os.path.isdir(args.output_path):
        pass
    else:
        os.makedirs(args.output_path)

if args.song_name is not None:
    final(args.song_name, args.output_path)
elif args.list_path is not None:
    if os.path.exists(args.list_path):
        songs_list = open(args.list_path, "r", encoding="utf8")
        for song in songs_list.read().split('\n'):
            final(song, args.output_path)
    else:
        print('list is not exists')

'''
songs_list = open('songs.txt', "r", encoding="utf8")
for song in songs_list.read().split('\n'):
    youtube_url = get_url_vid(song.replace(" ", "+"))
    mp3io_to_download = get_download_url(youtube_url)
    save_file(song, mp3io_to_download)
    songs_dict[song] = [youtube_url, mp3io_to_download]
    print("")
    print("****************************")
    print("finish with: "+song)
'''
