"""
Microsoft Foundry IQ Integration for StudyMate AI

Grounded knowledge retrieval from Microsoft Learn with citations and semantic search.
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Configuration
AZURE_PROJECT_CONNECTION_STRING = os.getenv("AZURE_PROJECT_CONNECTION_STRING")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "microsoft-learn-index")


def foundry_search(query: str, num_results: int = 5, certification: str = None) -> List[Dict[str, str]]:
    """
    Search using Microsoft Foundry IQ for grounded knowledge retrieval.
    
    Args:
        query: Search query for certification content
        num_results: Number of results to return
        certification: Optional certification filter (e.g., "AZ-204")
    
    Returns:
        List of results with title, content, url, citation, relevance_score
    
    Example:
        results = foundry_search("Azure Functions triggers", certification="AZ-204")
    """
    
    # Check if Foundry IQ is configured
    if not all([AZURE_PROJECT_CONNECTION_STRING, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY]):
        return _fallback_to_basic_search(query, num_results)
    
    try:
        from azure.ai.projects import AIProjectClient
        from azure.identity import DefaultAzureCredential
        from azure.search.documents import SearchClient
        from azure.core.credentials import AzureKeyCredential
        
        # Initialize Foundry IQ through Azure AI Projects
        project_client = AIProjectClient.from_connection_string(
            conn_str=AZURE_PROJECT_CONNECTION_STRING,
            credential=DefaultAzureCredential()
        )
        
        # Initialize Azure AI Search for grounded retrieval
        search_client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX,
            credential=AzureKeyCredential(AZURE_SEARCH_KEY)
        )
        
        # Build search query with certification filter
        search_filter = None
        if certification:
            search_filter = f"certification eq '{certification}'"
        
        # Perform semantic search with Foundry IQ
        search_results = search_client.search(
            search_text=query,
            filter=search_filter,
            top=num_results,
            include_total_count=True,
            query_type="semantic",  # Semantic search for better relevance
            semantic_configuration_name="default"
        )
        
        # Process results with citations
        results = []
        for result in search_results:
            results.append({
                "title": result.get("title", "Untitled"),
                "content": result.get("content", "")[:500] + "...",  # Preview
                "url": result.get("url", ""),
                "citation": result.get("source", "Microsoft Learn"),
                "relevance_score": result.get("@search.score", 0),
                "certification": result.get("certification", ""),
                "foundry_iq": True  # Flag that this came from Foundry IQ
            })
        
        return results
        
    except ImportError:
        print("[INFO] Foundry IQ libraries not installed. Using fallback search.")
        return _fallback_to_basic_search(query, num_results)
    except Exception as e:
        print(f"[WARNING] Foundry IQ error: {e}. Using fallback search.")
        return _fallback_to_basic_search(query, num_results)


def _fallback_to_basic_search(query: str, num_results: int) -> List[Dict[str, str]]:
    """
    Fallback to basic web search if Foundry IQ not configured.
    """
    try:
        from tools.web_search import web_search
        basic_results = web_search(query, num_results)
        
        # Convert to Foundry IQ format
        return [
            {
                "title": r["title"],
                "content": r["snippet"],
                "url": r["link"],
                "citation": "Web Search (SerpAPI)",
                "relevance_score": 0.5,
                "certification": "",
                "foundry_iq": False
            }
            for r in basic_results
        ]
    except Exception as e:
        return [{
            "title": "Search Unavailable",
            "content": f"Please configure Foundry IQ or SerpAPI. Error: {e}",
            "url": "",
            "citation": "Error",
            "relevance_score": 0,
            "certification": "",
            "foundry_iq": False
        }]


def search_microsoft_learn(topic: str, certification: str = None, num_results: int = 3) -> List[Dict[str, str]]:
    """
    Search specifically in Microsoft Learn documentation using Foundry IQ.
    
    Args:
        topic: What to search for
        certification: Filter by certification (e.g., "AZ-204")
        num_results: Number of results
    
    Returns:
        Grounded results from Microsoft Learn with citations
    """
    enhanced_query = f"Microsoft Learn {topic}"
    if certification:
        enhanced_query = f"{certification} {topic} Microsoft Learn documentation"
    
    return foundry_search(enhanced_query, num_results, certification)


def format_foundry_results(results: List[Dict[str, str]], max_results: int = 3) -> str:
    """
    Format Foundry IQ results for agent consumption with citations.
    
    Args:
        results: List of search results from Foundry IQ
        max_results: Maximum results to format
    
    Returns:
        Formatted string with grounded, cited content
    """
    if not results:
        return "[NO RESULTS] Foundry IQ search returned no results."
    
    formatted = "[FOUNDRY IQ KNOWLEDGE RETRIEVAL]\n"
    formatted += "[Grounded Results from Microsoft Intelligence Layer]\n\n"
    
    for i, result in enumerate(results[:max_results], 1):
        iq_badge = "🔷 [FOUNDRY IQ]" if result.get("foundry_iq") else "[WEB]"
        formatted += f"{i}. {iq_badge} {result['title']}\n"
        formatted += f"   Citation: {result['citation']}\n"
        if result.get('certification'):
            formatted += f"   Certification: {result['certification']}\n"
        formatted += f"   Relevance: {result.get('relevance_score', 0):.2f}\n"
        formatted += f"   URL: {result['url']}\n"
        formatted += f"   Content: {result['content']}\n\n"
    
    formatted += "[END FOUNDRY IQ RESULTS]\n"
    return formatted


# Foundry IQ Tool Metadata
FOUNDRY_TOOL_METADATA = {
    "foundry_search": {
        "name": "foundry_search",
        "description": "Search using Microsoft Foundry IQ - grounded knowledge retrieval with citations from Microsoft Learn",
        "parameters": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results (default: 5)", "default": 5},
            "certification": {"type": "string", "description": "Filter by certification (e.g., AZ-204)", "optional": True}
        },
        "returns": "Grounded results with citations and relevance scores",
        "iq_layer": "Foundry IQ"
    },
    "search_microsoft_learn": {
        "name": "search_microsoft_learn",
        "description": "Search specifically in Microsoft Learn documentation with Foundry IQ semantic search",
        "parameters": {
            "topic": {"type": "string", "description": "Topic to search"},
            "certification": {"type": "string", "description": "Certification filter", "optional": True},
            "num_results": {"type": "integer", "description": "Number of results (default: 3)", "default": 3}
        },
        "returns": "Microsoft Learn content with citations",
        "iq_layer": "Foundry IQ"
    }
}


if __name__ == "__main__":
    # Test Foundry IQ integration
    print("[TEST] Microsoft Foundry IQ Integration\n")
    
    if not all([AZURE_PROJECT_CONNECTION_STRING, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY]):
        print("[SETUP REQUIRED]")
        print("Add to .env:")
        print("  AZURE_PROJECT_CONNECTION_STRING=your_connection_string")
        print("  AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net")
        print("  AZURE_SEARCH_KEY=your_search_key")
        print("  AZURE_SEARCH_INDEX=microsoft-learn-index")
        print("\nGet these from: https://portal.azure.com")
        print("Using fallback search for now...\n")
    
    # Test search
    print("Testing foundry_search()...")
    results = foundry_search("Azure Functions Python triggers", num_results=3, certification="AZ-204")
    print(format_foundry_results(results))
    
    # Test Microsoft Learn specific search
    print("\nTesting search_microsoft_learn()...")
    docs = search_microsoft_learn("API authentication", certification="AZ-204", num_results=2)
    print(format_foundry_results(docs, max_results=2))
    
    print("[TEST] Complete!")
    print(f"\n[STATUS] Foundry IQ Active: {results[0].get('foundry_iq', False) if results else False}")
