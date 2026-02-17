# Fusion Cyber Chatbot Backend

FastAPI-based backend for the Fusion Cyber Chatbot application.

## Setup

### Prerequisites
- Python 3.10+
- Virtual environment (venv)

### Installation

1. **Activate the virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Server

Start the development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, you can access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Project Structure

```
backend/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
├── venv/               # Virtual environment
└── README.md           # This file
```

## Available Endpoints

- `GET /` - Root endpoint (health check)
- `GET /health` - Health check endpoint
- `POST /chat` - Chat endpoint (placeholder)

## Next Steps

- Add database models and ORM (SQLAlchemy)
- Implement authentication (JWT, OAuth2)
- Add environment configuration (.env)
- Create modular route handlers (routers)
- Add request/response models with Pydantic
