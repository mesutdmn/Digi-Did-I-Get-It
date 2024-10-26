from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from question_format import TestModel




class LLMs:
    def __init__(self,):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash",temperature=0,max_tokens=None,timeout=None,max_retries=2)

        self.question_template ="""
                                You are a professional exam preparation assistant.\n
                                You are asked to prepare various multiple choice test questions from the given document.\n
                                You have to use the context given to you while preparing the questions.\n
                                You can use your creativity for the options, remember that only one of the four options should be correct.\n
                                Even though this prompt is in English, you should make the output in the language asked to you.\n
                                You need to return the questions, options, correct answers, and the explanation of the correct answer in the given JSON format.\n
                        
                                Context: {context}
                                \nLanguage: {language}
                                \n{format_instructions}
                            """

    def question_maker(self, input):
        context = input["context"]
        language = input["language"]

        parser = JsonOutputParser(pydantic_object=TestModel)
        prompt = PromptTemplate(
            template=self.question_template,
            input_variables=["context", "language"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser

        response = chain.invoke({"context": context, "language": language})

        return response











