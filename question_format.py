from pydantic import BaseModel, Field, field_validator
from typing import List, Literal

class Question(BaseModel):
    question: str = Field(..., description="The text of the question being asked.")
    # The actual question text that will be presented to the user.

    choices: List[str] = Field(...,
                               description="List of four choices for the multiple-choice question. Only one should be correct.")
    # A list containing the possible answer choices. It should have exactly four options.

    answers: List[bool] = Field(...,
                                description="A list of boolean values indicating which choice is correct. Only one should be True.")
    # A list of boolean values where only one is `True`, indicating the correct choice among the four options.

    explain: str = Field(..., description="An explanation of why the correct answer is correct.")

    # A string that explains why the correct answer is the right choice.

    # Custom field_validator to ensure exactly 3 False and 1 True
    @field_validator('answers')
    def check_answers(cls, v):
        if len(v) != 4:
            raise ValueError('The answers list must contain exactly 4 boolean values.')
        if v.count(True) != 1 or v.count(False) != 3:
            raise ValueError('The answers list must contain exactly 3 False and 1 True values.')
        return v


class Test(BaseModel):
    questions: List[Question] = Field(...,
                                      description="A list of questions containing the question text, choices, answers, and explanations.")
    # Contains a list of `Question` objects, each holding the question text, choices, answers, and explanation for that question.


class AskLLM(BaseModel):
    """Answer the question, only True or False allowed."""
    answer: Literal[True,False] = Field(...,
                                        description="Answer to the question asked by the user.")

