# PiAxis Mini Detail Library

Hey there! This is a full-stack app that helps architects find the right building details for their projects. Think of it as a smart search engine that understands architectural contexts and suggests the best construction details based on what you're working with.

## What's This All About?

When you're designing a building, you need to figure out how different elements connect - like how a window meets an external wall, or how a slab connects to a wall. This app makes that easier by:

- **Searching through architectural details** with intelligent text search
- **Getting smart suggestions** based on your specific context (host element, adjacent element, and exposure conditions)
- **Using AI-powered recommendations** with RAG (Retrieval-Augmented Generation) to find the most relevant details

It's basically your architectural detail assistant that actually understands what you're looking for.

## The Stack

**Backend:**
- FastAPI (Python) - fast, modern, and makes building APIs actually fun
- PostgreSQL with pgvector - for storing details and doing vector similarity searches
- SQLAlchemy - handles all the database stuff
- Sentence Transformers - turns text into vectors for semantic search
- Google Gemini - generates human-friendly explanations (optional but cool)

**Frontend:**
- React + Vite - because nobody has time for slow builds
- Modern JS with hooks and all that good stuff

## Getting Started

### Prerequisites

You'll need:
- Python 3.11+ (the backend is picky about this)
- PostgreSQL with the pgvector extension
- Node.js and npm (for the frontend)
- A virtual environment tool (we use venv)

### Backend Setup

1. **Navigate to the backend folder:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source ./venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your environment variables:**

   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgresql://user:password@host:port/database
   GEMINI_API_KEY=your_api_key_here  # Optional - for AI explanations
   ```

5. **Make sure your database is ready:**

   You need PostgreSQL with pgvector extension installed. Your database should have:
   - A `details` table with columns: `id`, `title`, `category`, `tags`, `description`, `embedding`
   - A `detail_usage_rules` table for context-based matching
   - The pgvector extension enabled (`CREATE EXTENSION vector;`)

6. **Run the server:**
   ```bash
   python main.py
   ```

   The API will be running at `http://localhost:8000`. Check out the interactive docs at `http://localhost:8000/docs` - it's pretty slick.

### Frontend Setup

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the dev server:**
   ```bash
   npm run dev
   ```

   The app will open at `http://localhost:5173` (or whatever port Vite picks).

## Using the RAG Feature

The RAG (Retrieval-Augmented Generation) feature is the smart part of this app. Here's how to get it working:

1. **Make sure all dependencies are installed** (especially `sentence-transformers` and `google-generativeai`)

2. **Generate embeddings for your details:**
   ```bash
   curl -X POST http://localhost:8000/generate-embeddings
   ```
   This converts all your architectural details into vector embeddings so the AI can understand them semantically.

3. **Use the RAG suggestion endpoint:**
   ```bash
   curl -X POST http://localhost:8000/suggest-detail-rag \
     -H "Content-Type: application/json" \
     -d '{
       "host_element": "External Wall",
       "adjacent_element": "Slab",
       "exposure": "External"
     }'
   ```

The RAG system will:
- Take your context and turn it into a vector
- Find similar details in the database
- Rerank them to get the best matches
- Generate human-friendly explanations for why each detail fits

Pretty cool, right?

## API Endpoints

Here's what you can do with the API:

### Basic Endpoints
- `GET /details` - List all architectural details
- `GET /details/search?q=<query>` - Search details by keywords
- `POST /suggest-detail` - Get a suggestion based on exact context matching

### RAG Endpoints (The Smart Stuff)
- `POST /suggest-detail-rag` - Get AI-powered suggestions with explanations
- `POST /generate-embeddings` - Generate vector embeddings for all details

### Security Endpoints (Row-Level Security)
- `GET /security/details` - Get details based on user role
  - Requires headers: `X-USER-EMAIL` and `X-USER-ROLE`
  - Admins see everything, architects see standard details only

## Common Issues

**"503 Service Unavailable" on `/suggest-detail-rag`:**
- Make sure you installed all the RAG dependencies
- Restart the server after installing packages
- Check that the import worked: `python -c "from rag_service import rag_suggest_detail; print('Works!')"`

**Database connection errors:**
- Double-check your `DATABASE_URL` in the `.env` file
- Make sure PostgreSQL is running
- Verify the pgvector extension is installed: `CREATE EXTENSION IF NOT EXISTS vector;`

**Slow first request:**
- The sentence transformer model downloads on first use (it's about 80MB)
- Subsequent requests will be much faster

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app with all the endpoints
│   ├── rag_service.py       # RAG logic (embeddings, search, AI)
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Your secrets (don't commit this!)
│
└── frontend/
    ├── src/                 # React components and stuff
    ├── package.json         # Node dependencies
    └── vite.config.js       # Vite configuration
```

## Development Notes

- The backend uses CORS middleware with `allow_origins=["*"]` - you'll want to lock this down for production
- The Gemini API key is optional - the app falls back to template explanations if it's missing
- Vector search requires the `embedding` column to be populated - run `/generate-embeddings` first
- The sentence transformer models get cached in `/tmp/sentence_transformers` on Linux

## What's Next?

Some ideas if you want to extend this:
- Add more sophisticated reranking algorithms
- Implement user authentication properly
- Add image support for architectural details
- Build a feedback loop to improve suggestions over time
- Add autocomplete for search (there's a 404 endpoint waiting for it!)

## Need Help?

If something's not working:
1. Check the API docs at `http://localhost:8000/docs`
2. Look at the backend logs - FastAPI is pretty good about telling you what's wrong
3. Make sure all dependencies are installed correctly
4. Verify your database schema matches what the code expects

Happy building!
