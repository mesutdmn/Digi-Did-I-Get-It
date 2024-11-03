import random

from google.api_core.exceptions import InternalServerError
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader,Docx2txtLoader,
    UnstructuredURLLoader, WikipediaLoader,
    EverNoteLoader, UnstructuredPowerPointLoader,
    YoutubeLoader,  UnstructuredEPubLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_search import YoutubeSearch
from utils import extract_youtube_id
from graph import HelperLLM
from moviepy.editor import VideoFileClip
import yt_dlp
import imageio_ffmpeg
import time
import os
import google.generativeai as genai
import requests
import base64
from parallel_llm import split_audio_parallel


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class Loaders:
    def __init__(self, data,data_type, loader_status):
        self.data = data
        self.data_type = data_type
        self.loader_status = loader_status
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        self.helper_llm = HelperLLM()
        self.answer = ""
        self.status = False

        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")
        self.big_model = genai.GenerativeModel(model_name="gemini-1.5-pro-002")

        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=5000, chunk_overlap=0)
        self.loaders = {
            "pdf": PyPDFLoader,
            "txt": TextLoader,
            "url": UnstructuredURLLoader,
            "wiki": WikipediaLoader,
            "enex": EverNoteLoader,
            "youtube": YoutubeLoader,
            "epub": UnstructuredEPubLoader,
            "pptx": UnstructuredPowerPointLoader,
            "docx": Docx2txtLoader,

        }

    def youtube_loader(self, video_id):
        way = "transcript"
        document = ""
        attempt = 0
        try:
            self.loader_status.info("🛠️ Extracting transcript from YouTube video is starting...")
            time.sleep(1)
            while (len(document) == 0) and (attempt < 3):
                attempt += 1
                self.loader_status.info(f"📌 Extracting transcript from YouTube video... Attempt: {attempt}")
                time.sleep(1)
                try:
                    transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
                    available_languages = [trans.language_code for trans in transcript_languages]

                    document = self.loaders["youtube"].from_youtube_url(
                        youtube_url=f"https://www.youtube.com/watch?v={video_id}",
                        add_video_info=False,
                        language=available_languages[0],
                    ).load()
                    self.loader_status.info("📑 Transcript extracted successfully.")
                    self.status = True
                except Exception as e:
                    self.loader_status.warning(f"🤯 Attempt {attempt} failed. Retrying...")
                    time.sleep(1)

            if len(document) == 0:  # If still no document after 3 attempts, switch to audio extraction
                self.loader_status.info("😢 Transcript extracting failed, but...")
                time.sleep(2)
                self.loader_status.info("💪 Trying to extract audio from YouTube video...")
                way = "audio"
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',
                    }],
                    'outtmpl': 'audio.%(ext)s',
                    'ffmpeg_location': ffmpeg_path,
                    'progress_hooks': [self.progress_hook],
                    'postprocessor_hooks': [self.post_progress_hook],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

                document = self.audio_loader("audio.mp3")
                self.loader_status.info("✅ Audio extracted successfully.")

        except Exception as e:
            self.loader_status.error(f"😢 An unexpected error occurred: {str(e)}")
            document = ""

        if way == "transcript":
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
        else:
            split_doc = self.text_splitter.split_text(document)

        return split_doc

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            file_name = d["filename"]
            percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
            emoji = random.choice(["🍗","🍖","🥩","🍦","🍞","🥧","🥂"])
            self.loader_status.info(f"{file_name} {emoji} Download progress: {percent:.2f}%")
        elif d['status'] == 'finished':
            file_name = d["filename"]
            time.sleep(1)
            self.loader_status.info(f"{file_name}, ✅ Download finished!")
            time.sleep(1)

    def post_progress_hook(self, d):
        if d['status'] == 'started':
            self.loader_status.info(f"⏳ Started {d["postprocessor"]}, this might take a while..")
            time.sleep(1)
        elif d['status'] == 'finished':
            self.loader_status.info(f"✅ Post-processing finished!")
            time.sleep(1)

    def audio_loader(self, path):
        self.loader_status.info("⏳ Extracting text from audio, this might take a while...")
        chunk_length = 60*60
        prompt = """
        Please provide a detailed text for the audio.
        No need to provide timelines.
        Do not make up any information that is not part of the audio and do not be verbose.
        """
        llm_s = {"flash":self.model, "pro":self.big_model}
        response = " ".join(split_audio_parallel(path, llm_s, chunk_length, self.loader_status, prompt))

        return response

    def mp4_loader(self):
        self.loader_status.info("🛠️ Extracting audio from video...")
        try:
            video = VideoFileClip(self.data)

            video.audio.write_audiofile("audio.mp3")

            self.loader_status.info(f"✅ Audio extracted successfully and saved to audio.mp3")
            response = self.audio_loader("audio.mp3")

        except Exception as e:
            print(f"An error occurred: {e}")
            self.loader_status.error("😢 Failed to extract audio from video.")
            response = " "
        time.sleep(1)
        return response

    def image_loader(self):
        self.loader_status.info("🛠️ Extracting text from image...")
        image_file = genai.upload_file(path=self.data)
        prompt = """
                You are a highly accurate text recognition assistant. Please extract all readable text from the image file provided. 
                Return only the text in a well-organized and clear format, preserving any distinct sections, titles, paragraphs, or lists. 
                Make sure to include all visible text without omitting any details. 
                If any text is hard to read, make your best effort to transcribe it accurately. 
                Respond only with the extracted text, without adding additional explanations.
                """
        try:
            response = self.model.generate_content([image_file, prompt])
            text_response = response.text  # Access the text property if response is valid
            self.loader_status.info("✅ Text extracted successfully!")
            self.status = True

        except InternalServerError as e:
            print("An error occurred: ", e)
            self.loader_status.info("🤯 An error occurred, triggering the big model...")
            response = self.big_model.generate_content([image_file, prompt])
            text_response = response.text
            self.loader_status.info("🎉 Text extracted successfully with bigger model!")
        except Exception as e:
            print("Failed to retrieve text from response:", e)
            self.loader_status.error("😢 Failed to extract text from image.")
            text_response = " "
        time.sleep(1)
        return text_response

    def get_access_token(self, client_id, client_secret):
        auth_url = 'https://accounts.spotify.com/api/token'
        auth_header = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode("ascii")

        headers = {
            "Authorization": f"Basic {auth_header}"
        }

        data = {
            "grant_type": "client_credentials"
        }

        response = requests.post(auth_url, headers=headers, data=data)
        return response.json().get("access_token")

    def get_podcast_title(self,episode_id, access_token):
        url = f"https://api.spotify.com/v1/episodes/{episode_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get("name")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def spotify_loader(self):
        self.loader_status.info("🛠️ Extracting data from Spotify...")
        access_token = self.get_access_token(self.spotify_client_id, self.spotify_client_secret)
        episode_id = self.data.split("/")[-1]
        title = self.get_podcast_title(episode_id, access_token)
        self.loader_status.info(f"🔎 Podcast title: {title}")
        time.sleep(1)

        if title is None:
            self.loader_status.error("😓 Failed to extract podcast title, be sure it has a valid Spotify 'episode' URL.")
            self.status = False
            return None
        else:
            video_id = YoutubeSearch(f"{title}", max_results=1).to_dict()[0]["id"]
            video_title = YoutubeSearch(f"{title}", max_results=1).to_dict()[0]["title"]
            question = f"""{title} and {video_title} same content?"""
            self.answer = self.helper_llm.ask_llm(question)
            if self.answer:
                self.status = True

                return video_id
            else:
                self.loader_status.error("😓 Failed to find a suitable audio-text for the podcast.")
                video_id = None
                self.status = False

                return video_id

    def other_loader(self):
        self.loader_status.info("🛠️ Extracting data from other sources...")
        document = self.loaders[self.data_type](self.data).load()
        split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
        self.loader_status.info(f"✅ {str(self.data_type).upper()} file loaded successfully")
        self.status = True
        return split_doc


    def set_loaders(self):
        if self.data_type=="wiki":
            if self.helper_llm.ask_llm(f"Is this something searchable on Wikipedia?\n{self.data}"):
                try:
                    self.loader_status.info("🛠️ Extracting data from Wikipedia...")
                    document = self.loaders[self.data_type](self.data, load_max_docs=2).load()
                    split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
                    self.loader_status.info("✅ Wikipedia page loaded successfully")
                    time.sleep(1)
                    self.status=True
                except Exception as e:
                    self.loader_status.error("😓 Failed to load Wikipedia page.")
                    split_doc = " "
            else:
                self.loader_status.error("❌ That is not something searchable on Wikipedia.")
                split_doc = " "

        elif self.data_type=="youtube":
            if self.helper_llm.ask_llm(f"Is this a YouTube link?\n{self.data}"):
                try:
                    video_id = extract_youtube_id(self.data)
                    split_doc = self.youtube_loader(video_id)
                    time.sleep(1)
                    self.loader_status.info("🤖 Sending Data to the Model...")
                    self.status = True
                except Exception as e:
                    self.loader_status.error("😓 Failed to load YouTube video.")
                    split_doc = " "
            else:
                self.loader_status.error("❌ That is not a YouTube link.")
                split_doc = " "

        elif self.data_type=="audio":
            try:
                document = self.audio_loader(self.data)
                split_doc = self.text_splitter.split_text(document)
                time.sleep(1)
            except Exception as e:
                self.loader_status.error("😓 Failed to load audio file.")
                split_doc = " "

        elif self.data_type=="text":
            try:
                self.loader_status.info("🛠️ Loading text file...")
                time.sleep(1)
                self.loader_status.info("✅ Text file loaded successfully")
                split_doc = self.text_splitter.split_text(self.data)

                time.sleep(1)

                self.loader_status.info("✅ Text file split successfully")
                self.status = True
            except Exception as e:
                self.loader_status.error("😓 Failed to load text file.")
                split_doc = " "

        elif self.data_type=="mp4":
            try:
                document = self.mp4_loader()
                split_doc = self.text_splitter.split_text(document)
                time.sleep(1)
            except Exception as e:
                self.loader_status.error("😓 Failed to load video file.")
                split_doc = " "

        elif self.data_type=="image":
            try:
                document = self.image_loader()
                split_doc = self.text_splitter.split_text(document)
                time.sleep(1)
            except Exception as e:
                self.loader_status.error("😓 Failed to load image file.")
                split_doc = " "

        elif self.data_type=="spotify":
            if self.helper_llm.ask_llm(f"Is this a Spotify podcast link?\n{self.data}"):
                try:
                    video_id = self.spotify_loader()
                    if self.status:
                        split_doc = self.youtube_loader(video_id)
                    else:
                        split_doc = " "
                except Exception as e:
                    self.loader_status.error("😓 Failed to load Spotify podcast.")
                    split_doc = " "
            else:
                self.loader_status.error("❌ That is not a Spotify podcast link.")
                split_doc = " "
        else:
            try:
                split_doc = self.other_loader()
            except Exception as e:
                self.loader_status.error("😓 Failed to load file.")
                split_doc = " "

        time.sleep(1)
        if self.status:
            self.loader_status.info("🤖 Sending Data to the Model...")
        return split_doc

