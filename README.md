# Observability AI Agent

An intelligent observability platform built on **RAG (Retrieval-Augmented Generation) Agent Architecture** that leverages AI to analyze system logs and tickets, providing automated insights and query capabilities for infrastructure monitoring and incident management.

## Overview

This project implements a **RAG (Retrieval-Augmented Generation) Agent Architecture** that combines the power of Large Language Models (LLMs) with vector databases to create an intelligent observability system. The RAG approach enables the system to retrieve relevant context from your logs and tickets before generating responses, ensuring accurate and contextually-aware answers to your queries.

![Architecture Diagram](images/arch.png)

### RAG Architecture Benefits

- **Contextual Accuracy**: Retrieves relevant log entries and tickets before generating responses
- **Real-time Knowledge**: Works with your actual data, not just pre-trained knowledge
- **Semantic Search**: Uses vector embeddings to find semantically similar content
- **Scalable**: Handles large volumes of logs and tickets efficiently

![RAG Architecture](images/rag-overview.png)

### Key Features

- **RAG-Powered Analysis**: Retrieval-Augmented Generation for contextually accurate responses
- **AI-Powered Log Analysis**: Query your logs using natural language with semantic understanding
- **Intelligent Ticket Management**: Automated ticket generation and analysis with context retrieval
- **Vector Search**: Advanced semantic search capabilities using Qdrant vector database
- **LangChain Agents**: Sophisticated AI agents that can reason and use tools
- **RESTful API**: FastAPI-based backend for programmatic access
- **Interactive UI**: Streamlit-based web interface for easy interaction
- **Docker Support**: Containerized deployment with Docker Compose

## RAG Agent Architecture

The system implements a sophisticated RAG (Retrieval-Augmented Generation) architecture with the following key components:

### Core RAG Components

- **Observability Engine**: Core RAG agent powered by LangChain and OpenAI that orchestrates retrieval and generation
- **Vector Store**: Qdrant database storing embedded representations of logs and tickets
- **Embedding Pipeline**: Converts logs and tickets into high-dimensional vectors for semantic search
- **Retrieval System**: Finds relevant context based on semantic similarity to user queries
- **Generation Layer**: LLM that generates responses augmented with retrieved context

### Supporting Infrastructure

- **Log Ingestor**: Processes, chunks, and vectorizes log files for the RAG pipeline
- **Ticket System**: Generates and manages incident tickets with vector embeddings
- **API Layer**: FastAPI endpoints exposing RAG capabilities
- **Web Interface**: Streamlit dashboard for interactive RAG queries

### RAG Workflow

1. **Ingestion**: Logs and tickets are processed, chunked, and embedded into vectors
2. **Storage**: Vector embeddings are stored in Qdrant with metadata
3. **Query**: User submits natural language query
4. **Retrieval**: System finds semantically similar content from vector store
5. **Augmentation**: Retrieved context is combined with the user query
6. **Generation**: LLM generates contextually-aware response

## Project Structure

```
observability-ai-agent/
├── docker-compose.yml             # Docker services configuration
├── Dockerfile                     # Container build instructions
├── requirements.txt               # Python dependencies
├── images/                        # Documentation images
├── ingest-tracker/                # Ingestion tracking
│   ├── ingested_files.json        # Tracker for ingested log files
│   └── ingested_tickets.json      # Tracker for ingested tickets
├── logs/                          # Application logs
├── src/                           # Source code
│   ├── api.py                     # FastAPI application
│   ├── app.py                     # Streamlit web interface
│   ├── log_generator.py           # Log generation utilities
│   ├── log_ingestor.py            # Log ingestion into Vector DB
│   ├── observability_engine.py    # Core AI engine
│   ├── ticket_generator.py        # Ticket generation
│   └── ticket_ingestor.py         # Ticket ingestion into Vector DB
├── static-logs/                   # Sample log files
└── tickets/                       # Generated tickets
```

