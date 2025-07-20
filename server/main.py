import os
import uuid
import tempfile
from typing import Dict
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException
from pydantic import BaseModel
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

# Initialize FastAPI app
app = FastAPI(title="Board Game Helper API", version="1.0.0")

# Global dictionary to store vector store retrievers by session ID
vector_stores: Dict[str, Chroma] = {}

# Pydantic models for request/response validation
class UploadResponse(BaseModel):
    session_id: str

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    result: str

# Custom prompt template for the QA chain
prompt_template = """You are a helpful board game assistant. Use the following pieces of context to answer the question at the end. If you don't know the answer from the context provided, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""

PROMPT = PromptTemplate(
    template=prompt_template, 
    input_variables=["context", "question"]
)

@app.get("/")
async def root():
    """Root endpoint to verify the API is running"""
    return {"message": "Board Game Helper API is running"}

@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile):
    """
    Upload a PDF document and process it for RAG.
    
    This endpoint:
    1. Saves the uploaded PDF to a temporary file
    2. Loads and splits the document into chunks
    3. Creates embeddings for each chunk
    4. Stores the embeddings in a Chroma vector store
    5. Returns a session ID for future queries
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Load PDF using PyPDFLoader
        loader = PyPDFLoader(temp_file_path)
        documents = loader.load()
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create embeddings using OpenAI's text-embedding-3-small
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create Chroma vector store from documents
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings
        )
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Store vector store in global dictionary
        vector_stores[session_id] = vector_store
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        return UploadResponse(session_id=session_id)
        
    except Exception as e:
        # Clean up temporary file in case of error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_document(request: ChatRequest):
    """
    Chat with the uploaded document using RAG.
    
    This endpoint:
    1. Retrieves the vector store for the given session ID
    2. Creates a RetrievalQA chain with the vector store
    3. Processes the user's query
    4. Returns the generated answer
    """
    # Validate session ID
    if request.session_id not in vector_stores:
        raise HTTPException(
            status_code=404, 
            detail=f"Session ID '{request.session_id}' not found. Please upload a document first."
        )
    
    try:
        # Retrieve vector store
        vector_store = vector_stores[request.session_id]
        
        # Create retriever from vector store
        retriever = vector_store.as_retriever()
        
        # Initialize ChatOpenAI with gpt-4-1106-preview
        llm = ChatOpenAI(
            model="gpt-4-1106-preview",
            temperature=0,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Create RetrievalQA chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=False
        )
        
        # Invoke chain with user's query
        result = qa_chain.invoke({"query": request.query})
        
        return ChatResponse(result=result["result"])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Optional: Add endpoint to clean up sessions
@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated vector store"""
    if session_id in vector_stores:
        del vector_stores[session_id]
        return {"message": f"Session {session_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Session ID '{session_id}' not found")

if __name__ == "__main__":
    import uvicorn
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY environment variable not set")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)