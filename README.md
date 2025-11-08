# PBM Auto Conversion System

AI-powered data transformation application that intelligently parses, analyzes, and transforms data files using LangChain and LLMs

## 🎉 Project Status: Backend Complete!

**Backend: 100% Complete** ✅  
**Frontend: Setup Complete** ⏳ (Implementation guide ready)

## Features

- 🎯 **Multi-Format Support**: CSV, Excel, TXT, Pipe Delimited, Flat File (position-based)
- 🤖 **AI-Powered Mapping**: LangChain + OpenAI for intelligent column mapping recommendations
- 📊 **Interactive Dashboard**: Visual mapping interface with confidence scores
- 🔄 **Template System**: Save and reuse transformation templates
- 📦 **Batch Processing**: Handle large files up to 10GB
- 👥 **Multi-User**: Authentication and user management via Supabase
- 🚀 **41 API Endpoints**: Complete RESTful API

## Tech Stack

### Backend (Complete)
- **Framework**: FastAPI (Python 3.10+)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **AI/LLM**: LangChain + OpenAI (primary), Hugging Face (fallback)
- **File Processing**: Pandas, openpyxl
- **Background Jobs**: AsyncIO

### Frontend (Setup Complete)
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **State**: Zustand
- **HTTP**: Axios

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (optional)
- Supabase account

### 1. Clone Repository

```bash
git clone <repository-url>
cd pbm-auto-conv
```

### 2. Setup Environment Variables

Copy `.env.example` and fill in your credentials:

```bash
# Backend
cp .env.example backend/.env

# Frontend
cp .env.example frontend/.env
```

Required environment variables:
- `SUPABASE_URL` and `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `SECRET_KEY`

### 3. Option A: Docker (Recommended)

```bash
docker-compose up --build
```

- Backend: http://localhost:8000
- Frontend: http://localhost:80
- API Docs: http://localhost:8000/api/docs

### 3. Option B: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Documentation

### Essential Guides
- **[BACKEND_COMPLETE_SUMMARY.md](BACKEND_COMPLETE_SUMMARY.md)** - Complete API reference
- **[PHASE_7_GUIDE.md](PHASE_7_GUIDE.md)** - Frontend implementation guide
- **[SUPABASE_SETUP.md](SUPABASE_SETUP.md)** - Database setup
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions

### Phase Documentation
- [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Original 30-day plan
- [PHASE_2_SUMMARY.md](PHASE_2_SUMMARY.md) - Backend Core
- [PHASE_3_SUMMARY.md](PHASE_3_SUMMARY.md) - File Parsing
- [PHASE_4_SUMMARY.md](PHASE_4_SUMMARY.md) - AI Integration
- [PHASE_5_SUMMARY.md](PHASE_5_SUMMARY.md) - Batch Processing
- [PHASE_6_SUMMARY.md](PHASE_6_SUMMARY.md) - Data Transformation

## Backend API Endpoints (41 Total)

### Authentication (7)
- POST `/auth/register` - Register user
- POST `/auth/login` - Login
- GET `/auth/me` - Get profile
- POST `/auth/logout` - Logout
- And more...

### File Management (5)
- POST `/files/upload` - Upload file (up to 10GB)
- GET `/files/` - List files
- GET `/files/{id}/download` - Download
- And more...

### AI Mapping (4)
- POST `/ai/generate-mappings` - Generate mappings
- POST `/ai/calculate-similarity` - Column similarity
- And more...

### Transformation (4)
- POST `/transform/execute` - Transform file
- POST `/transform/preview` - Preview results
- And more...

### Jobs, Templates, Parsing (21 more endpoints)

See [BACKEND_COMPLETE_SUMMARY.md](BACKEND_COMPLETE_SUMMARY.md) for complete API reference.

## Project Structure

```
pbm-auto-conv/
├── backend/              # FastAPI backend (COMPLETE)
│   ├── app/
│   │   ├── api/v1/      # 41 API endpoints
│   │   ├── core/        # Config, auth, security
│   │   ├── services/    # Business logic
│   │   ├── models/      # Database models
│   │   └── schemas/     # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/            # React frontend (SETUP COMPLETE)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── store/
│   ├── package.json
│   └── Dockerfile
├── memory-bank/         # Project documentation
├── docker-compose.yml
└── README.md
```

## Testing the Backend

The backend is fully functional and can be tested immediately:

```bash
cd backend
uvicorn app.main:app --reload
```

Visit http://localhost:8000/api/docs for interactive API documentation.

### Example API Call

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Upload file
curl -X POST http://localhost:8000/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"
```

## Capabilities

### File Format Support

**Input:** CSV, Excel (.xls, .xlsx), TXT, Pipe-delimited, Flat File (position-based)  
**Output:** CSV, Excel, JSON, TSV, Pipe-delimited, Fixed-width, TXT

### AI-Powered Features

- Semantic column matching
- Confidence scoring (0-100%)
- Transformation logic generation
- Fallback to rule-based matching
- Multiple LLM support (OpenAI + Hugging Face)

### Data Processing

- Large files up to 10GB
- Chunked upload (1MB chunks)
- Streaming processing
- Background jobs
- Real-time progress tracking (0-100%)

## Development Status

### ✅ Completed (6/8 Phases)
1. ✅ Project Setup & Infrastructure
2. ✅ Backend Core Infrastructure
3. ✅ File Parsing System
4. ✅ AI Integration with LangChain
5. ✅ Batch Processing System
6. ✅ Data Transformation Engine

### 🚧 In Progress (2/8 Phases)
7. 🚧 Frontend Dashboard (Setup complete, implementation in progress)
8. ⏳ Template System (Backend CRUD complete, UI pending)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Environment Variables

### Backend (.env)
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
HUGGINGFACE_API_KEY=your_huggingface_api_key
SECRET_KEY=your_secret_key
DEBUG=True
MAX_FILE_SIZE=10737418240
```

### Frontend (.env)
```env
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_API_URL=http://localhost:8000
```

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.

## Acknowledgments

- FastAPI for the excellent Python web framework
- Supabase for authentication and database
- LangChain for LLM orchestration
- OpenAI for AI capabilities

---

**Status**: Backend production-ready | Frontend setup complete

Last Updated: November 2024
# pbm-auto-conversion
