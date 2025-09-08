#!/usr/bin/env python3
"""
Test script for deployed CymbalBot agent.
This script tests the deployed agent by sending queries and verifying responses.
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

class CymbalBotTester:
    def __init__(self, deployment_url: str):
        """
        Initialize the tester with the deployment URL.
        
        Args:
            deployment_url: The URL of the deployed agent (e.g., https://your-agent-url.com)
        """
        self.deployment_url = deployment_url.rstrip('/')
        self.session = requests.Session()
        
        # Set up headers for API requests
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'CymbalBot-Tester/1.0'
        })
    
    def test_agent_health(self) -> bool:
        """
        Test if the agent is accessible and responding.
        
        Returns:
            bool: True if agent is healthy, False otherwise
        """
        try:
            # Try to ping the agent endpoint
            health_url = f"{self.deployment_url}/health"
            response = self.session.get(health_url, timeout=10)
            
            if response.status_code == 200:
                print("✅ Agent health check passed")
                return True
            else:
                print(f"❌ Agent health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Agent health check failed: {e}")
            return False
    
    def send_query(self, query: str, user_id: str = "test_user") -> Dict[str, Any]:
        """
        Send a query to the deployed agent.
        
        Args:
            query: The question to ask the agent
            user_id: User identifier for the session
            
        Returns:
            Dict containing the agent's response
        """
        try:
            # Prepare the request payload
            payload = {
                "message": query,
                "user_id": user_id,
                "session_id": f"test_session_{int(time.time())}"
            }
            
            # Send the request
            response = self.session.post(
                f"{self.deployment_url}/chat",
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Query failed: {e}")
            return {"error": str(e)}
    
    def test_basic_queries(self) -> List[Dict[str, Any]]:
        """
        Test basic functionality with common queries.
        
        Returns:
            List of test results
        """
        test_queries = [
            "What are the company benefits?",
            "How do I enroll in benefits?",
            "What are the IT policies?",
            "What is the onboarding process?",
            "What are the vacation policies?"
        ]
        
        results = []
        
        print("\n🧪 Testing basic queries...")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\nTest {i}: {query}")
            print("-" * 30)
            
            response = self.send_query(query)
            
            if "error" in response:
                print(f"❌ Failed: {response['error']}")
                results.append({
                    "query": query,
                    "status": "failed",
                    "error": response["error"]
                })
            else:
                print("✅ Query successful")
                print(f"Response: {response.get('response', 'No response')[:200]}...")
                
                # Check for citations
                citations = response.get('citations', [])
                if citations:
                    print(f"📚 Found {len(citations)} citations")
                else:
                    print("📚 No citations found")
                
                results.append({
                    "query": query,
                    "status": "success",
                    "response_length": len(str(response.get('response', ''))),
                    "citations_count": len(citations)
                })
            
            # Small delay between requests
            time.sleep(1)
        
        return results
    
    def test_citations(self) -> bool:
        """
        Test that citations are properly formatted and accessible.
        
        Returns:
            bool: True if citations are working, False otherwise
        """
        print("\n🔗 Testing citations...")
        print("=" * 30)
        
        response = self.send_query("What are the company benefits?")
        
        if "error" in response:
            print("❌ Query failed, cannot test citations")
            return False
        
        citations = response.get('citations', [])
        
        if not citations:
            print("❌ No citations found in response")
            return False
        
        print(f"✅ Found {len(citations)} citations")
        
        # Test citation format
        for i, citation in enumerate(citations, 1):
            print(f"\nCitation {i}:")
            print(f"  Name: {citation.get('name', 'N/A')}")
            print(f"  URL: {citation.get('url', 'N/A')}")
            print(f"  Title: {citation.get('title', 'N/A')}")
            
            # Test if citation URL is accessible
            try:
                url_response = requests.head(citation.get('url', ''), timeout=5)
                if url_response.status_code == 200:
                    print("  ✅ URL is accessible")
                else:
                    print(f"  ⚠️  URL returned status {url_response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"  ❌ URL not accessible: {e}")
        
        return True
    
    def test_markdown_formatting(self) -> bool:
        """
        Test that responses are properly formatted in markdown.
        
        Returns:
            bool: True if formatting looks correct, False otherwise
        """
        print("\n📝 Testing markdown formatting...")
        print("=" * 35)
        
        response = self.send_query("What are the IT policies and security requirements?")
        
        if "error" in response:
            print("❌ Query failed, cannot test formatting")
            return False
        
        response_text = response.get('response', '')
        
        # Check for markdown elements
        has_headers = '##' in response_text or '###' in response_text
        has_bullets = '- ' in response_text or '* ' in response_text
        has_bold = '**' in response_text
        has_citations = 'Citations:' in response_text
        
        print(f"Headers (##/###): {'✅' if has_headers else '❌'}")
        print(f"Bullet points (-/*): {'✅' if has_bullets else '❌'}")
        print(f"Bold text (**): {'✅' if has_bold else '❌'}")
        print(f"Citations section: {'✅' if has_citations else '❌'}")
        
        if has_headers and has_bullets and has_citations:
            print("✅ Markdown formatting looks good")
            return True
        else:
            print("❌ Markdown formatting needs improvement")
            return False
    
    def run_full_test_suite(self) -> Dict[str, Any]:
        """
        Run the complete test suite.
        
        Returns:
            Dict containing test results summary
        """
        print("🚀 Starting CymbalBot Deployment Test Suite")
        print("=" * 50)
        
        # Test 1: Health check
        health_ok = self.test_agent_health()
        
        if not health_ok:
            print("\n❌ Agent is not accessible. Stopping tests.")
            return {"status": "failed", "reason": "Agent not accessible"}
        
        # Test 2: Basic queries
        query_results = self.test_basic_queries()
        
        # Test 3: Citations
        citations_ok = self.test_citations()
        
        # Test 4: Markdown formatting
        formatting_ok = self.test_markdown_formatting()
        
        # Summary
        successful_queries = sum(1 for r in query_results if r["status"] == "success")
        total_queries = len(query_results)
        
        print("\n📊 Test Summary")
        print("=" * 20)
        print(f"Health Check: {'✅' if health_ok else '❌'}")
        print(f"Successful Queries: {successful_queries}/{total_queries}")
        print(f"Citations Working: {'✅' if citations_ok else '❌'}")
        print(f"Markdown Formatting: {'✅' if formatting_ok else '❌'}")
        
        overall_success = health_ok and successful_queries > 0 and citations_ok and formatting_ok
        
        return {
            "status": "success" if overall_success else "failed",
            "health_check": health_ok,
            "successful_queries": successful_queries,
            "total_queries": total_queries,
            "citations_working": citations_ok,
            "markdown_formatting": formatting_ok,
            "query_results": query_results
        }

def main():
    """Main function to run the test suite."""
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <deployment_url>")
        print("Example: python test_deployment.py https://your-agent-url.com")
        sys.exit(1)
    
    deployment_url = sys.argv[1]
    
    # Create tester instance
    tester = CymbalBotTester(deployment_url)
    
    # Run full test suite
    results = tester.run_full_test_suite()
    
    # Ensure test_results directory exists
    os.makedirs("test_results", exist_ok=True)
    
    # Save results to file
    results_file = "test_results/test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Test results saved to {results_file}")
    
    if results["status"] == "success":
        print("\n🎉 All tests passed! CymbalBot is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the results above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
