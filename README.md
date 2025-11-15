# RAG-AI
Deploying Local AI with RAG, Ollama & ChromaDB 
With the rise of AI, businesses are seeking secure, cost-effective, and scalable solutions to leverage large language models without relying on cloud-based APIs. That's why I built a local AI stack using Ollama, ChromaDB, and RAG (Retrieval-Augmented Generation)—a powerful, self-hosted solution for enterprise AI.
🔹 Why Local AI? 
✅ Privacy & Security – Keep sensitive data in-house.
✅ Cost-Effective – No API costs or cloud fees.
✅ Customizable – Train AI on your own documents & PDFs.
✅ Faster Responses – No external latency, pure local processing.
🔧 My Stack:
🔹 Ollama – Runs LLMs locally (Mistral, Llama, etc.)
🔹 ChromaDB – Vector database for semantic search
🔹 RAG (Retrieval-Augmented Generation) – Enhances AI responses with real-time data
🔹 OpenAI WebUI – A simple web-based chat interface
💡 What Can This Do?
✅ Upload & process PDF documents
✅ Ask AI questions based on your custom data
✅ Get real-time, context-aware responses
✅ Deploy an API for seamless integration
🔍 Want to Set Up Your Own Local AI?
I’ve documented the full installation process, including Docker, Python setup, and API development. This guide walks you through:
\n
1️⃣ Deploying Ollama & ChromaDB with Docker
2️⃣ Downloading & running LLM models locally
3️⃣ Building a FastAPI backend for querying data
4️⃣ Adding PDF ingestion to enrich AI responses
5️⃣ Creating an AI assistant tailored to your business
📌 Full Guide Here 👉 https://lnkd.in/eG-RNbqB
========================================================
#for runing 
uvicorn rag-api:app --host 0.0.0.0 --port 5000 --workers 1 
#for query
curl -X POST "http://localhost:5000/query/" -H "Content-Type: application/json" -d '{"user_input": "آیا امکان غیرفعالسازی پرونده مالیاتی درکارپوشه وجود دارد؟"}'
\n
#for upload file for traning txt or json
curl -X POST "http://localhost:5000/upload_qa/" -F "file=@/home/db/bedon shenasname.json"
\n
curl -X POST "http://localhost:5000/upload_file/" -F "file=@/home/db/part1.txt"
======================================================================
Are you exploring local AI for your business? What challenges are you facing in AI deployment? Drop your thoughts in the comments! 👇
hashtag#AI hashtag#LocalAI hashtag#RAG hashtag#Ollama hashtag#ChromaDB hashtag#LLM hashtag#MachineLearning hashtag#opensource
