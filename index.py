import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from fastapi import HTTPException
from langchain_core.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.llms import Ollama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
import redis
splitter_technique=RecursiveCharacterTextSplitter(chunk_size=750,chunk_overlap=110)
embeddings=HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
dir="RAG_Document_Store"
os.makedirs(dir,exist_ok=True)
def file_exists(file_id:str):
    file_path=os.path.join(dir,file_id)
    return os.path.exists(file_path)
def get_redis_client():
    get_redis_client=redis.Redis(host='localhost',port=6379,db=0)
    return get_redis_client
def register_file(file_path,file_id):
    file_store=os.path.join(dir,file_id)
    os.makedirs(file_store,exist_ok=True)
    docs=PyPDFLoader(file_path)
    documents=docs.load()
    splitted_text=splitter_technique.split_documents(documents)
    bm25_retriver_instance=BM25Retriever.from_documents(splitted_text)
    bm25_retriver_instance.k=7
    faiss_store=FAISS.from_documents(documents=splitted_text,embedding=embeddings)
    faiss_store.save_local(os.path.join(file_store,"faiss"))
    with open(os.path.join(file_store,"bm25.pkl"),"wb") as f:
        import pickle
        pickle.dump(bm25_retriver_instance,f)
def aceess_file(file_id:str):
    try:
        import pickle
        with open(os.path.join(dir,file_id,"bm25.pkl"),"rb") as f:
            bm25_retriver_instance=pickle.load(f)
        faiss_store=FAISS.load_local(os.path.join(dir,file_id,"faiss"),embeddings,allow_dangerous_deserialization=True)
        relvent_text_faiss=faiss_store.as_retriever(search_kwargs={"k":3})
        hybrid_retriver=EnsembleRetriever(retrievers=[bm25_retriver_instance,relvent_text_faiss],weights=[0.4,0.6])
        return hybrid_retriver
    except Exception as e:
        raise HTTPException(status_code=500, detail=(str(e)+"Error in index.py"))

