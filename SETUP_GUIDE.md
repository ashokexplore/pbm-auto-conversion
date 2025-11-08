# Setup Guide

This guide will help you set up the development environment for the PBM Auto Conversion System.

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Docker and Docker Compose (optional, for containerized development)
- Git

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository** (if not already done)
   ```bash
   git clone <repository-url>
   cd pbm-auto-conv
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env` in the root directory
   - Fill in your Supabase credentials and API keys

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```
   
   This will:
   - Build and start the backend (port 8000)
   - Build and start the frontend (port 80)
   - Start Redis (port 6379)

4. **Access the application**
   - Frontend: http://localhost
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Option 2: Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your credentials:
     ```
     SUPABASE_URL=your_supabase_url
     SUPABASE_KEY=your_supabase_key
     SUPABASE_SERVICE_KEY=your_service_key
     OPENAI_API_KEY=your_openai_key
     SECRET_KEY=your_secret_key
     ```

6. **Create necessary directories**
   ```bash
   mkdir uploads tmp
   ```

7. **Run the backend**
   ```bash
   uvicorn app.main:app --reload
   ```
   
   Backend will be available at: http://localhost:8000

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Fill in your Supabase credentials:
     ```
     VITE_SUPABASE_URL=your_supabase_url
     VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
     VITE_API_URL=http://localhost:8000
     ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```
   
   Frontend will be available at: http://localhost:5173

## Supabase Setup

1. Follow the instructions in [SUPABASE_SETUP.md](./SUPABASE_SETUP.md)
2. Create your Supabase project
3. Run the SQL schema provided in the setup guide
4. Copy your API keys to the `.env` files

## Verify Installation

### Backend
```bash
curl http://localhost:8000/health
```
Should return: `{"status":"healthy","service":"PBM Auto Conversion System"}`

### Frontend
Open http://localhost:5173 in your browser. You should see the application homepage.

## Development Workflow

1. **Backend changes**: The server auto-reloads with `--reload` flag
2. **Frontend changes**: Vite hot-reloads automatically
3. **Database changes**: Use Alembic for migrations (to be set up in Phase 2)

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure virtual environment is activated
- **Port already in use**: Change port in `uvicorn` command or kill existing process
- **Missing dependencies**: Run `pip install -r requirements.txt` again

### Frontend Issues

- **Module not found**: Run `npm install` again
- **Build errors**: Check TypeScript errors with `npm run build`
- **CORS errors**: Ensure backend CORS_ORIGINS includes frontend URL

### Docker Issues

- **Build fails**: Check Docker logs with `docker-compose logs`
- **Port conflicts**: Modify ports in `docker-compose.yml`
- **Volume permissions**: Ensure uploads/ and tmp/ directories exist

## Next Steps

After setup is complete:
1. ✅ Verify both backend and frontend are running
2. ✅ Test API endpoints at http://localhost:8000/api/docs
3. ✅ Proceed to Phase 2: Backend Core Infrastructure

## Need Help?

- Check the [Implementation Plan](./IMPLEMENTATION_PLAN.md) for detailed phase breakdown
- Review [Memory Bank](./memory-bank/) for project context
- Check Supabase documentation for database setup issues

