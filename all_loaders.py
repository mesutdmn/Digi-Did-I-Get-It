from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader,Docx2txtLoader,
    WebBaseLoader, WikipediaLoader,
    EverNoteLoader, UnstructuredPowerPointLoader,
    YoutubeLoader, YoutubeAudioLoader, UnstructuredEPubLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from utils import extract_youtube_id
import google.generativeai as genai
from moviepy.editor import VideoFileClip
import yt_dlp
import imageio_ffmpeg as ffmpeg

class Loaders:
    def __init__(self, data):
        self.data = data
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")

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
            print("Extracting transcript from YouTube video...")
            video_id = extract_youtube_id(data)
            transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
            available_languages = [trans.language_code for trans in transcript_languages]

            doc = self.loaders[data_type].from_youtube_url(
                f"https://www.youtube.com/watch?v={video_id}",
                add_video_info=False,
                language=available_languages[0],
            ).load()
            print(doc)
        except:
            print("Extracting audio from YouTube video...")
            way = "audio"
            # path_audio = [audio.path for audio in
            #               YoutubeAudioLoader(urls=[data],
            #                                  save_dir=".").yield_blobs()]
            # doc = self.audio_loader(path_audio[0])
            ffmpeg_path = ffmpeg.get_ffmpeg_exe()
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': 'audio.%(ext)s',
                'ffmpeg_location': ffmpeg_path
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([data])
            doc = self.audio_loader("audio.mp3")
        return doc, way

    def audio_loader(self, data):
        audio_file = genai.upload_file(path=data)

        response = self.model.generate_content(["Convert speech to text", audio_file]).text
        return response

    def mp4_loader(self, data):
        try:
            video = VideoFileClip(data)

            # Sesi çıkarma ve kaydetme
            video.audio.write_audiofile("audio.mp3")

            print(f"Audio extracted successfully and saved to audio.mp3")

        except Exception as e:
            print(f"An error occurred: {e}")

        response = self.audio_loader("audio.mp3")

        return response

    def image_loader(self, data):
        response = self.model.generate_content(["Extract the text from image", data]).text
        return response

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
        elif data_type in ["png", "jpg", "jpeg"]:
            document = self.image_loader(self.data)
            split_doc = self.text_splitter.split_text(document)
        else:
            document = self.loaders[data_type](self.data).load()
            split_doc = self.text_splitter.split_text(" ".join([doc.page_content for doc in document]))

        return split_doc


