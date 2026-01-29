"""Prompt templates for content generation."""

# Theory generation prompts
THEORY_PROMPTS = {
    "notes": """Generate comprehensive study notes on the following topic:

TOPIC: {topic}

Create well-organized notes that include:
1. Introduction and overview
2. Key concepts and definitions
3. Important points and explanations
4. Examples where relevant
5. Summary or key takeaways

Target length: {max_length}

Use proper markdown formatting with headings, bullet points, and emphasis where appropriate.
Cite your sources using 📚 for course materials and 🌐 for web sources.
""",

    "summary": """Create a concise summary of the following topic:

TOPIC: {topic}

The summary should:
1. Capture the essential concepts
2. Be clear and to the point
3. Highlight the most important information
4. Be suitable for quick revision

Target length: {max_length} (aim for brevity)

Use markdown formatting. Cite sources with 📚 (course) and 🌐 (web).
""",

    "study_guide": """Create a comprehensive study guide for:

TOPIC: {topic}

Include the following sections:
1. **Learning Objectives**: What students should understand
2. **Key Concepts**: Core ideas and definitions
3. **Detailed Explanations**: In-depth coverage of each concept
4. **Practice Questions**: Self-assessment questions
5. **Common Mistakes**: What to avoid
6. **Further Reading**: Suggested resources

Target length: {max_length}

Format as a proper study guide with clear sections. Cite with 📚 and 🌐.
""",

    "explanation": """Provide a clear, educational explanation of:

TOPIC: {topic}

Your explanation should:
1. Start with the basics
2. Build up to more complex aspects
3. Use analogies and examples
4. Be suitable for a university student

Target length: {max_length}

Use clear language and markdown formatting. Cite sources with 📚 and 🌐.
"""
}

# Code generation prompts
CODE_PROMPTS = {
    "example": """Generate a code example demonstrating:

TOPIC: {topic}
LANGUAGE: {language}

Requirements:
- Complete, working code
- Clear structure
- Good variable names
- {comments_instruction}
- Example usage/output

{test_instruction}
""",

    "solution": """Provide a solution for the following programming problem:

PROBLEM: {topic}
LANGUAGE: {language}

Requirements:
- Working solution
- Efficient implementation
- Proper error handling
- {comments_instruction}

{test_instruction}
""",

    "template": """Create a code template for:

PURPOSE: {topic}
LANGUAGE: {language}

Include:
- Basic structure
- TODO comments for customization
- Example placeholders
- {comments_instruction}
"""
}

# Chat prompts
CHAT_PROMPTS = {
    "general": """You are an AI learning assistant for a university course platform.

Your role:
- Help students understand course materials
- Answer questions clearly and educationally
- Provide examples when helpful
- Cite sources (📚 course, 🌐 web)
- Be encouraging and supportive

Remember to base answers on course materials first, then supplement with web research if needed.
""",

    "search": """The student is searching for information. Provide relevant excerpts and explain them.

Query: {query}

Found in course materials:
{context}

{web_context}

Provide a helpful response that:
1. Answers the query directly
2. References specific materials
3. Offers to explain further if needed
""",

    "explain": """The student wants an explanation. Use the course materials as your primary source.

Topic to explain: {topic}

Course context:
{context}

Provide a clear, educational explanation suitable for a university student.
""",

    "generate_request": """The student has requested generated content.

Request: {request}
Type: {type}

Course context:
{context}

Generate the requested content while:
1. Staying grounded in course materials
2. Maintaining academic quality
3. Being educational and helpful
"""
}

# Validation prompts
VALIDATION_PROMPTS = {
    "grounding_check": """Analyze the following generated content and determine how well it's grounded in the source materials.

GENERATED CONTENT:
{content}

SOURCE MATERIALS:
{sources}

Evaluate:
1. What percentage of claims are supported by sources?
2. Are there any unsupported claims?
3. Are sources properly cited?
4. Is the content accurate to the sources?

Provide a grounding score from 0-100 and list any issues.
""",

    "relevance_check": """Evaluate how relevant the following content is to the requested topic.

TOPIC: {topic}

CONTENT:
{content}

Evaluate:
1. Does the content address the topic directly?
2. Is the content complete for the topic?
3. Is there irrelevant information?

Provide a relevance score from 0-100 and explain.
"""
}
