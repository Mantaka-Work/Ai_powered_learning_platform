"""LangChain chains and prompts for RAG operations."""
from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from app.config import settings


class RAGChains:
    """LangChain chains for RAG-based responses."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=settings.GENERATION_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_GENERATION_TOKENS
        )
    
    async def generate_response(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        web_context: Optional[str] = None
    ) -> str:
        """
        Generate a response using RAG with course context.
        
        Args:
            query: User query
            context: Retrieved course material context
            chat_history: Previous conversation messages
            web_context: Optional web search results
        
        Returns:
            Generated response
        """
        system_prompt = self._build_system_prompt(context, web_context)
        
        print(f"[RAGChains] Context length: {len(context)} chars")
        print(f"[RAGChains] Context preview: {context[:500]}..." if len(context) > 500 else f"[RAGChains] Context: {context}")
        
        messages = [SystemMessage(content=system_prompt)]
        
        # Add chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Last 10 messages
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=query))
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def generate_response_stream(
        self,
        query: str,
        context: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        web_context: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using RAG.
        
        Yields chunks of the response as they're generated.
        """
        system_prompt = self._build_system_prompt(context, web_context)
        
        print(f"[RAGChains-Stream] Context length: {len(context)} chars")
        print(f"[RAGChains-Stream] Context preview: {context[:500]}..." if len(context) > 500 else f"[RAGChains-Stream] Context: {context}")
        
        messages = [SystemMessage(content=system_prompt)]
        
        if chat_history:
            for msg in chat_history[-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=query))
        
        # Use astream for streaming responses
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content
    
    def _build_system_prompt(self, context: str, web_context: Optional[str] = None) -> str:
        """Build the system prompt with context."""
        prompt = """You are an AI learning assistant for a university course platform.
Your role is to help students understand course materials, answer questions, and provide explanations.

CRITICAL INSTRUCTIONS - YOU MUST FOLLOW THESE:
1. Answer ONLY using the information provided in the COURSE MATERIALS CONTEXT below
2. If the answer IS in the context, provide a detailed, helpful answer citing the specific source
3. If the answer is NOT in the context, say: "I couldn't find specific information about this in your course materials. The available materials cover: [briefly list what IS covered]"
4. NEVER say "I don't have access to your files" - you DO have access through the context below
5. NEVER say "I cannot access external files" - the relevant content is PROVIDED below
6. Always cite which source the information comes from using 📚

COURSE MATERIALS CONTEXT (USE THIS TO ANSWER):
---
{context}
---

Remember: The context above contains the relevant excerpts from the uploaded course materials. Base your answer on this content.
""".format(context=context if context else "No course materials were found matching this query.")
        
        if web_context:
            prompt += """

SUPPLEMENTARY WEB SEARCH RESULTS (use only if course materials don't cover the topic):
---
{web_context}
---

Note: Prefer course materials (📚) over web results (🌐).
""".format(web_context=web_context)
        
        return prompt
    
    async def summarize_content(self, content: str, max_length: Optional[int] = None) -> str:
        """Summarize course content."""
        prompt = f"""Summarize the following course content in a clear, educational manner.
Focus on key concepts, definitions, and important points.
{'Keep the summary under ' + str(max_length) + ' words.' if max_length else ''}

Content:
{content}

Summary:"""
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        return response.content


# Singleton instance
_chains = None


def get_chains() -> RAGChains:
    """Get or create chains singleton."""
    global _chains
    if _chains is None:
        _chains = RAGChains()
    return _chains
