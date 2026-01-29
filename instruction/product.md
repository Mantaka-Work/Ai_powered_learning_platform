# AI-Powered Supplementary Learning Platform - Product Requirements

## Project Overview

Build an AI-powered supplementary learning platform that enhances university courses by organizing content, enabling intelligent retrieval, generating validated learning materials, and providing a conversational interface for seamless interaction.

**Key Enhancement:** Platform integrates with Perplexity's web search capabilities to augment course materials with real-time research data and current information.

---

## 🎯 PART 1: Content Management System (CMS)

### Must-Have Requirements

#### 1.1 Admin Content Upload
- **Upload file types:**
  - PDF files (lecture slides, research papers)
  - PowerPoint/PPTX (presentations)
  - Code files (.py, .js, .java, .cpp, etc.)
  - Text files (notes, documentation)
  - Markdown files
  - Word documents (.docx)

- **Core functionality:**
  - Admin/Instructor can upload course materials
  - Simple drag-and-drop or file picker interface
  - Multiple file upload support
  - File size validation (max 50MB per file)
  - Progress indicator during upload

#### 1.2 Content Organization & Categorization
- **Two main categories:**
  - Theory (lecture slides, notes, PDFs, documentation)
  - Lab (code files, assignments, practical materials)

- **Metadata tracking:**
  - Topic/Subject name
  - Week number
  - Tags (searchable keywords)
  - Content type (PDF, code, slide, note)
  - Programming language (for code files)
  - Upload date and uploader info

#### 1.3 Content Browsing (Students)
- **Browse functionality:**
  - View all uploaded materials for a course
  - Filter by category (Theory/Lab)
  - Filter by week
  - Sort by upload date, topic, or content type
  - Display material metadata and preview

- **Content preview:**
  - PDF preview (first page)
  - Code file syntax highlighting
  - Document summaries

- **Download materials:**
  - Direct download link
  - Track download history (optional)

#### 1.4 Content Management (Admin)
- **Admin dashboard:**
  - View all uploaded materials
  - Edit metadata (topic, tags, week)
  - Delete materials
  - Bulk upload support
  - Search by filename or topic

### Bonus Features (Part 1)

- [ ] Batch metadata assignment (upload multiple files, assign metadata at once)
- [ ] Material versioning (track changes over time)
- [ ] Auto-extraction of metadata from file names
- [ ] Integration with institutional file systems (OneDrive, Google Drive)

---

## 🔍 PART 2: Intelligent Search Engine (Semantic Search / RAG-Based)

### Must-Have Requirements

#### 2.1 Semantic Search Core
- **Natural language search:**
  - Type questions or topics in plain English
  - System understands meaning, not just keywords
  - Returns relevant materials regardless of exact word match

- **Search capabilities:**
  - Search within course materials only
  - Return top 5 most relevant results
  - Display relevance score/confidence
  - Show excerpt/preview of matched content
  - Show source material (which PDF, which file)

#### 2.2 Search Features
- **Search filtering:**
  - Filter by category (Theory/Lab)
  - Filter by content type (PDF, code, notes)
  - Filter by week
  - Filter by programming language (for code search)

- **Search results display:**
  - Document title and source
  - Relevance score (0-100%)
  - Text excerpt matching the query
  - Link to full material
  - Content type indicator (PDF, Code, etc.)

#### 2.3 Search Indexing
- **Automatic processing:**
  - When material uploaded, automatically extract text
  - Break text into chunks (semantic units)
  - Create embeddings (AI representation of meaning)
  - Store in vector database
  - Ready for search within minutes of upload

#### 2.4 Code-Specific Search (Important for Lab)
- **Syntax-aware code search:**
  - Understand code structure (functions, classes, imports)
  - Search by functionality (not just variable names)
  - Example: "Find code that parses JSON" returns relevant snippets
  - Language-specific search (find Python examples, Java examples, etc.)

#### 2.5 Web Search Integration (NEW!)
- **Perplexity Web Search Integration:**
  - When student's query not sufficiently answered by course materials
  - System automatically triggers web search via Perplexity API
  - Fetch latest research, documentation, trends related to topic
  - Clearly label web search results vs course materials
  - Include source citations and URLs

