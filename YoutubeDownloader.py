#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs4
import base64


def save_html(html):
    with open("res.html", 'wb') as f:
        f.write(html)
    f.close()


def get_url_vid(name):
    search_results = requests.get(youtube_results_url, params={'search_query': name})
    html_doc = search_results.content
    save_html(html_doc)
    soup = bs4(html_doc, 'lxml')
    vid_id = soup.findAll("button", {"title": "Watch later"})[0].get("data-video-ids")
    print(vid_id.encode("utf-8"))
    return 'https://www.youtube.com/watch?v=' + vid_id


def base64_encode_url(plain_text_url):
    encoded_url = base64.b64encode(plain_text_url.encode('utf-8'))
    return encoded_url


#def download_mp3(convertor_url):
#    print()


songs_list = open('songs.txt', "r", encoding="utf8")
youtube_results_url = "https://www.youtube.com/results"
convertor_url = 'http://www.convertmp3.io/download/?video='

songs_dict = {}
for song in songs_list.read().split('\n'):
    youtube_url = get_url_vid(song.replace(" ", "+"))
    # base64_youtube_url=base64_encode_url(youtube_url).decode("utf-8")
    # songs_dict[song.strip('\n')]=[youtube_url,base64_youtube_url]
    songs_dict[song.strip('\n')] = [youtube_url]
