import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from question_format import Question
from utils import shuffle_choices
from graph import LLMs
from threading import Lock

lock = Lock()
def process_doc(doc, language_input, shared_list):
    llm = LLMs()

    try:
        response = llm.question_maker({"context": doc, "language": language_input})["questions"]
        response = shuffle_choices(response)
        for question in response:
            try:
                Question(**question)
                with lock:
                    shared_list.append(question)
            except Exception as e:
                print("One of the questions is not in required format.", e)
    except Exception as e:
        print("Error occurred while Testing Model questions.", e)


def parallel_process(data, data_name, language_input, p_bar):
    shared_list = []

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_doc, doc, language_input, shared_list) for doc in data]


        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            p_bar.progress(value=i / len(data), text=f"Questions Loading for Data: {data_name}: {i}/{len(data)}")
    return shared_list