- **Web search triggers:**
  - Query has low relevance score (<40%) in course materials
  - User explicitly requests "search web for this topic"
  - Topic is current/trending (requires fresh data)
  - Question about tools/technologies with frequent updates

- **Web search display:**
  - Separate section: "Additional Resources from Web"
  - Show source website, date, relevance
  - Provide direct link to original source
  - Include summarized excerpt
  - Mark clearly as "External Source"

### Bonus Features (Part 2)

- [ ] Faceted search (multiple filter combinations)
- [ ] Search suggestions/autocomplete
- [ ] Recent search history
- [ ] Saved searches
- [ ] Search analytics (what students search for)
- [ ] Typo tolerance ("serach" → "search")
- [ ] Query expansion (synonyms, related terms)

---

## 📚 PART 3: AI-Generated Learning Materials

### Must-Have Requirements

#### 3.1 Theory Content Generation
- **Generate from topics:**
  - User enters topic/concept name
  - System searches uploaded materials for related content
  - **NEW:** System also searches web via Perplexity for current info
  - AI generates original learning material based on course + web content
  - Output formats:
    - **Reading Notes:** Formatted markdown/text with clear sections
    - **Study Guides:** Bullet points, key concepts, definitions
    - **Summary:** Short condensed version (1-2 pages)

- **Content requirements:**
  - Material must be **grounded** in uploaded course materials
  - **NEW:** Can supplement with web research when necessary
  - Must cite sources (reference which materials were used)
  - Coherent, well-structured, academic tone
  - Appropriate length (2-5 pages for notes)
  - Include section headers, bullet points, clear formatting
  - Distinguish course content from web research

#### 3.2 Lab/Code Content Generation
- **Generate code examples:**
  - User enters topic/problem to solve
  - Specify programming language
  - System retrieves relevant code examples from materials
  - **NEW:** Can search web for latest syntax/best practices if needed
  - AI generates new, original code example
  - Output: Complete, working code file

- **Code requirements:**
  - Syntactically correct (no compilation errors)
  - Properly commented and documented
  - Follows good coding practices
  - Relevant to the requested topic
  - Includes example usage/test cases if applicable
  - Matches the requested programming language

- **Supported languages (minimum):**
  - Python
  - JavaScript/TypeScript
  - Java
  - C++
  - SQL

#### 3.3 Generation Process
- **Step-by-step:**
  1. User submits generation request (topic, type, language)
  2. System searches uploaded materials for context
  3. **NEW:** System queries Perplexity for current/supplementary info
  4. AI generates content using course materials + web context
  5. System validates generated content (see Part 4)
  6. Display results with validation status and source attribution
  7. User can review, download, or regenerate

- **External knowledge sources:**
  - **Course Materials:** Primary source (uploaded by instructors)
  - **Perplexity Web Search:** Secondary source (current research, examples)
  - Clearly distinguish course-specific vs web-sourced information

### Bonus Features (Part 3)

- [ ] Generate practice questions from topic
- [ ] Generate exam-style questions with answers
- [ ] Generate visual aids/diagrams (ASCII art at minimum)
- [ ] Multi-language support for code examples
- [ ] Generate video transcripts/scripts
- [ ] Difficulty level selection (beginner, intermediate, advanced)

---

## ✅ PART 4: Content Validation & Evaluation System

### Must-Have Requirements

#### 4.1 Code Validation
- **For generated code:**
  - Syntax checking (does code compile?)
  - Linting (follows code standards)
  - Basic static analysis (unused variables, potential bugs)
  - If possible: Attempt to run code (sandboxed execution)

- **Validation output:**
  - Pass/Fail status
  - Specific issues found (if any)
  - Suggestions for fixes
  - Validation score (0-100%)

#### 4.2 Theory Content Validation
- **For generated notes/materials:**
  - **Grounding check:** Is content based on course materials?
    - Count how many sentences cite sources
    - Identify if content contradicts uploaded materials
  
  - **Structure check:** Is formatting proper?
    - Has clear headings
    - Has bullet points/organization
    - Readable and scannable
  
  - **Relevance check:** Is content relevant to topic?
    - Does it answer what was asked?
    - Does it stay on topic?
    - Relevance score (0-100%)

