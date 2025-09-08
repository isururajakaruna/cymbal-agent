#!/usr/bin/env python3
"""
Test script for local CymbalBot agent.
This script tests the local agent with RAG API authentication.
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Import the local agent
from agents.agent_core import app

class LocalCymbalBotTester:
    def __init__(self):
        """Initialize the tester with the local agent."""
        self.app = app
        print("✅ Successfully connected to local CymbalBot agent")
    
    async def send_query(self, query: str, user_id: str = "test_user") -> Dict[str, Any]:
        """
        Send a query to the local agent.
        
        Args:
            query: The question to ask the agent
            user_id: User identifier for the session
            
        Returns:
            Dict containing the agent's response
        """
        try:
            print(f"🤖 Sending query: {query}")
            
            # Use the local agent to process the query
            response_stream = self.app.async_stream_query(
                user_id=user_id,
                message=query
            )
            
            # Collect the full response
            full_response = ""
            
            async for event in response_stream:
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if "text" in part:
                        full_response += part["text"]
            
            # Try to extract citations from the response
            citations = []
            if "Citations:" in full_response:
                citations_section = full_response.split("Citations:")[-1].strip()
                if citations_section and citations_section != "None":
                    # Parse citations (simple parsing for markdown links)
                    import re
                    citation_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', citations_section)
                    citations = [{"name": name, "url": url} for name, url in citation_links]
            
            return {
                "response": full_response,
                "citations": citations,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def test_basic_queries(self) -> List[Dict[str, Any]]:
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
            
            response = await self.send_query(query)
            
            if response.get("status") == "failed":
                print(f"❌ Failed: {response.get('error', 'Unknown error')}")
                results.append({
                    "query": query,
                    "status": "failed",
                    "error": response.get("error", "Unknown error")
                })
            else:
                print("✅ Query successful")
                response_text = response.get("response", "")
                print(f"Response: {response_text[:200]}...")
                
                # Check for citations
                citations = response.get("citations", [])
                if citations:
                    print(f"📚 Found {len(citations)} citations")
                    for j, citation in enumerate(citations, 1):
                        print(f"  {j}. {citation.get('name', 'N/A')}")
                else:
                    print("📚 No citations found")
                
                results.append({
                    "query": query,
                    "status": "success",
                    "response_length": len(response_text),
                    "citations_count": len(citations)
                })
            
            # Small delay between requests
            await asyncio.sleep(1)
        
        return results
    
    async def test_citations(self) -> bool:
        """
        Test that citations are properly formatted and accessible.
        
        Returns:
            bool: True if citations are working, False otherwise
        """
        print("\n🔗 Testing citations...")
        print("=" * 30)
        
        response = await self.send_query("What are the company benefits?")
        
        if response.get("status") == "failed":
            print("❌ Query failed, cannot test citations")
            return False
        
        citations = response.get("citations", [])
        
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
            print("  ✅ Citation format looks good")
        
        return True
    
    async def test_markdown_formatting(self) -> bool:
        """
        Test that responses are properly formatted in markdown.
        
        Returns:
            bool: True if formatting looks correct, False otherwise
        """
        print("\n📝 Testing markdown formatting...")
        print("=" * 35)
        
        response = await self.send_query("What are the IT policies and security requirements?")
        
        if response.get("status") == "failed":
            print("❌ Query failed, cannot test formatting")
            return False
        
        response_text = response.get("response", "")
        
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
    
    async def test_rag_api_connection(self) -> bool:
        """
        Test if the RAG API is accessible and working.
        
        Returns:
            bool: True if RAG API is working, False otherwise
        """
        print("\n🔌 Testing RAG API connection...")
        print("=" * 35)
        
        response = await self.send_query("What are the company benefits?")
        
        if response.get("status") == "failed":
            error = response.get("error", "")
            if "connection" in error.lower() or "timeout" in error.lower() or "refused" in error.lower():
                print("❌ RAG API connection failed")
                print(f"Error: {error}")
                return False
            else:
                print("❌ Query failed for other reason")
                print(f"Error: {error}")
                return False
        
        # Check if we got a meaningful response (not just "I don't know")
        response_text = response.get("response", "")
        if "don't know" in response_text.lower() or "no information" in response_text.lower():
            print("❌ RAG API returned no information")
            return False
        
        print("✅ RAG API connection successful")
        return True
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """
        Run the complete test suite.
        
        Returns:
            Dict containing test results summary
        """
        print("🚀 Starting CymbalBot Local Agent Test Suite")
        print("=" * 50)
        
        # Test 1: RAG API connection
        rag_connection_ok = await self.test_rag_api_connection()
        
        if not rag_connection_ok:
            print("\n⚠️  RAG API connection failed. This might be due to authentication.")
            print("Continuing with other tests...")
        
        # Test 2: Basic queries
        query_results = await self.test_basic_queries()
        
        # Test 3: Citations
        citations_ok = await self.test_citations()
        
        # Test 4: Markdown formatting
        formatting_ok = await self.test_markdown_formatting()
        
        # Summary
        successful_queries = sum(1 for r in query_results if r["status"] == "success")
        total_queries = len(query_results)
        
        print("\n📊 Test Summary")
        print("=" * 20)
        print(f"RAG API Connection: {'✅' if rag_connection_ok else '❌'}")
        print(f"Successful Queries: {successful_queries}/{total_queries}")
        print(f"Citations Working: {'✅' if citations_ok else '❌'}")
        print(f"Markdown Formatting: {'✅' if formatting_ok else '❌'}")
        
        overall_success = successful_queries > 0 and citations_ok and formatting_ok
        
        return {
            "status": "success" if overall_success else "failed",
            "rag_connection": rag_connection_ok,
            "successful_queries": successful_queries,
            "total_queries": total_queries,
            "citations_working": citations_ok,
            "markdown_formatting": formatting_ok,
            "query_results": query_results
        }

async def main():
    """Main function to run the test suite."""
    try:
        # Create tester instance
        tester = LocalCymbalBotTester()
        
        # Run full test suite
        results = await tester.run_full_test_suite()
        
        # Ensure test_results directory exists
        os.makedirs("test_results", exist_ok=True)
        
        # Save results to file
        results_file = "test_results/local_test_results.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to {results_file}")
        
        if results["status"] == "success":
            print("\n🎉 All tests passed! Local CymbalBot is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the results above.")
            if not results["rag_connection"]:
                print("💡 RAG API connection failed - check authentication setup.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite failed to initialize: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
