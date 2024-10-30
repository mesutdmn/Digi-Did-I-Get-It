from google.api_core.exceptions import InternalServerError
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader,Docx2txtLoader,
    WebBaseLoader, WikipediaLoader,
    EverNoteLoader, UnstructuredPowerPointLoader,
    YoutubeLoader,  UnstructuredEPubLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from utils import extract_youtube_id
from moviepy.editor import VideoFileClip
import yt_dlp
import imageio_ffmpeg as ffmpeg
import time
import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class Loaders:
    def __init__(self, data,data_type, loader_status):
        self.data = data
        self.data_type = data_type
        self.loader_status = loader_status
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash-002")
        self.big_model = genai.GenerativeModel(model_name="gemini-1.5-pro-002")

        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=10000, chunk_overlap=0)
        self.loaders = {
            "pdf": PyPDFLoader,
            "txt": TextLoader,
            "url": WebBaseLoader,
            "wiki": WikipediaLoader,
            "enex": EverNoteLoader,
            "youtube": YoutubeLoader,
            "epub": UnstructuredEPubLoader,
            "pptx": UnstructuredPowerPointLoader,
            "docx": Docx2txtLoader,

        }

    def youtube_loader(self):
        way = "transcript"
        try:
            doc = ""
            attempt = 0
            self.loader_status.info("Extracting transcript from YouTube video is starting...")

            while (len(doc) == 0) and (attempt < 3):
                time.sleep(2)
                attempt += 1
                self.loader_status.info(f"Extracting transcript from YouTube video... Attempt: {attempt}")
                video_id = extract_youtube_id(self.data)

                try:
                    transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
                    available_languages = [trans.language_code for trans in transcript_languages]

                    doc = self.loaders[self.data_type].from_youtube_url(
                        f"https://www.youtube.com/watch?v={video_id}",
                        add_video_info=False,
                        language=available_languages[0],
                    ).load()
                    self.loader_status.info("Transcript extracted successfully.")
                except Exception as e:
                    self.loader_status.warning(f"Attempt {attempt} failed. Retrying...")

            if len(doc) == 0:  # If still no document after 3 attempts, switch to audio extraction
                self.loader_status.info("Transcript extracting failed, trying to extract audio from YouTube video...")
                way = "audio"
                ffmpeg_path = ffmpeg.get_ffmpeg_exe()
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '128',
                    }],
                    'outtmpl': 'audio.%(ext)s',
                    'ffmpeg_location': ffmpeg_path,
                    'progress_hooks': [self.progress_hook]  # Progress hook
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.data])

                doc = self.audio_loader("audio.mp3")
                self.loader_status.info("Audio extracted successfully.")
                time.sleep(2)
                self.loader_status.info("Sending audio to GenerativeAI for text extraction...")

        except Exception as e:
            self.loader_status.error(f"An unexpected error occurred: {str(e)}")
            doc = ""
        return doc, way

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
            self.loader_status.info(f"Download progress: {percent:.2f}%")
        elif d['status'] == 'finished':
            self.loader_status.info("Download finished!")
        elif d['status'] == 'extracting':
            self.loader_status.info("Extracting audio from video...")
        elif d['status'] == 'postprocess':
            self.loader_status.info("Post-processing audio...")
        elif d['status'] == 'error':
            self.loader_status.error(f"An error occurred: {d.get('error', 'Unknown error')}")

    def audio_loader(self, path):
        audio_file = genai.upload_file(path=path)
        print("Uploading audio file to GenerativeAI...")
        prompt = """
        Please provide a detailed text for the audio.
        No need to provide timelines.
        Do not make up any information that is not part of the audio and do not be verbose.
        """
        try:
            response = self.model.generate_content([audio_file, prompt])
            text_response = response.text  # Access the text property if response is valid
            print("Audio extracted successfully, text:", text_response)
        except InternalServerError as e:
            print("An error occurred: ", e)
            print("Triggering the big model...")
            response = self.big_model.generate_content([audio_file, prompt])
            text_response = response.text
            print("Audio extracted successfully, text:", text_response)
        except Exception as e:
            print("Failed to retrieve text from response:", e)
            text_response = " "

        return text_response

    def mp4_loader(self):
        try:
            video = VideoFileClip(self.data)

            # Sesi çıkarma ve kaydetme
            video.audio.write_audiofile("audio.mp3")

            print(f"Audio extracted successfully and saved to audio.mp3")
            response = self.audio_loader("audio.mp3")

        except Exception as e:
            print(f"An error occurred: {e}")
            response = " "
        return response

    def image_loader(self):
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
            print("Image extracted successfully, text:", text_response)
        except InternalServerError as e:
            print("An error occurred: ", e)
            print("Triggering the big model...")
            response = self.big_model.generate_content([image_file, prompt])
            text_response = response.text
            print("Image extracted successfully, text:", text_response)
        except Exception as e:
            print("Failed to retrieve text from response:", e)
            text_response = " "
        return text_response

    def set_loaders(self):
        if self.data_type=="wiki":
            document = self.loaders[self.data_type](self.data, load_max_docs=2).load()
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
        elif self.data_type=="youtube":
            document, way = self.youtube_loader()
            if way == "transcript":
                split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
            else:
                split_doc = self.text_splitter.split_text(document)
        elif self.data_type=="audio":
            document = self.audio_loader(self.data)
            split_doc = self.text_splitter.split_text(document)
        elif self.data_type=="text":
            document = self.data
            split_doc = self.text_splitter.split_text(document)
        elif self.data_type=="mp4":
            document = self.mp4_loader()
            split_doc = self.text_splitter.split_text(document)
        elif self.data_type=="image":
            document = self.image_loader()
            split_doc = self.text_splitter.split_text(document)
        else:
            document = self.loaders[self.data_type](self.data).load()
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))

        return split_doc