- **Web source validation:**
  - Are web sources credible? (check domain authority)
  - Are sources recent and relevant?
  - Are sources properly cited with URLs?

#### 4.3 Evaluation Scoring
- **Overall validation score:**
  - Code: Syntax + Logic + Standards + Execution (if possible)
  - Theory: Grounding + Structure + Relevance + Accuracy + Source Credibility
  - Display as: 0-100% or Pass/Warn/Fail

- **Validation status:**
  - ✅ Validated (ready to use)
  - ⚠️ Warn (usable but has issues)
  - ❌ Failed (do not use, regenerate)

#### 4.4 Validation Display
- **Show to users:**
  - Validation status badge
  - Detailed validation report
  - Specific issues found
  - Suggestions to improve
  - Option to regenerate if failed
  - Source attribution (course vs web)

### Bonus Features (Part 4)

- [ ] Automated test case generation and execution
- [ ] Plagiarism detection (compare with existing materials)
- [ ] Rubric-based evaluation
- [ ] User feedback loop (students rate quality of generated content)
- [ ] Machine learning based quality scoring
- [ ] Citation accuracy checking

---

## 💬 PART 5: Conversational Chat Interface

### Must-Have Requirements

#### 5.1 Chat Basics
- **Core chat functionality:**
  - Text input box (type questions/requests)
  - Chat message display (conversation history)
  - Send button
  - Clean, intuitive UI
  - Mobile-responsive design

#### 5.2 Chat Features
Through the chat interface, users should be able to:

**A. Search materials** (MUST use Part 2)
- Question: "What is recursion?"
- Response: Searches materials, returns relevant excerpts
- Format: "I found information in [Material X]: [excerpt]..."
- **NEW:** If no good match, also includes web search results

**B. Get summaries/explanations** (MUST use Part 1)
- Question: "Summarize lecture 5"
- Response: AI reads uploaded material, provides explanation
- Must cite which material was referenced

**C. Request content generation** (MUST use Part 3)
- Question: "Generate notes on linked lists"
- Response: Generates learning material, shows validation status
- Must show sources used (course materials + web if applicable)

**D. Ask follow-up questions** (MUST maintain context)
- Question 1: "What is an API?"
- Question 2: "Can you give an example?" (context: knows we discussed APIs)
- Response: Remembers previous conversation, uses context

**E. Multi-turn conversations**
- Maintain full conversation history in current session
- Reference earlier messages
- Build context over time
- Example:
  - Q: "Tell me about Python"
  - Q: "What are functions?"
  - Q: "How do I use them in the program?" (context: Python functions)
  - System understands the context chain

#### 5.3 Chat UI Components
- **Message display:**
  - User messages right-aligned, blue
  - Assistant messages left-aligned, grey
  - Timestamp for each message
  - Source/reference indicators
  - Code blocks with syntax highlighting
  - Markdown formatting support
  - **NEW:** Web source badges (when referencing web search results)

- **Input features:**
  - Auto-focus input box
  - Placeholder text with examples
  - Typing indicator ("Assistant is typing...")
  - Clear button (clear entire conversation)
  - Export chat (download as PDF/text)

- **Session management:**
  - Create new chat session
  - View previous sessions
  - Save conversation
  - Delete old chats

#### 5.4 Chat Context Management
- **Conversation memory:**
  - Remember all messages in current session
  - Store conversation history in database
  - Load history when session reopened
  - Maintain context across messages (AI knows what was discussed)

- **Context window:**
  - Pass last 10-15 messages to AI
  - Summarize older messages if session is long
  - Prevent information loss

- **Web search in chat:**
  - When relevant, system suggests "Search web for more info?"
  - User can accept to trigger Perplexity search
  - Results integrated into conversation naturally

### Bonus Features (Part 5)

- [ ] Voice input (speak instead of type)
- [ ] Voice output (AI speaks responses)
- [ ] Chat with multiple courses in same session
- [ ] Collaborative chat (share session with classmates)
- [ ] Chat bot personality/tone customization
- [ ] Citation panel (show all sources used in conversation)
- [ ] Feedback buttons (helpful, not helpful, regenerate)
- [ ] Pin important messages

---

