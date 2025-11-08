# Supabase Setup Guide

This guide will help you set up Supabase for the PBM Auto Conversion System.

## 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in project details:
   - Name: `pbm-auto-conv` (or your preferred name)
   - Database Password: (save this securely)
   - Region: Choose closest to you
5. Wait for project to be created (2-3 minutes)

## 2. Get API Keys

1. Go to Project Settings → API
2. Copy the following:
   - **Project URL** → Use as `SUPABASE_URL`
   - **anon public key** → Use as `SUPABASE_KEY`
   - **service_role key** → Use as `SUPABASE_SERVICE_KEY` (keep secret!)

## 3. Set Up Database Schema

Run the following SQL in the Supabase SQL Editor (Project → SQL Editor):

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Templates table
CREATE TABLE templates (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  input_format VARCHAR(50),
  output_format VARCHAR(50),
  mapping_config JSONB NOT NULL,
  transformation_rules JSONB,
  confidence_scores JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jobs table (for batch processing)
CREATE TABLE jobs (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  status VARCHAR(50) NOT NULL DEFAULT 'pending',
  input_file_id UUID,
  reference_file_id UUID,
  template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
  progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
  result_file_id UUID,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- File metadata table
CREATE TABLE file_metadata (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  filename VARCHAR(255) NOT NULL,
  file_type VARCHAR(50),
  file_size BIGINT,
  storage_path TEXT,
  structure_analysis JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_templates_user_id ON templates(user_id);
CREATE INDEX idx_jobs_user_id ON jobs(user_id);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_file_metadata_user_id ON file_metadata(user_id);

-- Enable Row Level Security (RLS)
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_metadata ENABLE ROW LEVEL SECURITY;

-- RLS Policies for templates
CREATE POLICY "Users can view their own templates"
  ON templates FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own templates"
  ON templates FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own templates"
  ON templates FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own templates"
  ON templates FOR DELETE
  USING (auth.uid() = user_id);

-- RLS Policies for jobs
CREATE POLICY "Users can view their own jobs"
  ON jobs FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own jobs"
  ON jobs FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own jobs"
  ON jobs FOR UPDATE
  USING (auth.uid() = user_id);

-- RLS Policies for file_metadata
CREATE POLICY "Users can view their own files"
  ON file_metadata FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can create their own files"
  ON file_metadata FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete their own files"
  ON file_metadata FOR DELETE
  USING (auth.uid() = user_id);
```

## 4. Set Up Authentication

1. Go to Authentication → Settings
2. Configure:
   - **Site URL**: `http://localhost:5173` (for development)
   - **Redirect URLs**: Add your frontend URLs
3. Enable email authentication (or other providers as needed)

## 5. Configure Storage (Optional)

If you want to store files in Supabase Storage:

1. Go to Storage
2. Create a new bucket:
   - Name: `uploads`
   - Public: `false` (private)
3. Set up storage policies for user access

## 6. Environment Variables

Add these to your `.env` files:

**Backend `.env`:**
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
```

**Frontend `.env`:**
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## 7. Test Connection

You can test the connection by running a simple query in the Supabase SQL Editor or using the Supabase client in your application.

## Notes

- The `service_role` key bypasses RLS - use it only on the backend, never expose it to the frontend
- Row Level Security (RLS) ensures users can only access their own data
- The database schema supports the core features: templates, jobs, and file metadata

