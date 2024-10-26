import magic
import re

data_types = {"pdf":"application/pdf",
              "txt":"text/plain",
              "mp3":"audio/mpeg",
              "wav":"audio/wav",
              "enex":"text/xml",
              "mp4":"video/mp4",
              "docx":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
              "png":"image/png",
              "jpg":"image/jpeg",
              "jpeg":"image/jpeg",
              "pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
              "epub":"application/epub+zip"}

def check_file_type(file):
    # Dosya içeriğini okuma
    file_content = file.read()
    file_extension = file.name.split('.')[-1].lower()

    # MIME türünü kontrol etme
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file_content)

    # Beklenen MIME türüyle karşılaştırma

    return file_mime == data_types[file_extension]


def extract_youtube_id(url):
    # YouTube URL regex pattern
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.*|(?:v|e(?:mbed)?|watch|watch\?.*v=)|.*[?&]v=)|youtu\.be/)([a-zA-Z0-9_-]{11})'

    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        return None