## 🎓 System-Wide Requirements

### Performance
- **Search results:** Return within 2 seconds (course materials + optional web search)
- **Chat response:** Start streaming within 5 seconds
- **Content generation:** Complete within 30-60 seconds
- **File upload:** Support files up to 50MB
- **Web search:** Add <2 seconds when triggered

### Usability
- **Two user types:**
  - **Admin/Instructor:** Upload, manage, monitor
  - **Student:** Browse, search, chat, download

- **Authentication:**
  - Login required (username/password or SSO)
  - Different access levels (admin vs student)
  - Course-specific access control

- **UI/UX:**
  - Clean, modern design
  - Mobile-friendly
  - Dark/light mode (bonus)
  - Accessibility standards (WCAG 2.1 AA)

### Data Privacy & Security
- **Must have:**
  - Secure file storage (encrypted at rest)
  - Secure API communication (HTTPS)
  - User authentication
  - Course-specific data isolation
  - GDPR compliance (if EU users)
  - **NEW:** Safe Perplexity API integration (no data leakage to web search)

---

## 📋 Summary: Must-Have vs Bonus

### ✅ MUST IMPLEMENT (MVP - Minimum Viable Product)

**Part 1 - CMS:**
- [ ] File upload (PDF, PPTX, code, text)
- [ ] Categorize as Theory/Lab
- [ ] Add metadata (topic, week, tags)
- [ ] Browse/download materials
- [ ] Admin dashboard

**Part 2 - Search:**
- [ ] Semantic search (natural language)
- [ ] Return top 5 results with excerpts
- [ ] Filter by category/type/week
- [ ] Show source materials
- [ ] Basic code search
- [ ] **NEW:** Perplexity web search integration for low-relevance queries

**Part 3 - Generation:**
- [ ] Generate theory notes from topic
- [ ] Generate code examples
- [ ] Ground in uploaded materials
- [ ] Cite sources
- [ ] **NEW:** Augment with web research when needed

**Part 4 - Validation:**
- [ ] Code syntax checking + validation score
- [ ] Theory grounding check
- [ ] Display validation status to user
- [ ] Show issues/suggestions
- [ ] **NEW:** Validate web source credibility

**Part 5 - Chat:**
- [ ] Chat interface with message display
- [ ] Search through chat
- [ ] Generate content through chat
- [ ] Maintain conversation context
- [ ] Ask follow-up questions
- [ ] **NEW:** Integrated web search suggestions in chat

### 🎁 BONUS (Nice-to-Have, Post-MVP)

- [ ] Autocomplete search suggestions
- [ ] Handwritten notes OCR
- [ ] Content-to-video generation
- [ ] Community discussion features
- [ ] Practice question generation
- [ ] Advanced code analysis
- [ ] Plagiarism detection
- [ ] Student feedback ratings
- [ ] Rubric-based evaluation
- [ ] Multi-language code support

---

## 🎯 Deliverables Checklist

### Before Submission:
- [ ] Working demo (backend API + frontend UI)
- [ ] All MUST features functional
- [ ] Sample data loaded (test course with materials)
- [ ] Sample interactions documented (search, generation, chat)
- [ ] System architecture diagram
- [ ] Database schema diagram
- [ ] API documentation
- [ ] Validation strategy explained
- [ ] **NEW:** Perplexity integration documented
- [ ] Deployment/running instructions
- [ ] README with setup steps

### Nice-to-Have for Submission:
- [ ] Video demo walkthrough
- [ ] Performance metrics
- [ ] User feedback/testing results
- [ ] Bonus features implemented
- [ ] Scalability discussion
- [ ] Future roadmap

---

## 🚀 Success Metrics

### Functional Requirements Met
- All 5 parts working correctly
- No critical bugs
- Clean code and documentation
- Perplexity integration functioning properly

### User Experience
- Chat is intuitive and fast
- Search results are relevant (70%+ relevance)
- Generated content is useful and grounded
- Web search results clearly distinguished from course materials
- UI is responsive and accessible

### System Quality
- Generated code validates correctly (90%+ pass rate)
- Theory content is well-structured
- Validation catches issues correctly
- No data loss or security issues
- Web search provides valuable supplementary information
