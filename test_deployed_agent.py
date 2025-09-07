#!/usr/bin/env python3
"""
Test script for deployed CymbalBot agent.
This script tests the deployed agent using the Vertex AI Agent Engine API.
"""

import os
import sys
import json
import time
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
import vertexai
from vertexai import agent_engines

# Load environment variables
load_dotenv()

class DeployedCymbalBotTester:
    def __init__(self, agent_resource_name: str = None):
        """
        Initialize the tester with the deployed agent resource name.
        
        Args:
            agent_resource_name: The resource name of the deployed agent
        """
        if not agent_resource_name:
            # Use the deployed agent resource name from the deployment
            agent_resource_name = "projects/630583075057/locations/us-central1/reasoningEngines/5830125221910151168"
        
        self.agent_resource_name = agent_resource_name
        
        # Initialize Vertex AI
        PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GOOGLE_CLOUD_PROJECT_ID")
        LOCATION = os.getenv("VERTEX_AI_LOCATION") or os.getenv("GOOGLE_CLOUD_REGION") or "us-central1"
        
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        
        # Get the deployed agent
        try:
            self.agent_engine = agent_engines.get(agent_resource_name)
            print(f"✅ Successfully connected to deployed agent: {agent_resource_name}")
        except Exception as e:
            print(f"❌ Failed to connect to deployed agent: {e}")
            raise
    
    async def send_query(self, query: str, user_id: str = "test_user") -> Dict[str, Any]:
        """
        Send a query to the deployed agent.
        
        Args:
            query: The question to ask the agent
            user_id: User identifier for the session
            
        Returns:
            Dict containing the agent's response
        """
        try:
            print(f"🤖 Sending query: {query}")
            
            # Use the agent engine to process the query
            response_stream = self.agent_engine.async_stream_query(
                user_id=user_id,
                message=query
            )
            
            # Collect the full response
            full_response = ""
            citations = []
            
            async for event in response_stream:
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if "text" in part:
                        full_response += part["text"]
            
            # Try to extract citations from the response
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
            await asyncio.sleep(2)
        
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
    
    async def run_full_test_suite(self) -> Dict[str, Any]:
        """
        Run the complete test suite.
        
        Returns:
            Dict containing test results summary
        """
        print("🚀 Starting CymbalBot Deployed Agent Test Suite")
        print("=" * 55)
        
        # Test 1: Basic queries
        query_results = await self.test_basic_queries()
        
        # Test 2: Citations
        citations_ok = await self.test_citations()
        
        # Test 3: Markdown formatting
        formatting_ok = await self.test_markdown_formatting()
        
        # Summary
        successful_queries = sum(1 for r in query_results if r["status"] == "success")
        total_queries = len(query_results)
        
        print("\n📊 Test Summary")
        print("=" * 20)
        print(f"Successful Queries: {successful_queries}/{total_queries}")
        print(f"Citations Working: {'✅' if citations_ok else '❌'}")
        print(f"Markdown Formatting: {'✅' if formatting_ok else '❌'}")
        
        overall_success = successful_queries > 0 and citations_ok and formatting_ok
        
        return {
            "status": "success" if overall_success else "failed",
            "successful_queries": successful_queries,
            "total_queries": total_queries,
            "citations_working": citations_ok,
            "markdown_formatting": formatting_ok,
            "query_results": query_results
        }

async def main():
    """Main function to run the test suite."""
    if len(sys.argv) > 1:
        agent_resource_name = sys.argv[1]
    else:
        agent_resource_name = None
    
    try:
        # Create tester instance
        tester = DeployedCymbalBotTester(agent_resource_name)
        
        # Run full test suite
        results = await tester.run_full_test_suite()
        
        # Save results to file
        with open("deployed_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to deployed_test_results.json")
        
        if results["status"] == "success":
            print("\n🎉 All tests passed! CymbalBot is working correctly in production.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite failed to initialize: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
