from langchain_core.output_parsers import JsonOutputParser
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from unstructured.cleaners.translate import translate_text

from question_format import Test




class LLMs:
    def __init__(self,):
        self.model = GoogleGenerativeAI(model="gemini-1.5-flash-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)
        self.bigger_model = GoogleGenerativeAI(model="gemini-1.5-pro-002",temperature=0,max_tokens=None,timeout=None,max_retries=2)

        self.question_template = """
                                    You are an exam preparation expert tasked with generating multiple-choice questions from the provided context. For each question:
                                    - Generate **exactly four options**, and label them as "A", "B", "C", and "D".
                                    - Only one option should be correct. Indicate this by setting only one option as `True` in the answers list, with the others as `False`.
                        
                                    Provide the response in the specified JSON structure:
                                    {{
                                        "question": "The text of the question.",
                                        "choices": [
                                            "A) First option",
                                            "B) Second option",
                                            "C) Third option",
                                            "D) Fourth option"
                                        ],
                                        "answers": [], // True should appear only once.
                                           
                                        "explain": "A brief explanation of why the correct answer is correct."
                                    }}
                        
                                    Although this instruction is in English, provide the final output in the specified language.
                        
                                    Context: {context}
                                    Output Language: {language}
                                    {format_instructions}
                                """

        self.translation_template = """
                                            You are a translation expert. Given a JSON structure, translate only the **values** of the JSON into the specified language while leaving **keys unchanged**. 

                                            Requirements:
                                            - Preserve the JSON structure exactly as given.
                                            - Only translate the text within the values.
                                            - If the values are already in the target language, leave them as they are.
                                            - **Do not translate specific terms, labels, or the JSON structure**

                                            Provide the translated JSON output without modifying any keys.

                                            JSON Data:
                                            {json_data}
                                            Target Language: {language}
                                        """

    def question_maker(self, input):
        context = input["context"]
        language = input["language"]

        parser = JsonOutputParser(pydantic_object=Test)
        prompt = PromptTemplate(
            template=self.question_template,
            input_variables=["context", "language"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        chain_big = prompt | self.bigger_model | parser
        print("**Chain created**")
        response = ""
        try:
            print("**Entered Chain**")
            response = chain.invoke({"context": context, "language": language})

            # Convert response to a dictionary if needed for translation
            translated_response = self.translate_text({
                "json_data": response if isinstance(response, Test) else response,
                "language": language
            })

            print("**Response received and translated**")
        except Exception as e:
            print("Triggered Bigger Model", e)
            response = chain_big.invoke({"context": context, "language": language})
            try:
                translated_response = self.translate_text({
                    "json_data": response if isinstance(response, Test) else response,
                    "language": language
                })
                print("**Error Fixed By Bigger Model**")
            except Exception as e:
                print("Error occurred while Testing Model questions.", e)
                translated_response = response  # fallback if translation fails
        return translated_response

    def translate_text(self, input):

        parser = JsonOutputParser(pydantic_object=Test)
        prompt = PromptTemplate(
            template=self.translation_template,
            input_variables=["json_data", "language"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | self.model | parser
        chain_big = prompt | self.bigger_model | parser
        print("**Chain created**")
        try:
            print("**Entered Chain**")
            response = chain.invoke(input)
            Test(**response)
            print("**Response received**")
        except Exception as e:
            print("Triggered Bigger Model", e)
            response = chain_big.invoke(input)
            try:
                Test(**response)
                print("**Translated By Bigger Model**")
            except Exception as e:
                print("Error occurred while Testing Model questions.", e)
                response = input["json_data"]
        return response












