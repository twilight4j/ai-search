# AI Search API

AI-powered product search API for e-commerce platform using FastAPI, Langchain, and FAISS.

## Features

- Natural language product search
- Vector-based similarity search
- Integration with Oracle RDB
- OpenAI-powered embeddings and LLM

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and fill in your configuration values.

4. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

- `GET /`: Health check endpoint
- `POST /search`: Search products using natural language query

## Project Structure

```
.
├── main.py              # FastAPI application
├── requirements.txt     # Project dependencies
├── .env                 # Environment variables (create from .env.example)
└── README.md           # This file
```

## Development

The project uses:
- FastAPI for the web framework
- Langchain for AI/ML pipeline
- FAISS for vector similarity search
- Oracle RDB for product data storage
- OpenAI for embeddings and LLM 