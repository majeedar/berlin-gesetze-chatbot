# Berlin Gesetze Chatbot

> RAG-based chatbot for Berlin laws and regulations using open-source tools

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## 🎯 Project Overview

An intelligent chatbot system that helps users navigate Berlin's legal documents using Retrieval-Augmented Generation (RAG). The system scrapes, processes, and indexes laws from [gesetze.berlin.de](https://gesetze.berlin.de) to provide accurate, context-aware answers.

### Key Features

- 🔍 **Automated Scraping**: Collects laws and regulations from gesetze.berlin.de
- 📊 **Data Processing**: Cleans, chunks, and prepares documents for RAG
- 🧮 **Semantic Search**: Uses sentence-transformers for embeddings
- 💾 **Vector Database**: ChromaDB for efficient similarity search
- 🤖 **LLM Integration**: Groq API for fast, accurate responses
- 📦 **PostgreSQL Storage**: Structured metadata and document storage
- 🔄 **Apache Airflow**: Orchestrates data pipelines
- 🚀 **FastAPI Backend**: RESTful API for the chatbot
- 🎨 **React Frontend**: User-friendly chat interface

## ��️ Architecture
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     Frontend (React)            │
└──────────────┬──────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│      API (FastAPI)               │
├──────────────────────────────────┤
│   RAG Pipeline                   │
│   ├─ Text Processor              │
│   ├─ Embedding Generator         │
│   ├─ Vector Store (ChromaDB)     │
│   └─ LLM (Groq/Ollama)           │
└──────────────┬───────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌──────────┐    ┌───────────┐
│PostgreSQL│    │ ChromaDB  │
└──────────┘    └───────────┘
       ▲
       │
┌──────────────┐
│   Airflow    │
│  (Scraping)  │
└──────────────┘
```

## 📋 Prerequisites

- **OS**: Linux (Ubuntu 22.04+) or WSL2
- **RAM**: 16 GB minimum
- **Storage**: 50 GB free space
- **Software**:
  - Docker & Docker Compose
  - Python 3.10+
  - Git
  - Node.js 18+ (for frontend)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/majeedar/berlin-gesetze-chatbot.git
cd berlin-gesetze-chatbot
```

### 2. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 3. Start Services
```bash
# Start PostgreSQL, Redis, ChromaDB
make start

# Or manually with docker-compose
docker compose up -d postgres redis chromadb
```

### 4. Run Initial Scraping
```bash
# Open Jupyter notebook
jupyter notebook notebooks/gesetze_scraping_complete.ipynb

# Or run with Airflow
make phase1
```

### 5. Test RAG System
```bash
# Open RAG testing notebook
jupyter notebook notebooks/rag-testing/test_rag_prototype.ipynb
```

## 📁 Project Structure
```
berlin-gesetze-chatbot/
├── src/                          # Source code
│   ├── rag/                      # RAG pipeline modules
│   │   ├── text_processor.py    # Text chunking
│   │   ├── embeddings.py        # Embedding generation
│   │   ├── vector_store.py      # ChromaDB interface
│   │   └── rag_pipeline.py      # Complete pipeline
│   ├── database/                 # Database utilities
│   ├── api/                      # FastAPI backend
│   └── utils/                    # Helper functions
│
├── notebooks/                    # Jupyter notebooks
│   ├── gesetze_scraping_complete.ipynb
│   └── rag-testing/
│       └── test_rag_prototype.ipynb
│
├── airflow/                      # Airflow DAGs
│   └── dags/
│
├── services/                     # Microservices
│   ├── api/                      # Backend API
│   └── frontend/                 # React UI
│
├── config/                       # Configuration files
│   ├── rag_config.yaml
│   └── models.yaml
│
├── data/                         # Data storage
│   ├── raw/                      # Scraped documents
│   ├── processed/                # Processed chunks
│   └── embeddings/               # Vector embeddings
│
├── docker-compose.yml            # Docker services
├── Makefile                      # Development commands
└── requirements.txt              # Python dependencies
```

