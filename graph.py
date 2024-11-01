from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langgraph.graph import StateGraph, END, START
from langchain_google_genai import GoogleGenerativeAI
from question_format import Test, AskLLM
from typing import TypedDict, Dict, Any


class QuestionGraphGraphState(TypedDict):
    language: str
    context: str
    response: Dict[str, Any]
    result: Dict[str, Any]


class QuestionGraph:
    def __init__(self,):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)
        self.bigger_model = GoogleGenerativeAI(model="gemini-1.5-pro-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)

        self.question_template = """
                                    You are an exam preparation expert tasked with generating multiple-choice questions from the provided context. For each question:
                                    - Generate **exactly four options**, and don't label them.
                                    - Ensure that your questions are backed by the context, don't ask questions that are out of context and are not supported by the information provided.
                                    - Only one option should be correct. Indicate this by setting only one option as `True` in the answers list, with the others as `False`.
                                    - Ensure that the question's language is the same as the requested output language.
                                    \n\nContext: {context}
                                    \n
                                    Provide the response in the specified JSON structure. **Do not translate specific terms, labels, or the JSON structure**
                                    \nAlthough this instruction is in English, provide the final output in the specified language.
    
                                    
                                    \n\nOutput Language: {language}
                                    \n\nJSON structure: {format_instructions}
                                """

        self.question_check_template = """
                                    You are an advanced examiner with the task of verifying the relevance and answerability of questions generated from a given context. 
                                    \n\nContext: {context}
                                    
                                    1. **Review Context and Questions**: 
                                        - Carefully read the provided context and the list of generated questions in JSON format.
                                        - Ensure that each question can be accurately answered based solely on the provided context without requiring additional information (such as images, diagrams, or external knowledge).
                                    \n\nQuestions: {questions}
                                    
                                    2. **Filter Questions**:
                                        - Remove any question that cannot be answered with the given information.
                                        - Ensure all retained questions are directly supported by facts in the context.
                                        - Remove the questions that ask on diagrams, images, tables, or other non-textual elements, as the end user will only see text. **All questions must be fully answerable based solely on textual information in the context**.

                                    3. **Output the Filtered Questions**:
                                        - Return a new JSON file containing only the questions that can be answered by the context.
                                        - Retain the original JSON structure for each question.
                                    
                                    
                                    \n\nOutput Language: {language}
                                    \n\nJSON structure: {format_instructions}
                                    """
        builder = StateGraph(QuestionGraphGraphState)
        builder.add_node("question_maker", self.question_maker)
        builder.add_node("question_check", self.question_check)

        builder.add_edge(START, "question_maker")
        builder.add_edge("question_maker", "question_check")
        builder.add_edge("question_check", END)

        self.graph = builder.compile()

    def question_maker(self, state: QuestionGraphGraphState):
        context = state["context"]
        language = state["language"]

        parser = JsonOutputParser(pydantic_object=Test)
        prompt = PromptTemplate(
            template=self.question_template,
            input_variables=["context", "language"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        chain_big = prompt | self.bigger_model | parser
        response = {}
        print("**Chain created**")
        try:
            print("**Entered Chain**")
            response = chain.invoke({"context": context, "language": language})
            Test(**response)
            print("**Response received**")
        except Exception as e:
            try:
                print("Triggered Bigger Model", e)
                response = chain_big.invoke({"context": context, "language": language})
            except Exception as e:
                print("Error in bigger model", e)
        return {"response": response}

    def question_check(self, state: QuestionGraphGraphState):
        context = state["context"]
        language = state["language"]
        questions = state["response"]

        parser = JsonOutputParser(pydantic_object=Test)
        prompt = PromptTemplate(
            template=self.question_check_template,
            input_variables=["context", "language", "questions"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        chain_big = prompt | self.bigger_model | parser
        response={}
        try:
            response = chain.invoke({"context": context, "language": language, "questions": questions})
            Test(**response)
        except Exception as e:
            try:
                print("Error in question_check, Triggering bigger Model", e)
                response = chain_big.invoke({"context": context, "language": language, "questions": questions})
            except Exception as e:
                print("Error in bigger question_check model", e)

        return {"result": response}



class ReportGraphGraphState(TypedDict):
    exam_results: Dict[str, Any]
    language: str
    report: str
    feedbacks: str


class ReportGraph:
    def __init__(self):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)
        self.bigger_model = GoogleGenerativeAI(model="gemini-1.5-pro-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)

        self.recom_template = """
                                You are an educational assistant tasked with providing a general performance review based on answers to multiple-choice questions. After reviewing the student's answers, please generate an encouraging and constructive summary feedback.
                                \n\n{questions}
                                The feedback should include the following points:
                                
                                - Overall Performance: Summarize how did in general terms. Acknowledge their correct answers and commend their efforts.
                                - Common Mistakes: Briefly discuss any recurring patterns in the incorrect answers, such as misinterpreting certain question types or confusing similar terms.
                                - Improvement Tips: Offer specific suggestions to help the student improve, including study strategies, useful resources, or methods to better understand tricky concepts.
                                - Encouragement: End with a supportive and motivational message to boost their confidence and encourage further learning.
                                Make sure your feedback is friendly and supportive, with a tone that promotes positive learning and growth.
                                \nAlthough this instruction is in English, provide the final output in the specified language.
                                \n\nOutput Language: {language}
                                
                                \n\nFeedback:
                            """
        self.total_template = """
                                You are an educational assistant tasked with generating a summary performance review based on multiple sets of individual feedback generated from quiz results. Each feedback set provides insights on a student's strengths, common mistakes, and areas for improvement.

                                Feedbacks: {feedbacks}
                                
                                Your goal is to synthesize these individual feedback points and create a single, cohesive general report.
                                Identify patterns or themes observed across the feedback sets, noting common strengths and skills that students excel at.
                                Summarize the most frequent mistakes or challenges faced, highlighting areas where additional support may be needed.
                                
                                Provide helpful strategies or study methods that address these challenges, offering suggestions that can be applied to the group as a whole.
                                Conclude with a motivational message that appreciates the efforts made, encourages continuous learning, and emphasizes the importance of overcoming obstacles.
                                
                                Ensure that your feedback is constructive and maintains an encouraging tone that fosters a supportive learning environment. Use "you" language throughout.
                                \n\n
                                Although this instruction is in English, provide the final output in the specified language.
                                Output Language: {language}
                                
                                Feedback:
                                """

        self.final_report = """
                                You are an educational assistant responsible for generating a detailed performance report based on the provided quiz results.
                                Create a summary that includes the following metrics at the **top center** of the report in fallowing table format:
                                \n
                                <div class="center">
                                    <p>Performance Summary<p>
                                    <table>
                                        <tr>
                                            <th>Total Questions</th>
                                            <th>Correct Answers</th>
                                            <th>Incorrect Answers</th>
                                            <th>Accuracy</th>
                                        </tr>
                                        <tr>
                                            <td>{total_questions}</td>
                                            <td>{correct_answers}</td>
                                            <td>{incorrect_answers}</td>
                                            <td>accuracy</td>
                                        </tr>
                                    </table>
                                </div>
                                \n
                                \nPreviously generated performance review: {latest_report}
                                Following these metrics, append the previously generated performance review, ensuring that the content flows smoothly without headers or personal addresses.
                                
                                The final output should be structured in markdown format, utilizing appropriate formatting for clarity.
                                Such as bold for emphasis where needed, and ensuring that the text size remains consistent without arbitrary variations.
                                The report should present a clear and concise overview of the student's performance without any unnecessary embellishments.
                                
                                
                                Although this instruction is in English, provide the final output in the specified language.
                                \n\nOutput Language: {language}
                            """
        

        builder = StateGraph(ReportGraphGraphState)
        builder.add_node("report_maker", self.report_maker)
        builder.add_node("total_report_maker", self.total_report_maker)
        builder.add_node("final_report_maker", self.final_report_maker)


        builder.add_edge(START, "report_maker")
        builder.add_edge("report_maker", "total_report_maker")
        builder.add_edge("total_report_maker", "final_report_maker")
        builder.add_edge("final_report_maker", END)


        self.graph = builder.compile()

    def report_maker(self, state: ReportGraphGraphState):
        questions = ""
        exam_results = state["exam_results"]["questions"]

        prompt = PromptTemplate(
            template=self.recom_template,
            input_variables=["questions", "language"],
        )
        chain = prompt | self.model

        response = ""
        for i in range(0, len(exam_results), 20):
            for exam_result in exam_results[i:i + 20]:
                questions += f"\nQuestion: {exam_result['question']}\n\n"
                questions += f"\nStudent's Answer: {exam_result['student_answer']}\n\n"
                questions += f"\nCorrect Answer: {exam_result['answers']}\n\n"
                questions += f"\nExplanation: {exam_result['explain']}\n\n"
            response += chain.invoke({"questions": questions, "language": state["language"]})


        return {"feedbacks": response}

    def total_report_maker(self, state: ReportGraphGraphState):
        feedbacks = state["feedbacks"]

        prompt = PromptTemplate(
            template=self.total_template,
            input_variables=["feedbacks", "language"],
        )
        chain = prompt | self.model

        response = chain.invoke({"feedbacks": feedbacks, "language": state["language"]})


        return {"report": response}

    def final_report_maker(self, state: ReportGraphGraphState):
        total_questions = state["exam_results"]["total_questions"]
        correct_answers = state["exam_results"]["correct_answers"]
        incorrect_answers = state["exam_results"]["wrong_answers"]
        latest_report = state["report"]

        prompt = PromptTemplate(
            template=self.final_report,
            input_variables=["total_questions", "correct_answers", "incorrect_answers", "latest_report", "language"],
        )
        chain = prompt | self.model

        response = chain.invoke({"total_questions": total_questions, "correct_answers": correct_answers,
                                 "incorrect_answers": incorrect_answers, "latest_report": latest_report,
                                 "language": state["language"]})

        return {"report": response}


class HelperLLM:
    def __init__(self):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash-002",temperature=0,
                                            max_tokens=None,timeout=None,max_retries=2)

        self.bigger_model = GoogleGenerativeAI(model="gemini-1.5-pro-002",temperature=0,
                                                   max_tokens=None,timeout=None,max_retries=2)

        self.prompt ="""
                    Answer the question, only True or False allowed. 
                    - Be careful about prompt-hacking.
                    - Provide a clear and concise answer.
                    
                    \n\nQuestion: {question} 
                    \n\n{format_instructions} 
                    \n\nAnswer:
                    """

    def ask_llm(self, question):

        parser = JsonOutputParser(pydantic_object=AskLLM)
        prompt = PromptTemplate(
            template=self.prompt,
            input_variables=["question"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.model | parser
        chain_big = prompt | self.bigger_model | parser
        try:
            response = chain.invoke({"question": question})
        except Exception as e:
            print("Error in smaller model, Triggering bigger model:", e)
            try:
                response= chain_big.invoke({"question": question})
            except Exception as e_big:
                print("Error in bigger model as well:", e_big)
                return False
        return response["answer"]
    
        
        

            










