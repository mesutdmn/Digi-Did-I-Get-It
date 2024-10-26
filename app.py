import streamlit as st
import time

from click import progressbar
from tqdm import tqdm
from all_loaders import Loaders
from utils import check_file_type
import uuid
from graph import LLMs
from question_format import TestModel
from all_loaders import Loaders
import tempfile
from dotenv import load_dotenv
load_dotenv()


st.set_page_config(page_title="Digi", page_icon="🤖")

# Step 1: Data Entry Card
st.title("Dynamic Question Generator")
tab1, tab2, tab3 = st.tabs(["Data Entry", "Question Generation", "Question Review"])

data_types_dict = {"pdf":"pdf","mp3":"audio","wav":"audio","enex":"enex","mp4":"mp4","docx":"docx","png":"image","jpg":"image","pptx":"pptx","epub":"epub","txt":"txt"}

if "data" not in st.session_state:
    st.session_state.data = {}
    st.session_state.key_id = uuid.uuid4()
    st.session_state.question_list = []

if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.show_questions = False

def show_question():
    """Aktif soruyu gösterir ve cevabı denetler."""
    question = st.session_state.question_list[st.session_state.question_index]
    st.write(f"Soru {st.session_state.question_index + 1}: {question['question']}")

    # Kullanıcıdan cevap alma
    choice = st.radio("Seçenekler:", question['choices'])

    # Cevabı doğrula
    if st.button("Cevabı Gönder"):
        if choice is not None:
            # Doğru cevap kontrolü
            selected_answer_index = question['choices'].index(choice)
            if question['answers'][selected_answer_index]:
                st.success("Doğru bildiniz!")
                st.session_state.correct_count += 1
            else:
                st.error("Yanlış bildiniz.")
            st.write("Açıklama:", question['explain'])

def next_question():
    """Sonraki soruya geçiş yapar veya sonuçları gösterir."""
    st.session_state.question_index += 1
def take_again():
    """Testi tekrar başlatır."""
    st.session_state.question_index = 0
    st.session_state.correct_count = 0

def show_results():
    """Sonuçları gösterir."""
    with tab3:
        st.write(f"Toplam soru sayısı: {len(st.session_state.question_list)}")
        st.write(f"Doğru sayısı: {st.session_state.correct_count}")

def clean_components():
    st.session_state.key_id = uuid.uuid4()

def define_llm(data, data_type):
    loader = Loaders(data)
    data = loader.set_loaders(data_type)
    llm = LLMs()
    p_bar = st.progress(0)
    len_data = len(data[:4])
    for i, doc in enumerate(data[:4],1):
        p_bar.progress(i/len_data)
        try:
            # Modeli çalıştırıp yanıtı alıyoruz
            response = llm.question_maker({"context": doc, "language": "Turkish"})
            TestModel(**response)
            st.session_state.question_list.append(response)
        except:
            pass
    st.session_state.question_list = [question for questions in st.session_state.question_list for question in questions["test"]["questions"]]

def load_components(key_id):
    file_upload.file_uploader("Upload File", type=["pdf","txt","mp3","wav","enex","mp4","docx","png","jpg","pptx","epub"],
                                     accept_multiple_files=True, key=str(key_id)+"files")
    url_upload.text_input("URL",
                               placeholder="https://medium.com/@dumanmesut/building-autonomous-multi-agent-systems-with-crewai-1a3b3a348271", key=str(key_id)+"url")
    youtube_upload.text_input("Youtube URL", placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ", key=str(key_id)+"youtube")
    wikipedia_search.text_input("Wikipedia Search", placeholder="Artificial Intelligence", key=str(key_id)+"wiki")
    text_input.text_area("Direct Text Input", placeholder="Langchain is a platform that provides a suite of tools for developers to build and deploy AI models. "
                                                               "The platform is designed to be easy to use and flexible, allowing developers to create custom models "
                                                               "for a wide range of applications. Langchain provides a range of pre-trained models that can be used "
                                                               "out of the box, as well as tools for training custom models on your own data. The platform is built on "
                                                               "top of the latest research in AI and machine learning, and is designed to be scalable and efficient, "
                                                               "allowing developers to build and deploy models quickly and easily.", key=str(key_id)+"text")
with tab1:
    st.subheader("Enter Data")
    file_upload = st.empty()
    url_upload = st.empty()
    youtube_upload = st.empty()
    wikipedia_search = st.empty()
    text_input = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        st.button("Clean Form", use_container_width=True, type="secondary", on_click=clean_components)
    with col2:
        submit_data = st.button("Load Data", use_container_width=True, type="primary")
    st.write(st.session_state.key_id)
    load_components(st.session_state.key_id)


    if submit_data:
        uploads = st.session_state.get(str(st.session_state.key_id) + "files")
        if uploads:
            st.session_state.data["files"] = uploads
            for file in uploads:
                if not check_file_type(file):
                    st.error("Invalid file type, or manipulated extension. Please upload a valid file.")
                    break
                else:
                    data_extension = file.name.split('.')[-1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{data_extension}") as temp_file:
                        temp_file.write(file.getvalue())
                        temp_file.flush()
                        temp_file_path = temp_file.name

                    data_type = data_types_dict[data_extension]
                    define_llm(temp_file_path, data_type)

        if url_upload:
            st.session_state.data["url"] = st.session_state.get(str(st.session_state.key_id) + "url")
        if youtube_upload:
            st.session_state.data["youtube"] = st.session_state.get(str(st.session_state.key_id) + "youtube")
        if wikipedia_search:
            st.session_state.data["wiki"] = st.session_state.get(str(st.session_state.key_id) + "wiki")
        if text_input:
            st.session_state.data["text"] = st.session_state.get(str(st.session_state.key_id) + "text")

        st.session_state.show_questions = True
p_bar = st.empty()
with tab2:
    if st.session_state.show_questions & (st.session_state.question_index + 1 <= len(st.session_state.question_list)):
        show_question()
    if st.session_state.question_index + 1 <= len(st.session_state.question_list):
        st.button("Sonraki Soru", on_click=next_question)
    else:
        st.write("Tebrikler Testi Tamamladınız!")
        col3, col4 = st.columns(2)
        with col3:
            st.button("Testi Tekrar Başlat", on_click=take_again, use_container_width=True)
        with col4:
            st.button("Show Results", on_click=show_results, use_container_width=True)
