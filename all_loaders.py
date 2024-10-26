from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader,Docx2txtLoader,
    WebBaseLoader, WikipediaLoader,
    EverNoteLoader, UnstructuredPowerPointLoader,
    YoutubeLoader, UnstructuredEPubLoader)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from youtube_transcript_api import YouTubeTranscriptApi
from utils import extract_youtube_id
import google.generativeai as genai
from moviepy.editor import VideoFileClip


class Loaders:
    def __init__(self, data):
        self.data = data
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")

        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2000, chunk_overlap=0)
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
        video_id = extract_youtube_id(data)
        transcript_languages = YouTubeTranscriptApi.list_transcripts(video_id)
        available_languages = [trans.language_code for trans in transcript_languages]

        doc = self.loaders[data_type].from_youtube_url(
            f"https://www.youtube.com/watch?v={video_id}",
            add_video_info=False,
            language=available_languages[0],
        ).load()
        return doc

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
            doc = self.loaders[data_type](self.data, load_max_docs=2).load()
        elif data_type=="youtube":
            doc = self.youtube_loader(self.data, data_type)
        elif data_type=="audio":
            doc = self.audio_loader(self.data)
        elif data_type=="text":
            doc = self.data
        elif data_type=="mp4":
            doc = self.mp4_loader(self.data)
        elif data_type in ["png", "jpg", "jpeg"]:
            doc = self.image_loader(self.data)
        else:
            doc = self.loaders[data_type](self.data).load()
        split_doc = self.text_splitter.split_documents(doc)
        return split_doc


