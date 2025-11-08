# Project Brief: PBM Auto Conversion System

## Overview
A web-based intelligent data transformation application that uses AI (LangChain + LLMs) to parse, analyze, and transform data files of various formats into standardized output formats.

## Core Objectives
1. Accept multiple input file formats (CSV, XLS, JSON, TSV, TXT, XML, EDI, PDF, images, etc.)
2. Use optional reference documents for intelligent mapping
3. Leverage LangChain + LLMs for semantic understanding and mapping recommendations
4. Provide interactive dashboard for review and refinement
5. Generate output in desired formats
6. Store mapping templates for automation and reusability

## Key Requirements
- **Input Flexibility**: Support 15+ file formats
- **AI Reasoning**: LangChain integration with OpenAI or Ollama
- **Dashboard**: Visual mapping interface with confidence scores
- **Accuracy Target**: ≥95% mapping accuracy
- **Template System**: Save and reuse mapping configurations
- **Free/Open Source**: Prefer free tier services and open-source tools

## Success Criteria
- Successfully parse and understand structure of various file formats
- Generate accurate mapping recommendations (≥95% confidence)
- Allow user review and manual overrides
- Export transformed data in desired format
- Save and reuse mapping templates

## Constraints
- Must use free/open-source technologies where possible
- Should work with free tier hosting (Vercel, Netlify, Render, Railway)
- Support for local LLMs (Ollama) as alternative to OpenAI

