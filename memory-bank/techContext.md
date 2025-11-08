# Technical Context

## Technology Stack (Planned)

### Frontend
- **Framework**: React.js
- **Styling**: Tailwind CSS
- **State Management**: React Context or Zustand
- **File Upload**: react-dropzone
- **Charts/Visualization**: Recharts or Chart.js

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: Supabase Auth or JWT
- **File Parsing** (Priority):
  - Pandas (CSV, Excel, TSV, Pipe Delimited)
  - Custom parser for Flat File (position-based)
  - Text file parsing (TXT)
- **File Parsing** (Future):
  - PyMuPDF (PDF)
  - Pillow (Images)
  - OpenCV (Image processing)
  - python-docx (Word documents)
  - BeautifulSoup (HTML/XML)
  - EDI parsers (custom or library)

### AI/LLM
- **LangChain**: langchain library
- **LLM Options**:
  - **Primary**: OpenAI API (GPT-4/GPT-3.5)
  - **Fallback**: Hugging Face Transformers (free tier)

### Storage
- **Templates & User Data**: Supabase (PostgreSQL) - free tier
- **File Storage**: Local filesystem or Supabase Storage (for large files)

### Deployment
- **Architecture**: Single monorepo, all-in-one deployment
- **Containerization**: Docker
- **Hosting**: Render, Railway, or Fly.io (supports Docker)
- **Database**: Supabase (cloud PostgreSQL)

### File Processing
- **Max File Size**: 10GB
- **Typical Size**: 2GB
- **Processing**: Batch/async with job queue (Celery or FastAPI BackgroundTasks)
- **Priority Formats**: TXT, CSV, Excel (.xls, .xlsx), Pipe Delimited, Flat File (position-based)

## Development Setup
- Python 3.10+
- Node.js 18+
- Package managers: pip, npm/yarn
- Environment variables for API keys

## Dependencies (To Be Installed)
### Backend
- fastapi
- uvicorn
- langchain
- openai
- transformers (Hugging Face)
- pandas
- openpyxl (Excel)
- supabase-py (Supabase client)
- python-jose (JWT)
- passlib (password hashing)
- python-multipart (file uploads)
- celery (optional, for async jobs)
- redis (optional, for Celery)

### Frontend
- react
- react-dom
- tailwindcss
- react-dropzone
- axios
- @supabase/supabase-js (Supabase client)
- react-router-dom (routing)
- zustand (state management)

