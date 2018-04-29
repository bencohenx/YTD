#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs4
import base64


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
    save_html_youtube(html_doc)
    soup = bs4(html_doc, 'lxml')
    vid_id = soup.findAll("button", {"title": "Watch later"})[0].get("data-video-ids")
    return 'https://www.youtube.com/watch?v=' + vid_id


def download_mp3(yb_url):
    mp3_results = requests.get(mp3io_download_url, params={'video': yb_url})
    html_doc = mp3_results.content
    save_html_mp3io(html_doc)
    soup = bs4(html_doc, 'lxml')
    href_id = soup.findAll('a', {"id": "download"})[0].get("href")
    return 'http://www.convertmp3.io' + href_id


songs_list = open('songs.txt', "r", encoding="utf8")
youtube_results_url = "https://www.youtube.com/results"
mp3io_download_url = 'http://www.convertmp3.io/download/'

songs_dict = {}
for song in songs_list.read().split('\n'):
    youtube_url = get_url_vid(song.replace(" ", "+"))
    mp3io_to_download = download_mp3(youtube_url)
    songs_dict[song] = [youtube_url,mp3io_to_download]

print(songs_dict)