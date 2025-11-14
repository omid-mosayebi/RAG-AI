from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import ollama
import chromadb
import pypdf
import hashlib
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = FastAPI()

# Connect to ChromaDB running in Docker
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_or_create_collection(name="rag_collection")

# Define text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

# In-memory cache for quick responses
cache = {}

def get_text_hash(text):
    """Generate a unique hash for a given text chunk."""
    return hashlib.md5(text.encode()).hexdigest()

class QueryRequest(BaseModel):
    user_input: str

def extract_text_from_file(file: UploadFile):
    """Extract text from a PDF or text file."""
    try:
        if file.filename.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(file.file)
            text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
        elif file.filename.endswith(".txt"):
            text = file.file.read().decode("utf-8")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload a PDF or text file.")
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting text: {str(e)}")

def store_text_chunks(text_chunks, source_type="document", metadata_extra={}):
    """Generate embeddings and store text chunks in ChromaDB."""
    try:
        embeddings = [
            ollama.embeddings(model="nomic-embed-text", prompt=chunk)["embedding"]
            for chunk in text_chunks
        ]

        collection.add(
            ids=[get_text_hash(chunk) for chunk in text_chunks],
            embeddings=embeddings,
            metadatas=[{"text": chunk, "source": source_type, **metadata_extra} for chunk in text_chunks]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing embeddings: {str(e)}")

@app.post("/upload_file/")
async def upload_file(file: UploadFile = File(...)):
    """Extract text from a file and store embeddings in ChromaDB."""
    text = extract_text_from_file(file)
    text_chunks = text_splitter.split_text(text)
    store_text_chunks(text_chunks, source_type="document", metadata_extra={"filename": file.filename})

    return {"message": f"File '{file.filename}' processed and stored in ChromaDB"}


# Add this to your FastAPI script to debug stored data
@app.get("/debug_chromadb/")
async def debug_chromadb():
    try:
        results = collection.get()
        return {"stored_data": results}
        return {"stored_metadata": results.get("metadatas", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stored data: {str(e)}")



@app.post("/upload_qa/")
async def upload_qa_file(file: UploadFile = File(...)):
    """Upload a JSON file with QA pairs and store in ChromaDB."""
    try:
        qa_data = json.load(file.file)
        for entry in qa_data:
            question, answer = entry.get("question"), entry.get("answer")
            if not question or not answer:
                continue
            print(f"Storing: Q: {question}")  # Debugging
            print(f"          **********          ")  # Debugging
            print(f"A: {answer}")  # Debugging
            print(f"_______________________________________")

            store_text_chunks([answer], source_type="qa", metadata_extra={"question": question})

        return {"message": "QA pairs stored successfully in ChromaDB"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing QA file: {str(e)}")

@app.post("/query_qa/")
async def query_rag(request: QueryRequest):
    try:
        print(f"User Query: {request.user_input}")  # Debugging

        # Check cache for quick response
        if request.user_input in cache:
            return {"response": cache[request.user_input]}

        # Generate embedding for the user's input
        embedding = ollama.embeddings(model="nomic-embed-text", prompt=request.user_input)["embedding"]
        print("Generated Embedding:", embedding)  # Debugging

        # Query ChromaDB for relevant documents
        results = collection.query(
            query_embeddings=[embedding],
            n_results=300,  # Retrieve top 3 results
            include=["metadatas", "documents"]  # Include metadata and documents in the results
        )
        print("Raw ChromaDB Query Response:", results)  # Debugging

        # Check if results are empty
        if not results or not results["metadatas"]:
            return {"response": "No relevant data found."}

        # Extract metadata and documents
        metadatas = results["metadatas"][0]
        documents = results["documents"][0]

        # Debugging: Print retrieved metadata and documents
        print("Retrieved Metadata:", metadatas)
        print("Retrieved Documents:", documents)

        # Find the most relevant QA pair
        best_match = None
        best_score = float("-inf")

        for meta, doc in zip(metadatas, documents):
            # Retrieve the stored question from metadata
            stored_question = meta.get("question", "")
            if not stored_question:
                continue

            # Calculate similarity between the user's input and the stored question
            question_embedding = ollama.embeddings(model="nomic-embed-text", prompt=stored_question)["embedding"]
            similarity_score = sum([a * b for a, b in zip(embedding, question_embedding)])  # Cosine similarity (dot product)

            # Track the best match
            if similarity_score > best_score:
                best_score = similarity_score
                best_match = {
                    "question": stored_question,
                    "answer": doc,  # The associated answer (document chunk)
                }

        # If no match is found, return a default response
        if not best_match:
            return {"response": "No relevant data found."}

        print("Best Match:", best_match)  # Debugging

        # Use the best match to generate a response
        context = best_match["answer"]
        prompt = f"""
        شما به هوش مصنوعی شرکت وثوق دسترسی دارید. اگر سوالی دارید خوشحال خواهم شد که از طرف شرکت معتمد مالیاتی وثوق پاسخگو باشم.
        
        Context:
        {context}

        User Question:
        {request.user_input}

        Answer:
        """
        print("Prompt:", prompt)  # Debugging

        # Generate the response using Ollama
        response = ollama.chat(model="partai/dorna-llama3:latest", messages=[{"role": "user", "content": prompt}])
        print("Raw Model Response:", response)  # Debugging

        # Cache the response for future queries
        cache[request.user_input] = response["message"]["content"]
        return {"response": response["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/query/")
async def query_rag(request: QueryRequest):
    try:
        print(f"User Query: {request.user_input}")  # Debugging
        if request.user_input in cache:
            return {"response": cache[request.user_input]}

        embedding = ollama.embeddings(model="nomic-embed-text", prompt=request.user_input)["embedding"]
        print("Generated Embedding:", embedding)  # Debugging

        results = collection.query(query_embeddings=[embedding], n_results=30000)
        print("Raw ChromaDB Query Response:", results)  # Debugging
        if not results or not results["metadatas"]:
            return {"response": "No relevant data found."}

        threshold = 90  # Adjust based on results
        retrieved_texts = [
            meta.get("text", "") 
            for meta_list in results.get("metadatas", []) 
            for meta in meta_list
        ]

        print("Raw Distances:", results["distances"][0])  # Debugging
        print("Filtered Retrieved Texts:", retrieved_texts)  # Debugging
        context = "\n".join(retrieved_texts)
        if not context.strip():
            return {"response": "No relevant data found."}

        print("Final Retrieved Context:", context)  # Debugging
        # Debugging
        print("Retrieved Context:", context)

        prompt = f"""
      IT's My AI

        Context:
        {context}

        User Question:
        {request.user_input}

        Answer:
        """
        print(" PROMT Vosouq : " , prompt) # Debugging
        response = ollama.chat(model="partai/dorna-llama3:latest", messages=[{"role": "user", "content": prompt}])
        #response = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
        print("Raw Model Response:", response)  # Debugging
        cache[request.user_input] = response["message"]["content"]
        return {"response": response["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

