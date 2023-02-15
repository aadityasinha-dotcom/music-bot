from youtubesearchpython import VideosSearch
from pytube import YouTube

def download_song(url):
    if url is None:
        print("NONE")
        return
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4')
    streams.first().download()
    print(yt.title)

def search_song(user_input):
    return VideosSearch(user_input, limit = 1).result()

def get_link(result):
    return result['result'][0]['link']

def func(input):
    result = search_song(input)
    if result is not None:
        url = result['result'][0]['link']
        print("downloading your song....", end=" ")
        print(url)
        download_song(url)
    else:
        print("try again")

print(search_song("ghungroo")['result'][0])
# func("ghungroo")
