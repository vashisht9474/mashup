import re
import streamlit as st
import os
import requests
from pytube import YouTube
from moviepy.editor import VideoFileClip, concatenate_audioclips
from moviepy.audio.io.AudioFileClip import AudioFileClip
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from pydub.audio_segment import AudioSegment
st.set_page_config(layout="wide")

video_html = """
		<style>

		#myVideo {
		  position: fixed;
		  right: 0;
		  bottom: 0;
		  min-width: 100%; 
		  min-height: 100%;
		}

		.content {
		  position: fixed;
		  bottom: 0;
		  background: rgba(0, 0, 0, 0.5);
		  color: #f1f1f1;
		  width: 100%;
		  padding: 20px;
		}

		</style>	
		<video autoplay muted loop id="myVideo">
		  <source src="https://player.vimeo.com/external/347024098.hd.mp4?s=39da73487285e2c9f2009ae34fd55a005d015351&profile_id=174")>
		  Your browser does not support HTML5 video.
		</video>
        """

st.markdown(video_html, unsafe_allow_html=True)


def search_video(artist_name):
    query = artist_name + " song"
    query = query.replace(" ", "+")
    url = "https://www.youtube.com/results?search_query=" + query
    response = requests.get(url)
    html = response.text
    videos = re.findall(r"watch\?v=(\S{11})", html)
    return ["https://www.youtube.com/watch?v=" + video for video in videos[:10]]
download_dir = "videos"
audio_download_dir = "audio"
output_file="output"
def download_video(url, artist_name):
    yt = YouTube(url)
    title = yt.title
    if artist_name.lower() in title.lower():
        stream = yt.streams.first()
        stream.download(download_dir)
        print(f"{title} by {artist_name} has been downloaded.")
    else:
        print(f"The video {title} is not by {artist_name}.")
st.title("Welcome To MASHUP")
artist_name = st.text_input("Enter Artist Name")
urls = search_video(artist_name)
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
col1, col2, col3 = st.columns([1,1,1])
with col1:
    if(st.button("Download Video")):
        for url in urls:
            download_video(url, artist_name)
    



video_files = [f for f in os.listdir(download_dir)]
if not os.path.exists(audio_download_dir):
    os.makedirs(audio_download_dir)
with col2:
    if(st.button("Convert To Audio")):
        for video_file in video_files:
            video = VideoFileClip(os.path.join(download_dir, video_file))
            audio = video.audio
            audio_file = os.path.splitext(video_file)[0] + ".mp3"
            audio.write_audiofile(os.path.join(audio_download_dir, audio_file))
    
if not os.path.exists(output_file):
    os.makedirs(output_file)

with col3:    
    if(st.button("Merge")):
        audio_files = [f for f in os.listdir(audio_download_dir)]
        clips = [AudioFileClip(os.path.join(audio_download_dir, audio_file)) for audio_file in audio_files]
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(os.path.join(output_file, "final.mp3"))


col1, col2, col3 = st.columns([1,1,1])



def send_email(email, password, to, subject, message, file):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    attachment = open(file, "rb")

    payload = MIMEBase('application', 'octet-stream')
    payload.set_payload((attachment).read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=file)
    msg.attach(payload)

    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.starttls()
    smtp.login(email, password)
    smtp.sendmail(email, to, msg.as_string())
    smtp.quit()
    print("Email sent!")

email = "vashishtv2002@gmail.com"
password = "rwnwmyzknvwjauhr"

subject = "Mashup Output File"
message = "Attached is the mashup output file you requested."
file = os.path.join(output_file, "final.mp3")


rer=st.text_input("enter recievers mail")
    
to = rer

if(st.button("Send Email")):
    send_email(email, password, to, subject, message, file)
