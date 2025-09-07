import os
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

from agents.agent_core import app  # the AdkApp we already built

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
LOCATION   = os.getenv("VERTEX_AI_LOCATION") or os.getenv("GOOGLE_CLOUD_REGION") or "us-central1"
STAGING    = os.getenv("VERTEX_STAGING_BUCKET")

print(f"Deploying CymbalBot to Google Agent Engine...")
print(f"Project: {PROJECT_ID}")
print(f"Location: {LOCATION}")
print(f"Staging Bucket: {STAGING}")

if not STAGING:
    raise RuntimeError("VERTEX_STAGING_BUCKET is required for deployment (e.g., gs://your-bucket).")

# Initialize Vertex AI with staging bucket
vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING)

# Dependencies for the remote runtime (you can also pass a path to requirements.txt)
requirements = [
    "google-cloud-aiplatform[agent_engines,adk]>=1.66.0",
    "python-dotenv>=1.0.1",
    "requests>=2.32.3",
]

# Ship your source code so imports work in the hosted container
extra_packages = ["agents"]  # (contains rag_tool.py and agent_core.py)

# Propagate runtime configuration to the hosted container
env_vars = {
    "VERTEX_AI_MODEL_NAME": os.getenv("VERTEX_AI_MODEL_NAME", "gemini-2.5-flash"),
    "RAG_BASE_URL": os.getenv("RAG_BASE_URL", "http://localhost:8000"),
    "RAG_KTOP": os.getenv("RAG_KTOP", "10"),
    "RAG_THRESHOLD": os.getenv("RAG_THRESHOLD", "0.7"),
    "RAG_ALLOWED_TAGS": os.getenv("RAG_ALLOWED_TAGS", "hr,tech,infra"),
    "RAG_DEFAULT_TAG": os.getenv("RAG_DEFAULT_TAG", ""),
}

remote_agent = agent_engines.create(
    app,
    requirements=requirements,
    extra_packages=extra_packages,
    display_name="CymbalBot - Internal Knowledge Assistant",
    description="AI-powered internal knowledge assistant for Cymbal company. Helps employees with policies, benefits, IT resources, and onboarding questions.",
    env_vars=env_vars,
    # Optional autoscaling/resources:
    # min_instances=1,
    # max_instances=3,
    # resource_limits={"cpu": "2", "memory": "4Gi"},
)

print("Deployed resource:", remote_agent.resource_name)