## 🛠️ Technology Stack

### Core Technologies

- **Python 3.10+**: Main programming language
- **Docker**: Containerization
- **PostgreSQL**: Relational database
- **ChromaDB**: Vector database
- **Redis**: Caching layer

### Data Pipeline

- **Apache Airflow**: Workflow orchestration
- **BeautifulSoup4**: Web scraping
- **Pandas**: Data processing

### RAG Components

- **sentence-transformers**: Text embeddings
- **LangChain**: RAG framework
- **Groq API**: LLM inference (Llama 3.1)
- **Ollama**: Local LLM alternative

### API & Frontend

- **FastAPI**: REST API backend
- **React**: Frontend framework
- **Nginx**: Web server

## 📖 Usage

### Makefile Commands
```bash
# Setup
make setup              # Initial project setup

# Development phases
make phase1             # Start data collection (Airflow)
make phase2             # Data processing
make phase3             # Generate embeddings
make phase4             # Test API
make phase5             # Full stack

# Service management
make start              # Start core services
make stop               # Stop all services
make logs               # View logs
make stats              # Resource usage

# Database
make db-shell           # PostgreSQL shell
make redis-cli          # Redis CLI

# Cleanup
make clean              # Remove all data
```

### Example Queries
```python
from src.rag.rag_pipeline import RAGPipeline
import yaml

# Load configuration
with open('config/rag_config.yaml') as f:
    config = yaml.safe_load(f)

# Initialize RAG
rag = RAGPipeline(config)

# Query
result = rag.query("Was regelt das Berliner Bauordnungsrecht?")
print(result['answer'])
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:
```bash
# Database
POSTGRES_USER=gesetze
POSTGRES_PASSWORD=your_password
POSTGRES_DB=gesetze

# LLM API (Groq)
LLM_PROVIDER=groq
LLM_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.1-8b-instant

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Vector Database
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

### RAG Configuration

Edit `config/rag_config.yaml`:
```yaml
chunking:
  chunk_size: 500      # Adjust chunk size
  chunk_overlap: 50

retrieval:
  top_k: 5             # Number of documents to retrieve
  score_threshold: 0.7

llm:
  temperature: 0.7     # LLM creativity
  max_tokens: 2048
```

## 📊 Data Pipeline

1. **Scraping**: Collects laws from gesetze.berlin.de
2. **Processing**: Cleans and normalizes text
3. **Chunking**: Splits documents into manageable pieces
4. **Embedding**: Generates vector representations
5. **Indexing**: Stores in ChromaDB
6. **Retrieval**: Finds relevant chunks for queries
7. **Generation**: Uses LLM to create answers

## 🧪 Testing
```bash
# Run unit tests
pytest tests/

# Test specific module
pytest tests/test_rag_pipeline.py

# Run with coverage
pytest --cov=src tests/
```

## 📈 Performance

- **Embedding Speed**: ~100 docs/second on CPU
- **Retrieval Latency**: <100ms for top-5 results
- **LLM Response Time**: 1-3 seconds (with Groq)
- **Memory Usage**: 4-6 GB RAM (without local LLM)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Berlin Senate for providing open access to legal documents
- Anthropic for Claude AI assistance
- Open-source community for amazing tools

## 📧 Contact

**Majeed** - [@majeedar](https://github.com/majeedar)

**Project Link**: [https://github.com/majeedar/berlin-gesetze-chatbot](https://github.com/majeedar/berlin-gesetze-chatbot)

## 🗺️ Roadmap

- [x] Web scraping pipeline
- [x] Document processing
- [x] RAG prototype
- [ ] FastAPI endpoints
- [ ] React frontend
- [ ] User authentication
- [ ] Deployment scripts
- [ ] Performance optimization
- [ ] Multi-language support
- [ ] Mobile app

## ⚠️ Disclaimer

This tool is for educational and research purposes. Always verify legal information with official sources.

---

**Built with ❤️ for the Berlin tech community**
