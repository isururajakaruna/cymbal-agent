# RAG ADK Agent

A Google ADK (Agent Development Kit) agent with RAG (Retrieval-Augmented Generation) capabilities, designed to be deployed on Google Cloud's Agent Engine.

## Project Structure

```
rag-adk-agent/
├── agents/
│   ├── __init__.py
│   ├── agent_core.py      # ADK agent definition
│   └── rag_tool.py        # RAG search tool
├── agent_cli.py           # Local CLI for testing
├── deploy.py              # Deployment script for Agent Engine
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── .gitignore            # Git ignore patterns
└── service-account-key.json  # GCP service account (keep local)
```

## Setup

### 1. Create and Activate Conda Environment

```bash
# Create conda environment
conda create -n cymbal-agent python=3.11 -y

# Activate environment
conda activate cymbal-agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

The `.env` file contains the following configuration:

```bash
# GCP
GOOGLE_CLOUD_PROJECT_ID=cymbol-demo
GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
GOOGLE_CLOUD_REGION=us-central1

# Vertex AI
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL_NAME=gemini-2.5-flash
VERTEX_STAGING_BUCKET=gs://cymbol-demo-agent-staging

# Your RAG API
RAG_BASE_URL=http://localhost:8000

# RAG defaults
RAG_KTOP=10
RAG_THRESHOLD=0.7
RAG_ALLOWED_TAGS=hr,tech,infra
```

### 3. Authentication

Choose one of the following authentication methods:

**Option A: User Application Default Credentials (ADC)**
```bash
gcloud auth application-default login
```

**Option B: Service Account**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
```

## Usage

### Local Testing

1. **Start your RAG API** on `http://localhost:8000`

2. **Test the agent locally:**
   ```bash
   # Single message
   python agent_cli.py "Summarize our HR leave policy"
   
   # Interactive mode
   python agent_cli.py
   ```

### Deployment to Agent Engine

1. **Ensure you have a GCS bucket** for staging (set `VERTEX_STAGING_BUCKET` in `.env`)

2. **Deploy the agent:**
   ```bash
   python deploy.py
   ```

3. **The deployment will output the resource name** of your deployed agent.

## Features

- **RAG Integration**: Connects to your RAG API for document retrieval
- **Tag-based Filtering**: Automatically infers tags (hr, tech, infra) from queries
- **Environment-driven Configuration**: All settings configurable via environment variables
- **Local Testing**: CLI interface for development and testing
- **Cloud Deployment**: Ready for Google Cloud Agent Engine deployment

## RAG API Requirements

Your RAG API should expose an endpoint at `/api/v1/search/rag` that accepts:

```json
{
  "query": "search query",
  "ktop": 10,
  "threshold": 0.7,
  "tags": ["hr", "tech", "infra"]  // optional
}
```

And returns search results in JSON format.

## Configuration

- **RAG_KTOP**: Number of top results to retrieve (default: 10)
- **RAG_THRESHOLD**: Similarity threshold for results (default: 0.7)
- **RAG_ALLOWED_TAGS**: Comma-separated list of allowed tags (default: "hr,tech,infra")
- **RAG_DEFAULT_TAG**: Optional default tag if none inferred from query

## Notes

- The `service-account-key.json` file should be kept local and never committed to version control
- The `.env` file is also excluded from version control for security
- Make sure your RAG API is running and accessible before testing locally
- The CLI suppresses ADK warnings about non-text parts (thought_signature, function_call) for cleaner output
