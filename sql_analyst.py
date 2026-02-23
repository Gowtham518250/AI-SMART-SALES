from langchain_community.llms import Ollama
from fastapi import APIRouter, UploadFile, File, Form
from langchain.prompts import PromptTemplate
from fastapi import HTTPException,Form,File,UploadFile
import pandas as pd
import io
import time
from sqlalchemy import create_engine
import numpy as np
import os
import pyodbc
from sqlalchemy import create_engine
import uuid
from urllib.parse import quote_plus
from RAG_APP.db import engine
model=Ollama(model="qwen2.5:14b",temperature=0.0,base_url="http://localhost:11434",num_predict=500)
template=""" You are an Senior Level SQL Analyst.Based on Provided Context And User Question Write a Accurate Query.
You Does not Have to Access Complete Data
    - Table Name : {table_name}
    - The Data was provided with Columns with Respective Column Types
    - Columns with Column Types:
    - {column_types}
    - Question : {query}
Rules:
- please provide accurate answer
- Before Generating Query Please Check Columns You Used Correctly in Answer or not
- Dont Provide Additional information
- Return The Query alone.
- Dont Produce any Noisy Data
- Dont give any single extra letter or symbols i need Exact Query Only
- AT last dont miss semicolon(;) in query end
"""
router = APIRouter()
@router.post("/sql_analysis/")
async def sql_analysis(file:UploadFile=File(...),query:str=Form(...)):
    start=time.time()
    content=await file.read()
    if file.filename.endswith(".csv"):
        try:
            df=pd.read_csv(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400,detail="Error reading CSV file: "+str(e))
    elif file.filename.endswith(".xlsx"):
        try:
            df=pd.read_excel(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400,detail="Error reading Excel file: "+str(e))
    elif file.filename.endswith(".json"):
        try:
            df=pd.read_json(io.BytesIO(content))
        except Exception as e:
            raise HTTPException(status_code=400,detail="Error reading JSON file: "+str(e))
    table_name=f"user_table_{uuid.uuid4().hex}"
    df.to_sql(table_name,engine,if_exists="replace",index=False)
    columns=df.columns.to_list()
    column_types=", ".join([f"{col}:{df[col].dtype}" for col in columns])
    new_template=PromptTemplate(
        template=template
    ,input_variables=["table_name","column_types","query"])
    prompt_template=new_template.format(table_name=table_name,column_types=column_types,query=query)
    print("Generated Prompt Template:",prompt_template)
    answer=model.invoke(prompt_template)
    forbidden = ["drop", "delete", "update", "insert", "alter"]
    if any(word in answer.lower() for word in forbidden):
        raise HTTPException(status_code=500,detail="Risked query Generated")
    print("Generated SQL Query:",answer)
    response=pd.read_sql_query(answer,engine)
    print("SQL Query Executed Successfully",pd.DataFrame(response))
    end=time.time()
    print(os.getcwd())
    return ({"Query":answer,"Execution Time":end-start, "Data": response.to_dict('records')})

