"""Test script for hybrid RAG chat."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.chat_service import get_chat_service
from app.services.search_service import get_search_service
from uuid import UUID


async def test_search_only():
    """Test just the search to verify context retrieval."""
    search_service = get_search_service()
    course_id = UUID("6667db80-1e3a-432b-b8b7-8baa698997a3")  # Correct course ID with embeddings
    query = "what is a nested loop?"
    
    print("Testing search service...")
    print(f"Course ID: {course_id}")
    print(f"Query: {query}")
    print("-" * 50)
    
    try:
        results = await search_service.hybrid_search(
            query=query,
            course_id=course_id,
            limit=5,
            include_web=False
        )
        
        print(f"Course results: {len(results.get('course_results', []))}")
        for i, r in enumerate(results.get("course_results", [])[:3], 1):
            print(f"\n--- Result {i} ---")
            print(f"Title: {r.get('material_title', 'N/A')}")
            print(f"Score: {r.get('relevance_score', 0):.3f}")
            print(f"Content preview: {r.get('content', '')[:200]}...")
        
        # Calculate avg relevance
        scores = [r.get('relevance_score', 0) for r in results.get('course_results', [])]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"\nAverage relevance: {avg:.3f}")
        print(f"Would use course context: {avg >= 0.2 and len(scores) > 0}")  # Updated threshold
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


async def test_rag_chain_directly():
    """Test RAG chain directly without database."""
    from app.core.rag.chains import get_chains
    
    chains = get_chains()
    
    # Test with course context
    context = """📚 [Course Source 1: C Programming Basics]
A variable in C is a named storage location in memory that holds a value of a specific data type.
Variables must be declared before use with their type and name, like: int age; float price;
Variables can be initialized at declaration: int count = 0;

📚 [Course Source 2: C Data Types]  
C supports several basic data types for variables:
- int: for integers
- float: for decimal numbers
- char: for single characters
- double: for double-precision floats"""
    
    query = "what is a variable in C?"
    
    print("\n" + "=" * 50)
    print("Testing RAG chain with course context...")
    print("=" * 50)
    print(f"Context length: {len(context)} chars")
    print(f"use_general_knowledge: False")
    print("-" * 50)
    
    print("Response:")
    async for chunk in chains.generate_response_stream(
        query=query,
        context=context,
        use_general_knowledge=False
    ):
        print(chunk, end="", flush=True)
    
    print("\n")
    
    # Test with general knowledge
    print("=" * 50)
    print("Testing RAG chain with general knowledge...")
    print("=" * 50)
    print(f"use_general_knowledge: True")
    print("-" * 50)
    
    print("Response:")
    async for chunk in chains.generate_response_stream(
        query="what is quantum computing?",
        context="No relevant course materials found.",
        use_general_knowledge=True
    ):
        print(chunk, end="", flush=True)
    
    print("\n")


if __name__ == "__main__":
    asyncio.run(test_search_only())
    asyncio.run(test_rag_chain_directly())
