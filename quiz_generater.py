from fastapi import FastAPI,Form
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import time
model=Ollama(model="llama3.1:8b",temperature=0.7,base_url="http://localhost:11434",num_predict=2024)
start_time=time.time()
template = """
You are a senior {programming_language} developer and technical interviewer.

Task:
Generate exactly {number_of_questions} {difficulty_level} level {question_type} questions in {programming_language}.

Output Format Rules (STRICTLY FOLLOW):

1. Return ONLY the questions.
2. Do NOT include answers.
3. Do NOT include explanations.
4. Do NOT include any text before or after the questions.
5. Number each question properly:
   1.
   2.
   3.
6. After each question, add a new line containing exactly:
   *
7. Do NOT add '*' at the beginning.
8. Do NOT add extra '*' at the end.
9. If question_type is MCQ:
   - Provide exactly 4 options labeled:
     A)
     B)
     C)
     D)
   - Do NOT highlight the correct option.
10. Maintain consistent formatting.

Important:
Each question block must end with a single '*' on its own line.
"""

app=FastAPI()
@app.post("/quiz")
async def quiz_generated(programming_language:str=Form(...),question_type:str=Form(...),difficulty_level:str=Form(...),number_of_questions:int=Form(...)):
    try:
        prompt=PromptTemplate(template=template,input_variables=["programming_language","question_type","difficulty_level","number_of_questions"])
        prompt_template=prompt.format(programming_language=programming_language,question_type=question_type,difficulty_level=difficulty_level,number_of_questions=number_of_questions)
        print(prompt_template)
        response=model.invoke(prompt_template)
        print(response.split("*"))
        end_time=time.time()
        print("Time Taken",end_time-start_time)
        return response
    except Exception as e:
        return str(e)