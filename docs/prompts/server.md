You are an expert Python developer specializing in building AI-powered backend services. Your task is to create a complete, production-ready FastAPI application that functions as the backend for a board game rule assistant.

Referencing the architecture document provided, implement the backend using Python, FastAPI, and LangChain.

### **Core Requirements:**

1.  **Framework:** Use `FastAPI`.
2.  **AI Orchestration:** Use the `LangChain` library for all major AI-related tasks.
3.  **LLM for Generation:** Use OpenAI's `gpt-4-1106-preview` model for the final answer generation step.
4.  **Embedding Model:** Use OpenAI's `text-embedding-3-small` for creating vector embeddings from text chunks.
5.  **Vector Store:** Use `ChromaDB` as the in-memory vector store. The application should manage the lifecycle of the vector store for each uploaded document. Do not persist the database to disk for this implementation.
6.  **PDF Parsing:** Use `PyPDFLoader` from LangChain to load and parse the uploaded PDF documents.

### **API Endpoints to Implement:**

1.  **`POST /upload`**
    * Accepts a file upload (`UploadFile`).
    * This endpoint should be **asynchronous**.
    * **Logic:**
        * Save the uploaded PDF to a temporary file on disk.
        * Use `PyPDFLoader` to load the document from the file path.
        * Use `RecursiveCharacterTextSplitter` from LangChain to split the document into chunks (use a chunk size of 1000 and an overlap of 200).
        * Use `OpenAIEmbeddings` (configured for `text-embedding-3-small`) to create embeddings for each chunk.
        * Initialize a `Chroma` vector store from the documents and their embeddings.
        * **Crucially**, store the created `Chroma` vector store retriever in a global dictionary, using a unique session ID (e.g., a UUID) as the key.
        * Return a JSON response containing the `session_id`.

2.  **`POST /chat`**
    * Accepts a JSON body with two fields: `session_id` (string) and `query` (string).
    * **Logic:**
        * Retrieve the correct `Chroma` vector store retriever from the global dictionary using the provided `session_id`. If the ID is not found, return a 404 error with a clear message.
        * Create a LangChain `RetrievalQA` chain.
        * Configure the chain with a `ChatOpenAI` instance (model `gpt-4-1106-preview`).
        * Use the retrieved vector store's `.as_retriever()` method for the chain.
        * Define a custom prompt template for the chain that strictly instructs the model to answer based *only* on the provided context, as outlined below.
        * Invoke the chain with the user's `query`.
        * Return the `result` from the chain in a JSON response.

### **Code Structure and Best Practices:**

* Create a main `main.py` file for the FastAPI application.
* Use Pydantic models for request and response bodies to ensure type safety and generate accurate OpenAPI documentation.
* Implement proper error handling (e.g., for missing `session_id`, file processing errors).
* Include all necessary imports.
* Add comments to explain the key parts of the RAG pipeline implementation.
* Ensure you have a mechanism to provide the `OPENAI_API_KEY`. The code should expect it as an environment variable.
* Provide a `requirements.txt` file listing all dependencies.

### **Example Prompt Template for the QA Chain:**

```
prompt_template = """You are a helpful board game assistant. Use the following pieces of context to answer the question at the end. If you don't know the answer from the context provided, just say that you don't know, don't try to make up an answer.

{context}

Question: {question}
Helpful Answer:"""
```

Please generate the complete Python code for the `main.py` file and the corresponding `requirements.txt` file.
