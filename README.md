# msft-ai-hackathon-2026-analyzer:  

## TrustLens AI

### TrustLens AI is a governed RAG system that delivers source backed, low hallucination answer for compliance critical industries.

## Problem

Existing AI systems generate hallucinated and unverifiable responses, creating risks in compliance environments.

## Innovation

TrustLens uses a dual-layer AI system: Analyzer AI + Supervisor AI (verification)

- Analyzer AI generates insights from retrieved document data
- Supervisor AI evaluates the response for accuracy and completeness
- The system assigns a confidence score to each output
- Responses are always traceable to source documents


![TrustLens UI](https://drive.google.com/uc?export=view&id=1aG0EdjtgsoZewyRNIfUhFUrPelQZOCBb)

![YouTube Video]([https://youtu.be/UBquG0yevVU](https://youtu.be/UBquG0yevVU))

  

TrustLens An Azure RAG starter that:

- uploads files into Azure Blob Storage
- stores docs, images, and videos in separate containers
- extracts text from PDFs, DOCX, TXT, and Markdown
- chunks content for retrieval
- generates embeddings with Azure OpenAI
- indexes chunks into Azure AI Search
- searches with hybrid keyword + vector retrieval

## Project structure

```text
msft-ai-hackathon-2026-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── blob_service.py
│   ├── parsers.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── search_index.py
│   └── ingest_service.py
├── scripts/
│   └── create_search_index.py
├── .env.example
├── requirements.txt
└── README.md
```

## Architecture

```text
User Upload
   ↓
FastAPI API
   ↓
Azure Blob Storage
   ↓
Parsing + Chunking + Embeddings
   ↓
Azure AI Search
   ↓
Hybrid Search Results
```

## Azure resources

### 1. Azure Blob Storage
Create one storage account with these containers:

- `documents`
- `images`
- `videos`
- `raw`

Recommended for a low-cost demo:

- Performance: `Standard`
- Redundancy: `LRS`
- Access tier: `Hot`
- Public access: `Private (no anonymous access)`

### 2. Azure AI Search
Create a search service and used an admin key.

### 3. Azure OpenAI
Deploy an embeddings model.
A low-cost default is often:

- deployment name: your custom Azure deployment for `text-embedding-3-small`
- dimensions: `1536`

## Setup

### 1. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your environment file

```bash
cp .env.example .env
```

Fill in your real Azure values.

### 4. Create the Azure AI Search index

```bash
python scripts/create_search_index.py
```

### 5. Run the API

```
uvicorn app.main:app --reload
```

Open Swagger docs at:

```text
http://127.0.0.1:8000/docs
```

## Endpoints  [API](https://trustlens-fybxdsfqakhggqdr.westus2-01.azurewebsites.net/docs)

### `GET /health`
Basic health check.

### `POST /upload`
Uploads a file to Blob Storage and indexes its content into Azure AI Search.

Supported now:

- `.pdf`
- `.docx`
- `.txt`
- `.md`
- image/video uploads are stored now and indexed with placeholder text

### `POST /search`
Searches the index using hybrid retrieval.

Example request body:

```json
{
  "query": "what does the PDF say about onboarding?",
  "top_k": 5
}
```

To test `/search`, replace the `query` string in the JSON body with a phrase from the file you uploaded.

## Notes on Google and Microsoft files

- Microsoft files like PDF and DOCX can be uploaded directly.
- Google Docs should usually be exported first to PDF, DOCX, TXT, or Markdown before upload.
- Blob Storage stores files; it does not convert Google-native formats by itself.

## Good next upgrades

- Add Azure AI Vision OCR for images
- Add a transcript pipeline for video files
- Add metadata filters like source type or upload date
- Add a `/chat` endpoint that sends retrieved chunks to an LLM
- Add Docker support for easier deployment
