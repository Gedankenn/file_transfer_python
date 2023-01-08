from pytube import YouTube
import os
from pathlib import Path

def yt2mp3(url,outdir):
    yt = YouTube(url)

    video = yt.streams.filter(abr='160kbps').last()

    out_file = video.download(output_path=outdir)
    base, ext = os.path.splitext(out_file)
    new_file = Path(f'{base}.wav')
    os.rename(out_file,new_file)

    if new_file.exists():
        print(f'{yt.title} has been downloaded')
    else:
        print(f'ERROR: ')

url = input("link of video")
save = 'C:\\Users\\gedan\\Downloads'
yt2mp3(url,save)