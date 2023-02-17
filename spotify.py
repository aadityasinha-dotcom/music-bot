from pydub import AudioSegment
from youtubesearchpython import VideosSearch
from pytube import YouTube

def download_song(url):
    if url is None:
        print("NONE")
        return
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4')
    final = streams.first().download()
    print(yt.title)
    # print("streams = "+final)
    # return yt.title
    return final

def search_song(user_input):
    return VideosSearch(user_input, limit = 1).result()

def get_link(result):
    return result['result'][0]['link']

def convert(path: str):
    index = 0
    for i in range(len(path)-1,-1,-1):
        if path[i]=='/':
            index = i+1
            break
    path = path[index:]
    print("path = "+path)
    mp4_file = AudioSegment.from_file(
            path,
            format="mp4")
    mp3_file = mp4_file.export(f"{path}.mp3", format="mp3")
    print("converted")
    return f"{path}.mp3"

def func(input):
    result = search_song(input)
    if result is not None:
        url = result['result'][0]['link']
        print("downloading your song....", end=" ")
        print(url)
        return download_song(url)
    else:
        print("try again")

print(search_song("ghungroo"))
# path = func("ghungroo")
# print(convert(path))
