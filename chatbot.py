from datetime import datetime
from fastapi import APIRouter, Form, HTTPException
import tempfile
import redis
from RAG_APP.RAG import get_redis_client
from RAG_APP.RAG import llm
from RAG_APP.RAG import prompt_template
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
import os
import tempfile
from RAG_APP.index import register_file, aceess_file, file_exists
start=datetime.now()
"""splitter=RecursiveCharacterTextSplitter(chunk_size=750,chunk_overlap=110)
embeddings=HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")
"""
model=Ollama(model="phi3:mini",temperature=0.3,base_url="http://localhost:11434",num_predict=512)
pdf_path=r"C:\Users\madhugoud\Downloads\AI_Shopkeeper_Full_Documentation.pdf"
print(os.path.exists(pdf_path))
prompt_template = """You are a help assistant for a login screen.

Answer only about:
- Login
- Account creation
- App features
- Basic usage

Rules:
- Maximum 3 bullet points.
- No paragraphs.
- No technical terms.
- If unsure, say you don’t know.

Context:
{retrieved_documents}

Question:
{user_query}

Answer:
"""
with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as temp_file:
    with open(pdf_path,"rb") as f:
        content=f.read()
    temp_file.write(content)
    temp_file_path=temp_file.name
file_id="chatbot_data_file"
if not file_exists(file_id):
    register_file(temp_file_path,file_id)
    print("File registered successfully.")
router=APIRouter()

# Simple health check endpoint
@router.get("/chatbot/health")
async def chatbot_health():
    return {"status": "ok", "message": "Chatbot service is running"}

@router.post("/chatbot/")
async def get_answer_from_pdf(query: str = Form(...)):
    import sys
    print(f"\n{'='*50}", file=sys.stderr)
    print(f"CHATBOT REQUEST RECEIVED", file=sys.stderr)
    print(f"Query parameter: {repr(query)}", file=sys.stderr)
    print(f"Query type: {type(query)}", file=sys.stderr)
    print(f"Query is None: {query is None}", file=sys.stderr)
    print(f"Query stripped: {repr(query.strip()) if query else 'N/A'}", file=sys.stderr)
    print(f"{'='*50}\n", file=sys.stderr)
    
    if not query or query.strip() == "":
        return {
            "message": "Please ask a question about our app. For example: 'How do I login?' or 'What are the app features?'"
        }
    
    try:
        # Check cache first
        cache_key = f"{file_id}:{query}"
        try:
            if get_redis_client().exists(cache_key):
                cached_answer = get_redis_client().get(cache_key).decode()
                print(f"Returning cached response for: {query}")
                return {"message": cached_answer}
        except Exception as cache_err:
            print(f"Cache lookup failed (non-critical): {cache_err}")
        
        # Ensure file is registered
        if not file_exists(file_id):
            try:
                register_file(temp_file_path, file_id)
                print("File registered successfully.")
            except Exception as reg_err:
                print(f"File registration error: {reg_err}")
                raise HTTPException(status_code=500, detail=f"Failed to register PDF file: {str(reg_err)}")
        
        # Access retriever
        try:
            hybrid_retriever = aceess_file(file_id)
            print("Retriever accessed successfully.")
        except Exception as ret_err:
            print(f"Retriever access error: {ret_err}")
            raise HTTPException(status_code=500, detail=f"Failed to access document retriever: {str(ret_err)}")
        
        # Retrieve documents
        try:
            docs = hybrid_retriever.get_relevant_documents(query)
            print(f"Number of documents retrieved: {len(docs)}")
            if len(docs) == 0:
                return {"message": "I couldn't find any relevant information in the documentation to answer your question."}
        except Exception as doc_err:
            print(f"Document retrieval error: {doc_err}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve documents: {str(doc_err)}")
        
        # Prepare context and prompt
        try:
            context = " ".join([doc.page_content for doc in docs])
            prompt = prompt_template.format(retrieved_documents=context, user_query=query)
            print("Prompt prepared successfully.")
        except Exception as prompt_err:
            print(f"Prompt preparation error: {prompt_err}")
            raise HTTPException(status_code=500, detail=f"Failed to prepare prompt: {str(prompt_err)}")
        
        # Invoke model
        try:
            answer = model.invoke(prompt)
            print("Model invoked successfully.")
            if not answer or answer.strip() == "":
                return {"message": "I'm having trouble responding right now. Please try again."}
        except Exception as model_err:
            print(f"Model invocation error: {model_err}")
            # Fallback response when Ollama is not available
            if "connection" in str(model_err).lower() or "refused" in str(model_err).lower():
                return {
                    "message": "The AI assistant service is currently unavailable. Please ensure Ollama is running on localhost:11434"
                }
            raise HTTPException(status_code=503, detail=f"Assistant service error: {str(model_err)}")
        
        # Cache the answer
        try:
            get_redis_client().set(cache_key, answer, ex=3600)
        except Exception as cache_set_err:
            print(f"Cache set failed (non-critical): {cache_set_err}")
        
        end = datetime.now()
        print(f"Time taken: {end - start}")
        return {"message": answer}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in chatbot endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



