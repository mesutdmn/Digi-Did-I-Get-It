import streamlit as st
from streamlit.components.v1 import html

from utils import check_file_type, create_pdf
import uuid
from all_loaders import Loaders
import tempfile
import os
from dotenv import load_dotenv
import random
import base64
import pypandoc
from parallel_llm import parallel_process
from graph import QuestionGraph, ReportGraph
import static_ffmpeg
import gc

load_dotenv()

os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]
os.environ["SPOTIFY_CLIENT_ID"] = st.secrets["SPOTIFY_CLIENT_ID"]
os.environ["SPOTIFY_CLIENT_SECRET"] = st.secrets["SPOTIFY_CLIENT_SECRET"]


st.set_page_config(page_title="Digi", page_icon="🤖")

def get_base64(bin_file):
    """Get base64 of a file."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

background = get_base64("./media/background.jpg")

with open("./style/style.css", "r") as style:
    css=f"""<style>{style.read().format(background=background)}</style>"""
    st.markdown(css, unsafe_allow_html=True)

def script():
    with open("./style/script.js", "r", encoding="utf-8") as scripts:
        open_script = f"""<script>{scripts.read()}</script> """
        html(open_script, width=0, height=0)

def create_questions_pdf():
    create_pdf(st.session_state.question_list_reorder)

tab1, tab2, tab3 = st.tabs([" ", " ", " "])

if "data" not in st.session_state:
    st.session_state.data = {}
    st.session_state.key_id = uuid.uuid4()
    st.session_state.question_list = []
    st.session_state.question_list_reorder = []
    st.session_state.question = None
    st.session_state.choice = None
    st.session_state.user_request = 0
    st.session_state.answered = False
    pypandoc.download_pandoc() # Download pandoc for pdf conversion, comment this on windows once it is installed.
    #static_ffmpeg.add_paths() # This is not working on Streamlit Sharing due to permission issues. ffmpeg is added in package.txt. Uncomment this on windows.
    st.session_state.answer_list = []
    st.session_state.report = ""
    st.session_state.requested_language = ""
    st.session_state.report_created = True
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.show_questions = False

data_types_dict = {"pdf":"pdf","docx":"docx",
                   "pptx":"pptx","txt":"txt",
                   "enex":"enex","epub":"epub",
                   "mp3":"audio","mp4":"video","mpeg4":"video",
                   "png":"image","jpg":"image","jpeg":"image"}

def send_answer():
    """Send the answer to the question."""
    with tab2:

        if st.session_state.choice is not None:
            selected_answer_index = st.session_state.question['choices'].index(st.session_state.choice)
            if st.session_state.question['answers'][selected_answer_index]:
                st.success("Congratulations, you answered correctly!")
                st.session_state.correct_count += 1
            else:
                st.session_state.answer_list.append({"question": st.session_state.question['question'],
                                                     "student_answer": st.session_state.choice,
                                                     "answers": st.session_state.question['choices'][
                                                         st.session_state.question['answers'].index(True)],
                                                     "explain": st.session_state.question['explain']})

                st.error("Correct answer: " + st.session_state.question['choices'][
                    st.session_state.question['answers'].index(True)])
            st.warning(f"Explanation: {st.session_state.question['explain']}")
            st.session_state.answered = True



def show_question():
    """Show the question and options."""
    st.session_state.question = st.session_state.question_list_reorder[st.session_state.question_index]
    st.write(f"Q-{st.session_state.question_index + 1}: {st.session_state.question['question']}")

    st.session_state.choice = st.radio("Options: ",st.session_state.question['choices'], disabled=st.session_state.answered, label_visibility="collapsed")

    st.button("Submit Answer", type="primary", on_click=send_answer, disabled=st.session_state.answered)



def reset_exam():
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.answered = False
    st.session_state.question_list_reorder = []
    st.session_state.question_list = []
    st.session_state.user_request = 0
    st.session_state.show_questions = False
    st.session_state.answer_list = []
    st.session_state.requested_language = ""
    st.session_state.report_created= True
    st.session_state.report = ""
    gc.collect()


def next_question():
    st.session_state.question_index += 1
    st.session_state.asked = False
    st.session_state.answered = False

def take_again():
    st.session_state.question_index = 0
    st.session_state.correct_count = 0
    st.session_state.answered = False
    st.session_state.answer_list = []
    st.session_state.report_created = True
    st.session_state.report = ""


def clean_components():
    """Clean the components."""
    st.session_state.key_id = uuid.uuid4()

def calculate_results():
    """Calculate the results."""
    st.session_state.report = (f"The exam is over. Here are your results:"
                               f"\n\n Total number of questions: {len(st.session_state.question_list_reorder)} "
                               f"\n\n Number of correct answers: {st.session_state.correct_count}")

with tab2:
    back, forward = st.columns(2)
    back.button("◄ Back to Data Entry", type="secondary", use_container_width=True)
    forward.button("Forward to Results ►", type="primary", use_container_width=True)
    st.button("Show the Results", use_container_width=True, on_click=calculate_results,
              disabled= not (st.session_state.question_index +1 == len(st.session_state.question_list_reorder)) & st.session_state.answered,
              help="You can see the results after you finish the exam.")
    loader_status = st.empty()
    p_bar = st.empty()


def define_llm(data, data_type, data_name, language_input="English"):
    """Define the LLM and generate questions."""
    llm = QuestionGraph().graph
    loader = Loaders(data, data_type,loader_status)
    data = loader.set_loaders()

    shared_list = parallel_process(data, data_name, language_input, llm, p_bar)
    st.session_state.question_list_reorder += list(shared_list)

    print("Questions are generated successfully.")

def create_report():
    """Create the report."""
    report = ReportGraph().graph
    exam_results = {"total_questions": len(st.session_state.question_list_reorder),
                    "correct_answers": st.session_state.correct_count,
                    "wrong_answers": len(st.session_state.question_list_reorder) - st.session_state.correct_count,
                    "questions": st.session_state.answer_list}
    report_response = report.invoke({"exam_results": exam_results, "language": st.session_state.requested_language})
    st.session_state.report = report_response["report"]
    st.session_state.report_created = False

def return_random_questions():
    """Return random amount of questions."""
    st.session_state.question_list_reorder = random.sample(st.session_state.question_list_reorder, st.session_state.user_request)
    st.session_state.show_questions = True

def load_components(key_id):
    """Load the components."""
    file_upload.file_uploader("Upload File", type=data_types_dict.keys(),
                                     accept_multiple_files=True, key=str(key_id)+"files", help="Please upload your document file")
    url_upload.text_input(label="URL",
                          placeholder="https://arxiv.org/pdf/2403.05530",
                          key=str(key_id)+"url",
                          help="Please provide the URL of the document you want to generate questions from. Can't pass paywall.")

    youtube_upload.text_input(label="Youtube URL",
                              placeholder="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                              key=str(key_id)+"youtube",
                              help="Please provide a valid Youtube URL.")

    spotify_upload.text_input(label="Spotify Podcast",
                              placeholder="https://open.spotify.com/episode/6KBpL2XfR9VdojbKNpE7cX?si=fef460b37e7c45eb",
                              key=str(key_id)+"spotify",
                              help="Please provide the Spotify Podcast URL. (There should be episode in the middle)")

    wikipedia_search.text_input(label="Wikipedia Search",
                                placeholder="Artificial Intelligence",
                                key=str(key_id)+"wiki",
                                help="Please provide the search term for Wikipedia.")

    text_input.text_area(label="Direct Text Input",
                         placeholder="Langchain is a platform that provides a suite of tools for developers to build and deploy AI models. "
                                                               "The platform is designed to be easy to use and flexible, allowing developers to create custom models "
                                                               "for a wide range of applications. Langchain provides a range of pre-trained models that can be used "
                                                               "out of the box, as well as tools for training custom models on your own data. The platform is built on "
                                                               "top of the latest research in AI and machine learning, and is designed to be scalable and efficient, "
                                                               "allowing developers to build and deploy models quickly and easily.",
                         key=str(key_id)+"text",
                         help="Please provide the text you want to generate questions from.")

    language_input.selectbox(label="In which language do you prefer questions?",
                             options=["Same as provided document","Turkish", "English", "German", "French", "Spanish", "Italian",
                                          "Portuguese", "Dutch", "Russian", "Chinese", "Japanese", "Korean"],
                             key=str(key_id)+"lang",
                             help="Please select the language you want to generate questions in.")
with tab1:
    back, forward = st.columns(2)
    back.button("◄ Forward to Results ", type="secondary", use_container_width=True)
    forward.button("Forward to Questions ► ", type="primary", use_container_width=True)
    file_upload = st.empty()
    url_upload = st.empty()
    youtube_upload = st.empty()
    spotify_upload = st.empty()
    wikipedia_search = st.empty()
    text_input = st.empty()
    language_input = st.empty()
    col1, col2 = st.columns(2)
    with col1:
        st.button("Clean Form", use_container_width=True, type="secondary", on_click=clean_components)
    with col2:
        submit_data = st.button("Load Data", use_container_width=True, type="primary", on_click=reset_exam)
    load_components(st.session_state.key_id)



    if submit_data:
        uploads = st.session_state.get(str(st.session_state.key_id) + "files")
        url = st.session_state.get(str(st.session_state.key_id) + "url")
        youtube = st.session_state.get(str(st.session_state.key_id) + "youtube")
        spotify = st.session_state.get(str(st.session_state.key_id) + "spotify")
        wikipedia_search = st.session_state.get(str(st.session_state.key_id) + "wiki")
        text_input = st.session_state.get(str(st.session_state.key_id) + "text")
        requested_language = st.session_state.get(str(st.session_state.key_id) + "lang")
        st.session_state.requested_language = requested_language
        print(requested_language)
        if uploads:
            st.session_state.data["files"] = uploads
            for file in uploads:
                if not check_file_type(file):
                    with tab2:
                        st.error(f"{file.name} is invalid file type, or has manipulated extension. Please upload a valid file.")
                    continue
                else:
                    data_extension = file.name.split('.')[-1].lower()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{data_extension}") as temp_file:
                        temp_file.write(file.getvalue())
                        temp_file.flush()
                        temp_file_path = temp_file.name

                    data_type = data_types_dict[data_extension]
                    define_llm(data=temp_file_path, data_type=data_type, data_name=file.name, language_input=requested_language)
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    print(f"{temp_file_path} is removed.")

        if len(url) > 0:
            st.session_state.data["url"] = [url]
            define_llm(data=[url], data_type="url", data_name=url, language_input=requested_language)

        if len(youtube) > 0:
            st.session_state.data["youtube"] = youtube
            define_llm(data=youtube, data_type="youtube", data_name=youtube, language_input=requested_language)

        if len(spotify) > 0:
            st.session_state.data["spotify"] = spotify
            define_llm(data=spotify, data_type="spotify", data_name=spotify, language_input=requested_language)

        if len(wikipedia_search) > 0:
            st.session_state.data["wiki"] = wikipedia_search
            define_llm(data=wikipedia_search, data_type="wiki", data_name=wikipedia_search, language_input=requested_language)

        if len(text_input) > 0:
            st.session_state.data["text"] = text_input
            define_llm(data=text_input, data_type="text", data_name="text_input", language_input=requested_language)




with tab2:
    if st.session_state.show_questions and (st.session_state.question_index < len(st.session_state.question_list_reorder)):
        show_question()
        if st.session_state.question_index + 1 < len(st.session_state.question_list_reorder):
            st.button("Next Question", on_click=next_question, disabled=not st.session_state.answered)
    else:
        st.warning("There is no question to show.")

with tab2:

    if submit_data & (len(st.session_state.question_list_reorder) > 0):
        total_q_count = len(st.session_state.question_list_reorder)
        st.write(f"I have Total {total_q_count} questions for you!")

        st.number_input("How many questions do you want to answer?", min_value=1,
                                           max_value=total_q_count, step=None, on_change=return_random_questions, key="user_request")

    elif (len(st.session_state.question_list_reorder) == 0) & submit_data:
        st.warning("Couldn't generate any questions. Please try again with different data.")



with tab3:
    back, forward = st.columns(2)
    back.button("◄ Back to Questions", type="secondary", use_container_width=True)
    forward.button("Forward to Data Entry ►", type="primary", use_container_width=True)
    st.button("↻ Re-Take The Exam ↺", use_container_width=True, on_click=take_again,
              disabled = not (st.session_state.question_index +1 == len(st.session_state.question_list_reorder)),
              help="You can retake the exam after you finish the exam.")

    if st.session_state.question_index + 1 == len(st.session_state.question_list_reorder):
        result_markdown = st.empty()
        result_markdown.markdown(st.session_state.report, unsafe_allow_html=True)

        create_questions_pdf()
        with open("questions.pdf", "rb") as file:
            file_bytes = file.read()

        col3, col4 = st.columns(2)

        col3.download_button(
            label="▼ Download Questions ▼",
            data=file_bytes,
            file_name="questions.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
        if st.session_state.report_created:
            col4.button("Create Report 📄", use_container_width=True, on_click=create_report)
    else:
        st.warning("The exam is not over. Please answer all the questions.")

script()
