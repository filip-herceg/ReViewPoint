# System Architecture

This page describes the overall system structure of ReViewPoint.

## System Overview

```mermaid
graph TD
    FE[Frontend<br>React + Tailwind]
    BE[Backend<br>FastAPI Core]
    MOD[Modules<br>(Microservices)]
    LLM[LLM Adapter<br>OpenAI/vLLM]
    DB[(PostgreSQL)]
    STORAGE[(MinIO/S3)]
    FILES[(PDF Upload)]
    DOCS[Documentation<br>(MkDocs)]

    FE -->|REST API| BE
    FE --> DOCS
    BE -->|dispatches| MOD
    MOD -->|returns result| BE
    BE -->|prompts| LLM
    BE --> DB
    BE --> STORAGE
    FE -->|renders result| BE
    FILES --> BE
```

---

## Components

### Frontend

- React + Vite + TailwindCSS
- PDF upload and display
- Module result views
- Final LLM-based summary view

### Backend

- FastAPI
- Central dispatcher for modules
- JSON schema validation
- Connection to PostgreSQL and S3
- Integrated LLM adapters (OpenAI, vLLM)

### Modules

- Dockerized REST services
- Own testing, linting, and CI/CD
- Communicate via JSON input/output

### LLM Layer

- OpenAI (external)
- vLLM (local)
- Prompt templates using Jinja2
- LLM adapter interface for flexible integration

---

## Standard Module Output (JSON)

```json
{
  "module_name": "structure_validator",
  "score": 78,
  "status": "warning",
  "feedback": [
    "Missing conclusion section.",
    "Introduction too short."
  ],
  "version": "1.0.0"
}
```

---

## Data Flow Summary

```text
PDF → Backend → Parsing → Modules → LLM → Aggregated Result → Frontend
```

---

## Scalability Features

- Independent containers for modules
- Parallel evaluation
- Plug-and-play LLM provider
- Optional Prometheus/Grafana monitoring
- Decoupled CI for modules and core system
