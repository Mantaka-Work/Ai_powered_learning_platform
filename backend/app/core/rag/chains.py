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
        web_context: Optional[str] = None,
        use_general_knowledge: bool = False
    ) -> str:
        """
        Generate a response using RAG with course context.
        
        Args:
            query: User query
            context: Retrieved course material context
            chat_history: Previous conversation messages
            web_context: Optional web search results
            use_general_knowledge: If True, use general knowledge instead of course context
        
        Returns:
            Generated response
        """
        system_prompt = self._build_system_prompt(context, web_context, use_general_knowledge)
        
        print(f"[RAGChains] Context length: {len(context)} chars")
        print(f"[RAGChains] Use general knowledge: {use_general_knowledge}")
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
        web_context: Optional[str] = None,
        use_general_knowledge: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response using RAG.
        
        Yields chunks of the response as they're generated.
        """
        system_prompt = self._build_system_prompt(context, web_context, use_general_knowledge)
        
        print(f"[RAGChains-Stream] Context length: {len(context)} chars")
        print(f"[RAGChains-Stream] Use general knowledge: {use_general_knowledge}")
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
    
    def _build_system_prompt(self, context: str, web_context: Optional[str] = None, use_general_knowledge: bool = False) -> str:
        """Build the system prompt with context."""
        
        # If using general knowledge (low relevance from course materials)
        if use_general_knowledge:
            prompt = """You are an AI learning assistant for a university course platform.
The student asked a question that is NOT directly covered in their uploaded course materials.

INSTRUCTIONS:
1. Answer using your general knowledge as an AI assistant
2. Be helpful, accurate, and educational
3. Start your response with "🌐 **Based on general knowledge:**" to indicate this is not from course materials
4. If this topic MIGHT be related to their course, suggest they upload relevant materials
5. Provide clear explanations with examples where helpful"""
            
            # Add web context if available (for general knowledge + web search)
            if web_context:
                prompt += """

WEB SEARCH RESULTS (Latest information from the internet):
---
{web_context}
---

Use these web results to provide up-to-date information. Cite sources with their URLs when relevant.""".format(web_context=web_context)
            
            prompt += """

Note: The following course materials were found but had low relevance to this question:
---
{context}
---

Answer the student's question using your general knowledge{web_note}.""".format(
                context=context if context else "No course materials available.",
                web_note=" and the web search results" if web_context else ""
            )
            
            return prompt
        
        # Normal mode: use course materials
        prompt = """You are an AI learning assistant for a university course platform.
Your role is to help students understand course materials, answer questions, and provide explanations.

CRITICAL INSTRUCTIONS:
1. The COURSE MATERIALS CONTEXT below contains relevant content from the student's uploaded files
2. USE this context to answer the question - explain concepts, show code examples, provide detailed answers
3. If the context contains code, explain it step by step
4. If the context contains explanations or theory, summarize and elaborate on it
5. Start your response with "📚 **Based on course materials:**" to indicate this is from their uploaded content
6. Always be helpful and educational - use the context to teach
7. Cite specific sources when possible

COURSE MATERIALS CONTEXT:
---
{context}
---
""".format(context=context if context else "No course materials were found matching this query.")
        
        # Add web context if web search was enabled (course context + web supplement)
        if web_context:
            prompt += """
🌐 WEB SEARCH RESULTS (Supplementary latest information):
---
{web_context}
---

IMPORTANT: 
- Primarily use the COURSE MATERIALS (📚) to answer
- Use WEB RESULTS (🌐) to supplement with latest news, updates, or additional context
- Clearly indicate when citing web sources vs course materials
- If web results contradict course materials, mention both perspectives
""".format(web_context=web_context)
        
        prompt += """
Based on the above context, answer the student's question thoroughly and helpfully."""
        
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
