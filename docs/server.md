# Server documentation
This document describers the implementation of server component.

## Tech stack
Python, FastAPI, langchain, ChromaDB

## Brief descrption
The FastAPI application (`main.py`) includes:
  - POST /upload: Processes PDF files, creates embeddings, and stores them in ChromaDB
  - POST /chat: Retrieves relevant context and generates answers using GPT-4
  - DELETE /session/{session_id}: Optional cleanup endpoint
  - Proper error handling and validation using Pydantic models
  - Session management using UUIDs

**requirements.txt**
  - All necessary dependencies including FastAPI, LangChain, ChromaDB, and OpenAI libraries.

**To run the application:**
1. Install dependencies: pip install -r requirements.txt
2. Set your OpenAI API key: export OPENAI_API_KEY="your-key-here"
3. Run the server: python main.py

The API will be available at http://localhost:8000 with automatic documentation at /docs.


## How the vector database (ChromaDB) works in the solution:

**Vector Database Usage Flow:**

1. Document Processing & Embedding Creation (/upload endpoint)
    - PDF is loaded and split into chunks (1000 chars with 200 char overlap)
    - Each chunk is converted to a vector embedding using OpenAI's text-embedding-3-small
    - ChromaDB stores both the text chunks and their vector representations

2. Vector Storage

    - ChromaDB creates an in-memory vector index
    - Each document chunk is stored with its embedding vector
    - The vector store is kept in the global vector_stores dictionary, keyed by session ID

3. Similarity Search (/chat endpoint)

    - When a user asks a question, it's converted to a vector embedding
    - ChromaDB performs a similarity search to find the most relevant chunks
    - By default, it returns the top-k most similar chunks based on cosine similarity

4. RAG Pipeline

    - The retrieved chunks become the "context" for the LLM
    - The RetrievalQA chain passes this context to GPT-4
    - GPT-4 generates an answer based only on the provided context

**Key Benefits**

    - Semantic Search: Finds relevant content based on meaning, not just keywords
    - Scalability: Vector search is efficient even with large documents
    - Context Window Management: Only relevant chunks are sent to the LLM, staying within token limits

The vector database essentially acts as a semantic index of the PDF content, enabling accurate retrieval of relevant information for each query.