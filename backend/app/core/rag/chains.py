"""LangChain chains and prompts for RAG operations."""
from typing import List, Dict, Any, Optional, AsyncGenerator
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks import AsyncIteratorCallbackHandler

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
        callback = AsyncIteratorCallbackHandler()
        streaming_llm = ChatOpenAI(
            model=settings.OPENAI_CHAT_MODEL,
            temperature=settings.GENERATION_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            max_tokens=settings.MAX_GENERATION_TOKENS,
            streaming=True,
            callbacks=[callback]
        )
        
        system_prompt = self._build_system_prompt(context, web_context)
        messages = [SystemMessage(content=system_prompt)]
        
        if chat_history:
            for msg in chat_history[-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))
        
        messages.append(HumanMessage(content=query))
        
        # Start generation in background
        import asyncio
        task = asyncio.create_task(streaming_llm.ainvoke(messages))
        
        async for token in callback.aiter():
            yield token
        
        await task
    
    def _build_system_prompt(self, context: str, web_context: Optional[str] = None) -> str:
        """Build the system prompt with context."""
        prompt = """You are an AI learning assistant for a university course platform. 
Your role is to help students understand course materials, answer questions, and provide explanations.

IMPORTANT GUIDELINES:
1. Base your answers primarily on the provided course materials
2. If course materials don't cover a topic well, use web search results (if provided)
3. Always cite your sources - indicate whether information comes from course materials (📚) or web search (🌐)
4. Be educational, clear, and helpful
5. If you're not sure about something, say so
6. For code questions, provide working examples when possible

COURSE MATERIALS CONTEXT:
{context}
""".format(context=context if context else "No relevant course materials found.")
        
        if web_context:
            prompt += """

WEB SEARCH RESULTS (use as supplementary information):
{web_context}

Note: Web results should supplement, not replace, course materials.
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