## Prerequisites

- Python 3.11+
- Docker and Docker Compose
- OpenAI API key
- Qdrant vector database (cloud or self-hosted)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd observability-ai-agent
```

### 2. Environment Setup

Copy the `.env` file and configure your API keys:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=your_qdrant_url
QDRANT_CLOUD_API_KEY=your_qdrant_api_key

# Optional: LangChain Tracing
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_TRACING_V2=true

# Configuration
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_MODEL=gpt-4-mini
COLLECTION_NAME=aks_logs
DEFAULT_K=5
THRESHOLD_LIMIT=0.2
```

### 3. Docker Deployment (Recommended)

```bash
# Build and start services
docker-compose up --build

# Access the applications
# API: http://localhost:8000/docs
# Streamlit UI: http://localhost:8501
```

### 4. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
cd src
uvicorn api:app --host 0.0.0.0 --port 8000

# Start the Streamlit app (in another terminal)
cd src
streamlit run app.py --server.port=8501
```

### 5. Running through CLI

```bash
# Install dependencies
pip install -r requirements.txt

# Generate sample logs
cd src
python log_generator.py <Date YYYY-MM-DD> <Number of logs>

# Generate sample tickets
cd src
python ticket_generator.py <Date YYYY-MM-DD> <Number of tickets>

# Ingest logs and tickets
cd src
python log_ingestor.py
python ticket_ingestor.py

# Query through CLI
cd src
python observability_engine.py
```

## Usage

### Web Interface (RAG Queries)

1. Navigate to `http://localhost:8501`
2. Use natural language to query your logs and tickets - the RAG system will retrieve relevant context and generate accurate responses
3. Examples:
   - "Show me all error logs from yesterday" - _RAG retrieves matching error logs and provides detailed analysis_
   - "What tickets occurred in the last 24 hours?" - _RAG finds recent tickets and summarizes incidents_
   - "Find logs related to authentication failures" - _RAG performs semantic search for auth-related issues_
   - "Analyze the root cause of database connection errors" - _RAG retrieves relevant logs and provides diagnostic insights_

### API Endpoints

The FastAPI server provides several endpoints:

- `POST /generate-logs` - Generate sample logs for testing
- `POST /ingest-logs` - Ingest log files into the vector database
- `POST /generate-tickets` - Generate simulating incident tickets
- `POST /ingest-tickets` - Ingest ticket files into the vector database

### API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Configuration

Key configuration options in `.env`:

| Variable          | Description                   | Default                |
| ----------------- | ----------------------------- | ---------------------- |
| `OPENAI_API_KEY`  | OpenAI API key for LLM access | Required               |
| `QDRANT_URL`      | Qdrant database URL           | Required               |
| `EMBEDDING_MODEL` | OpenAI embedding model        | text-embedding-3-small |
| `RETRIEVAL_MODEL` | LLM model for queries         | gpt-5-mini             |
| `COLLECTION_NAME` | Qdrant collection for logs    | aks_logs               |
| `DEFAULT_K`       | Number of results to retrieve | 5                      |
| `THRESHOLD_LIMIT` | Similarity threshold          | 0.2                    |

## Development

### Extending the AI Engine

The observability engine uses LangChain agents. To add new capabilities:

1. Define new tools in `observability_engine.py`
2. Update the agent initialization
3. Test with the Streamlit interface

## Dependencies

Key Python packages for RAG implementation:

- **LangChain**: RAG agent framework and orchestration
- **OpenAI**: LLM for generation and embedding models for retrieval
- **Qdrant**: Vector database for storing and searching embeddings
- **FastAPI**: Web API framework for RAG endpoints
- **Streamlit**: Interactive web interface for RAG queries
- **Pydantic**: Data validation and modeling
- **Tiktoken**: Token counting for optimal chunking strategies

## License

This project is licensed under the terms specified in the LICENSE file.
