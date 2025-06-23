# AI Search API

AI-powered product search API for e-commerce platform using FastAPI, Langchain, and FAISS.

## Features

- Natural language product search
- Vector-based similarity search
- OpenAI-powered embeddings and LLM

## Setup

1. Create a virtual environment:
```bash
poetry shell
```

2. Install dependencies:
```bash
poetry update
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

- `GET /search`: Search products using natural language query

## Project Structure

```
.
├── /.db                # database
├── /core               # core packages initialized when the server starts up
├── /models             # response models
├── /services           # service package
├── /utils              # utility
├── .env                # env environment file (referenced by .env.example )
├── main.py             # FastAPI application
├── pyproject.toml      # project metadata and dependency
└── README.md           # README
```

## Development

The project uses:
- FastAPI for the web framework
- Langchain for AI/ML pipeline
- FAISS for vector similarity search
- OpenAI for embeddings and LLM 