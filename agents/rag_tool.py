import os
import requests
import logging
import urllib.parse
from typing import Dict, Any, List

# Color codes for terminal output
class Colors:
    LOG = '\033[90m'       # Gray for logs
    RESET = '\033[0m'      # Reset color

# Set up logging with custom formatter
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        return f"{Colors.LOG}{super().format(record)}{Colors.RESET}"

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(message)s'))
logger.addHandler(handler)

RAG_BASE_URL    = os.getenv("RAG_BASE_URL", "http://localhost:8000")
RAG_KTOP        = int(os.getenv("RAG_KTOP", "10"))
RAG_THRESHOLD   = float(os.getenv("RAG_THRESHOLD", "0.6"))
API_AUTH_TOKEN  = os.getenv("API_AUTH_TOKEN", "")
_ALLOWED_TAGS   = [t.strip() for t in os.getenv("RAG_ALLOWED_TAGS", "hr,tech,infra,product,policy,onboarding,benefits,it,security,finance,legal").split(",") if t.strip()]
_DEFAULT_TAG    = os.getenv("RAG_DEFAULT_TAG", "policy").strip()

# Company-specific tag mapping for better knowledge retrieval
_COMPANY_TAG_MAPPING = {
    # HR & Benefits
    "hr": ["hr", "human resources", "employee", "staff", "workforce"],
    "benefits": ["benefits", "insurance", "health", "dental", "vision", "retirement", "401k", "pto", "vacation"],
    "policy": ["policy", "policies", "guidelines", "procedures", "rules", "compliance"],
    "onboarding": ["onboarding", "new hire", "orientation", "training", "welcome"],
    
    # IT & Security
    "it": ["it", "technology", "computer", "laptop", "software", "hardware", "system"],
    "security": ["security", "password", "access", "permissions", "cybersecurity", "data protection"],
    
    # Business
    "finance": ["finance", "budget", "expense", "reimbursement", "payroll", "salary"],
    "legal": ["legal", "contract", "agreement", "terms", "compliance", "liability"],
    
    # Infrastructure
    "infra": ["infrastructure", "office", "facilities", "building", "equipment", "supplies"],
    
    # Products
    "product": ["product", "catalog", "inventory", "sales", "marketing", "customer"]
}

def _choose_tags_from_text(query: str) -> List[str]:
    """
    Smart tag selection for Cymbal company knowledge base.
    Maps query terms to appropriate document categories.
    """
    qlower = query.lower()
    chosen = []
    
    # Check for direct tag matches first
    for tag in _ALLOWED_TAGS:
        if tag in qlower:
            chosen.append(tag)
    
    # If no direct matches, use intelligent mapping
    if not chosen:
        for tag, keywords in _COMPANY_TAG_MAPPING.items():
            if any(keyword in qlower for keyword in keywords):
                chosen.append(tag)
    
    # If still no matches, use default tag
    if not chosen and _DEFAULT_TAG and _DEFAULT_TAG in _ALLOWED_TAGS:
        chosen = [_DEFAULT_TAG]
    
    # Remove duplicates and return
    return list(set(chosen))

def _generate_citations(rag_response: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate citations array from RAG response with downloadable links.
    """
    citations = []
    
    if not rag_response.get('files'):
        return citations
    
    base_url = RAG_BASE_URL.rstrip('/')
    
    for file_info in rag_response['files']:
        file_name = file_info.get('name', '')
        if not file_name:
            continue
            
        # Create downloadable URL using the view API
        encoded_filename = urllib.parse.quote(file_name, safe='')
        download_url = f"{base_url}/api/v1/files/view?filename={encoded_filename}"
        
        citation = {
            "name": file_name,
            "url": download_url,
            "title": file_info.get('title', file_name)
        }
        
        # Add additional metadata if available
        if file_info.get('tags'):
            citation['tags'] = file_info['tags']
        if file_info.get('last_updated'):
            citation['last_updated'] = file_info['last_updated']
            
        citations.append(citation)
    
    return citations

def rag_search(query: str) -> Dict[str, Any]:
    """
    Enhanced RAG search with multiple strategies and better logging.
    """
    # Build URL with authentication token
    url = f"{RAG_BASE_URL}/api/v1/search/rag"
    if API_AUTH_TOKEN:
        url += f"?token={API_AUTH_TOKEN}"
    
    # Try multiple search strategies
    search_strategies = [
        # Strategy 1: Original query with tags
        {
            "query": query,
            "ktop": RAG_KTOP,
            "threshold": RAG_THRESHOLD,
            "tags": _choose_tags_from_text(query) or None
        },
        # Strategy 2: Lower threshold for broader search
        {
            "query": query,
            "ktop": RAG_KTOP,
            "threshold": 0.3,
            "tags": None
        },
        # Strategy 3: Broader query terms
        {
            "query": query.lower(),
            "ktop": RAG_KTOP,
            "threshold": 0.5,
            "tags": None
        }
    ]
    
    for i, payload in enumerate(search_strategies, 1):
        # Remove None values from payload
        payload = {k: v for k, v in payload.items() if v is not None}
        
        logger.info("=" * 60)
        logger.info(f"RAG SEARCH REQUEST - Strategy {i}")
        logger.info("=" * 60)
        logger.info(f"URL: {url}")
        logger.info(f"Query: {query}")
        logger.info(f"Payload: {payload}")
        logger.info("=" * 60)

        try:
            resp = requests.post(url, json=payload, timeout=30)
            logger.info(f"Response status: {resp.status_code}")
            
            resp.raise_for_status()
            result = resp.json()
            
            logger.info("RAG RESPONSE")
            logger.info("=" * 60)
            logger.info(f"Response data: {result}")
            logger.info("=" * 60)
            
            # If we get results, add citations and return them
            if result.get('total_files', 0) > 0 or result.get('total_chunks', 0) > 0:
                logger.info(f"✅ Found results with strategy {i}")
                # Generate citations for the response
                citations = _generate_citations(result)
                result['citations'] = citations
                logger.info(f"Generated {len(citations)} citations")
                return result
            else:
                logger.info(f"❌ No results with strategy {i}, trying next...")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"RAG API request failed with strategy {i}: {e}")
            if i == len(search_strategies):  # Last strategy
                raise
            continue
        except Exception as e:
            logger.error(f"Unexpected error in RAG search with strategy {i}: {e}")
            if i == len(search_strategies):  # Last strategy
                raise
            continue
    
    # If all strategies failed, return the last result with empty citations
    logger.warning("All search strategies returned no results")
    result['citations'] = []
    return result
