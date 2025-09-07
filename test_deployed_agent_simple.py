#!/usr/bin/env python3
"""
Simple test script for deployed CymbalBot agent.
This script tests basic functionality without requiring RAG API access.
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

class SimpleCymbalBotTester:
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
            
            async for event in response_stream:
                content = event.get("content", {})
                for part in content.get("parts", []):
                    if "text" in part:
                        full_response += part["text"]
            
            return {
                "response": full_response,
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return {"error": str(e), "status": "failed"}
    
    async def test_basic_functionality(self) -> List[Dict[str, Any]]:
        """
        Test basic functionality with simple queries.
        
        Returns:
            List of test results
        """
        test_queries = [
            "Hello, who are you?",
            "What can you help me with?",
            "Tell me about Cymbal company",
            "What is your role?",
            "How can I get help?"
        ]
        
        results = []
        
        print("\n🧪 Testing basic functionality...")
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
                response_text = response.get("response", "")
                print("✅ Query successful")
                print(f"Response: {response_text[:300]}...")
                
                results.append({
                    "query": query,
                    "status": "success",
                    "response_length": len(response_text),
                    "has_content": len(response_text) > 0
                })
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        return results
    
    async def test_agent_identity(self) -> bool:
        """
        Test that the agent identifies itself correctly.
        
        Returns:
            bool: True if agent identity is correct, False otherwise
        """
        print("\n🆔 Testing agent identity...")
        print("=" * 30)
        
        response = await self.send_query("Who are you and what is your role?")
        
        if response.get("status") == "failed":
            print("❌ Query failed, cannot test identity")
            return False
        
        response_text = response.get("response", "").lower()
        
        # Check for key identity indicators
        has_cymbal = "cymbal" in response_text
        has_bot = "bot" in response_text or "assistant" in response_text
        has_knowledge = "knowledge" in response_text or "help" in response_text
        
        print(f"Cymbal mentioned: {'✅' if has_cymbal else '❌'}")
        print(f"Bot/Assistant mentioned: {'✅' if has_bot else '❌'}")
        print(f"Knowledge/Help mentioned: {'✅' if has_knowledge else '❌'}")
        
        if has_cymbal and has_bot:
            print("✅ Agent identity looks correct")
            return True
        else:
            print("❌ Agent identity needs improvement")
            return False
    
    async def test_error_handling(self) -> bool:
        """
        Test how the agent handles errors or unclear queries.
        
        Returns:
            bool: True if error handling is good, False otherwise
        """
        print("\n⚠️  Testing error handling...")
        print("=" * 35)
        
        # Test with a nonsensical query
        response = await self.send_query("asdfghjkl random gibberish 12345")
        
        if response.get("status") == "failed":
            print("❌ Query failed completely")
            return False
        
        response_text = response.get("response", "")
        
        # Check if agent provides helpful response to unclear query
        has_helpful = any(word in response_text.lower() for word in [
            "help", "understand", "clarify", "specific", "question", "assist"
        ])
        
        print(f"Helpful response to unclear query: {'✅' if has_helpful else '❌'}")
        
        if has_helpful:
            print("✅ Error handling looks good")
            return True
        else:
            print("❌ Error handling needs improvement")
            return False
    
    async def run_simple_test_suite(self) -> Dict[str, Any]:
        """
        Run the simple test suite.
        
        Returns:
            Dict containing test results summary
        """
        print("🚀 Starting CymbalBot Simple Test Suite")
        print("=" * 45)
        print("Note: This test doesn't require RAG API access")
        print("=" * 45)
        
        # Test 1: Basic functionality
        query_results = await self.test_basic_functionality()
        
        # Test 2: Agent identity
        identity_ok = await self.test_agent_identity()
        
        # Test 3: Error handling
        error_handling_ok = await self.test_error_handling()
        
        # Summary
        successful_queries = sum(1 for r in query_results if r["status"] == "success")
        total_queries = len(query_results)
        responses_with_content = sum(1 for r in query_results if r.get("has_content", False))
        
        print("\n📊 Test Summary")
        print("=" * 20)
        print(f"Successful Queries: {successful_queries}/{total_queries}")
        print(f"Responses with Content: {responses_with_content}/{total_queries}")
        print(f"Agent Identity: {'✅' if identity_ok else '❌'}")
        print(f"Error Handling: {'✅' if error_handling_ok else '❌'}")
        
        overall_success = successful_queries > 0 and responses_with_content > 0 and identity_ok
        
        return {
            "status": "success" if overall_success else "failed",
            "successful_queries": successful_queries,
            "total_queries": total_queries,
            "responses_with_content": responses_with_content,
            "agent_identity": identity_ok,
            "error_handling": error_handling_ok,
            "query_results": query_results
        }

async def main():
    """Main function to run the simple test suite."""
    if len(sys.argv) > 1:
        agent_resource_name = sys.argv[1]
    else:
        agent_resource_name = None
    
    try:
        # Create tester instance
        tester = SimpleCymbalBotTester(agent_resource_name)
        
        # Run simple test suite
        results = await tester.run_simple_test_suite()
        
        # Save results to file
        with open("simple_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Test results saved to simple_test_results.json")
        
        if results["status"] == "success":
            print("\n🎉 Basic tests passed! CymbalBot is responding correctly.")
            print("Note: RAG functionality requires a deployed RAG API.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the results above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite failed to initialize: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
