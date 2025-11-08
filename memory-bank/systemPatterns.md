# System Patterns

## Architecture (Planned)
```
┌─────────────────┐
│   React Frontend │
│  (Dashboard UI)  │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Backend│
│  (Python)       │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────┐
│LangChain│ │File   │
│ + LLM  │ │Parsers│
└────────┘ └───────┘
    │
┌───▼──────┐
│ Template │
│ Storage  │
└──────────┘
```

## Key Components (Planned)
1. **File Upload Service**: Handles multi-format file uploads
2. **Parser Service**: Extracts structure and data from files
3. **AI Reasoning Service**: LangChain integration for mapping logic
4. **Mapping Engine**: Applies transformations
5. **Template Manager**: Stores and retrieves mapping templates
6. **Export Service**: Generates output files

## Design Patterns (To Be Implemented)
- Service-oriented architecture
- RESTful API design
- Component-based frontend
- Template pattern for mappings
- Strategy pattern for different file parsers

