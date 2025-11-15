# Ollama-RAG


Setting Up RAG with Ollama and ChromaDB


# Setting Up RAG with Ollama and ChromaDB





## Step 1: Install and Run Docker Containers





Ensure Docker is running on your system.





### 1.1 Run ChromaDB as a Docker Container


Run the following command to start ChromaDB:


```sh


docker run -d --name chromadb -p 8000:8000 chromadb/chroma


docker run -d --rm --name chromadb -p 8000:8000 -v ./chroma:/chroma/chroma -e IS_PERSISTENT=TRUE -e ANONYMIZED_TELEMETRY=TRUE chromadb/chroma


```


- `-d` runs the container in the background.


- `--name chromadb` gives the container a name.


- `-p 8000:8000` exposes it on port 8000.





To check if it's running:


```sh


docker ps


curl http://localhost:8000/api/v1/heartbeat


wget http://0.0.0.0:8000


```


If it returns `{ "heartbeat": "OK" }`, ChromaDB is working.





### 1.2 Run Ollama as a Docker Container


Run the following command:


```sh


docker run -d --name ollama -p 11434:11434 ollama/ollama


```


- Exposes Ollama’s API on port 11434.





To verify, run:


```sh


curl http://localhost:11434/api/tags


```


If it responds with available models, Ollama is working.





### 1.3 Run Open-webui


```sh


docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -e OLLAMA_API_BASE_URL=http://localhost:11434 -v open-webui-data:/app/backend/data --name open-webui --restart unless-stopped ghcr.io/open-webui/open-webui:latest


```





## Step 2: Download an LLM Model for Ollama


Ollama needs a model to generate responses. You can download one like Mistral:


```sh


ollama pull mistral


```


To list available models:


```sh


ollama list


```


To test if Ollama works, run:


```sh


ollama run mistral "Hello, how are you?"


```
## Step 3: Install Python and Required Libraries
You'll need Python for the backend API.

### 3.1 Install Python Dependencies
First, install Python (if not already installed), then create a virtual environment:
```sh
python -m venv rag_env
source rag_env/bin/activate   # For Linux/macOS
rag_env\Scripts\activate      # For Windows
```
Now install dependencies:
```sh
pip install chromadb requests fastapi uvicorn ollama llama-index langchain llama-index-readers-file llama-index-embeddings-openai pypdf
```

## Step 4: Create a Python API to Connect ChromaDB and Ollama
Create a file called `rag_api.py`.

# Step 5: starting rag_api.py service and uploading your file and query
```sh
uvicorn rag-api-v2:app --host 0.0.0.0 --port 5000 --workers 1
```
```sh
curl -X POST "http://localhost:5000/upload_qa/" -F "file=@/home/db/part2.json"
curl -X POST "http://localhost:5000/upload_file/" -F "file=@/home/db/part1.txt"
```
```sh
curl -X POST "http://localhost:5000/query/" -H "Content-Type: application/json" -d '{"user_input": "Are you my own AI?"}'
```

