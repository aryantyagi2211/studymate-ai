"""
Tools package for StudyMate AI agents.
Provides external capabilities including:
- Microsoft Foundry IQ (grounded knowledge retrieval)
- Web search (SerpAPI fallback)
- Documentation lookup
"""

from .web_search import web_search, search_documentation
from .foundry_search import foundry_search, search_microsoft_learn, format_foundry_results

__all__ = [
    'web_search', 
    'search_documentation',
    'foundry_search',
    'search_microsoft_learn',
    'format_foundry_results'
]
