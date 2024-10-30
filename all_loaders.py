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
    def __init__(self, data):
        self.data = data
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


    def youtube_loader(self, data, data_type):
        way = "transcript"
        try:
            doc=""
            attempt=0
            while (len(doc) == 0) & (attempt < 3):
                time.sleep(5)
                attempt += 1
                print(f"Extracting transcript from YouTube video... {attempt}")
                video_id = extract_youtube_id(data)
                transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
                available_languages = [trans.language_code for trans in transcript_languages]

                doc = self.loaders[data_type].from_youtube_url(
                    f"https://www.youtube.com/watch?v={video_id}",
                    add_video_info=False,
                    language=available_languages[0],
                ).load()
                print("Transcript extracted successfully")

        except:
            print("Transcript Extracting Failed, Extracting audio from YouTube video...")
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
                'ffmpeg_location': ffmpeg_path
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([data])
            doc = self.audio_loader("audio.mp3")
            print("Audio Extracted successfully")

        return doc, way

    def audio_loader(self, data):
        audio_file = genai.upload_file(path=data)
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

    def mp4_loader(self, data):
        try:
            video = VideoFileClip(data)

            # Sesi çıkarma ve kaydetme
            video.audio.write_audiofile("audio.mp3")

            print(f"Audio extracted successfully and saved to audio.mp3")
            response = self.audio_loader("audio.mp3")

        except Exception as e:
            print(f"An error occurred: {e}")
            response = " "
        return response

    def image_loader(self, data):
        image_file = genai.upload_file(path=data)
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

    def set_loaders(self, data_type):
        if data_type=="wiki":
            document = self.loaders[data_type](self.data, load_max_docs=2).load()
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
        elif data_type=="youtube":
            document, way = self.youtube_loader(self.data, data_type)
            if way == "transcript":
                split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))
            else:
                split_doc = self.text_splitter.split_text(document)
        elif data_type=="audio":
            document = self.audio_loader(self.data)
            split_doc = self.text_splitter.split_text(document)
        elif data_type=="text":
            document = self.data
            split_doc = self.text_splitter.split_text(document)
        elif data_type=="mp4":
            document = self.mp4_loader(self.data)
            split_doc = self.text_splitter.split_text(document)
        elif data_type=="image":
            document = self.image_loader(self.data)
            split_doc = self.text_splitter.split_text(document)
        else:
            document = self.loaders[data_type](self.data).load()
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))

        return split_doc


