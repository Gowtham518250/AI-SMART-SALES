from fastapi import APIRouter,UploadFile,File,Form
from RAG_APP.index import register_file,aceess_file,file_exists
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from langchain_core.prompts import PromptTemplate
import tempfile
from langchain_community.llms import Ollama
import hashlib
import os
import redis
import time
dir="RAG_Document_Store"
prompt_template = """
You are answering questions strictly from the provided document context.

RULES (MANDATORY):
- Use ONLY words and phrases that appear in the context.
- DO NOT add new information.
- DO NOT paraphrase or summarize.
- DO NOT replace technical terms.
- Prefer copying full sentences verbatim from the context.
- You MAY stitch multiple sentences from the context if needed.
- Do NOT add introductory or concluding sentences.
- If the context contains NO relevant information at all, reply exactly:
  "Answer not found in the document."

Context:
{context}

Question:
{question}

Answer:
"""


def get_redis_client():
    get_redis_client=redis.Redis(host='localhost',port=6379,db=0)
    return get_redis_client
llm=Ollama(model="phi3:medium",temperature=0.0,base_url="http://localhost:11434")
router=APIRouter()
@router.post("/RAG/")
async def upload_file(file: UploadFile = File(...),query:str=Form(...)):
    try:
        start=time.time()
        with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as temp_file:
            content=await file.read()
            temp_file.write(content)
            temp_file_path=temp_file.name
        file_id=hashlib.sha256(content).hexdigest()
        cache_key=f"{file_id}:{query}"
        if file_exists(file_id):
            if get_redis_client().exists(cache_key):
                return {"answer":get_redis_client().get(cache_key).decode()}
        if not file_exists(file_id):
            register_file(temp_file_path,file_id)
            print("File registered successfully.")
        hybrid_retriver=aceess_file(file_id)
        print("Retriever accessed successfully.")
        docs=hybrid_retriver.get_relevant_documents(query)
        response=" ".join([doc.page_content for doc in docs])
        print("Retrieved relevant context successfully",str(response))
        PROMPT=PromptTemplate(
        template=prompt_template,
        input_variables=["context","question"])
        prompt_template_instance=PROMPT.format(context=response,question=query)
        print("Prompt template formatted successfully",str(prompt_template_instance))
        rag_chain_response=llm.invoke(prompt_template_instance)
        print("RAG chain executed successfully",str(rag_chain_response))
        get_redis_client().setex(cache_key,3600,value=rag_chain_response)
        end=time.time()
        print("Total execution time:",end-start) 
        return {"answer":rag_chain_response,"execution_time":end-start}   
    except Exception as e:
        return str(e)


