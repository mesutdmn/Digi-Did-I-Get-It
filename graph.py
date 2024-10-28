from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from question_format import TestModel




class LLMs:
    def __init__(self,):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)

        self.question_template = """
                                        You are a professional exam preparation assistant.
                                        You need to create multiple choice test questions based on the given context.
                                        For each question, generate exactly four options, with only one option marked as correct.
                                        Ensure that only one option is marked as correct per question, and no more.
                                        Even though this prompt is in English, produce the output in the specified language.
                                        Provide the questions, options, correct answer, and a concise explanation of the correct answer in the specified JSON format.

                                        Context: {context}
                                        Output Language: {language}
                                        {format_instructions}
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
        print("**Chain created**")
        response = ""
        try:
            print("**Entered Chain**")
            response = chain.invoke({"context": context, "language": language})
            print("**Response received**")
        except Exception as e:
            response = self.check_json_error(e)
            print("**Error occurred**")
        print(response)
        return response

    def check_json_error(self, error):
        fixer_prompt = """You are en error fixer assistant, fix this JSON file and return in the required format.\n\n
                    
                    Broken JSON: {error}
                    \n{format_instructions}
                    """
        parser = JsonOutputParser(pydantic_object=TestModel)
        prompt = PromptTemplate(
            template=fixer_prompt,
            input_variables=["error"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        try:
            response = chain.invoke({"error": error})
        except Exception as e:
            print(f"An error occurred While Fixin: {e}")
            response = " "
        return response










