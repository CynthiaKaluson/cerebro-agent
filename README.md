# Cerebro: Autonomous Multimodal Knowledge API 🧠
**A Submission for the Google Gemini 3 Hackathon**

Cerebro is a next-generation AI agent that acts as a central "Neural Hub" for complex research. Unlike standard RAG systems, Cerebro uses **Gemini 3’s high-level reasoning** to autonomously decide when to search its internal knowledge base and how to synthesize multimodal data.

## 🏗️ Architecture
```mermaid
graph TD
    A[User/Client] -->|Multimodal Upload| B(Django API: process-file)
    A -->|Natural Language Query| C(Django API: chat)
    B -->|Ingest & Analyze| E[Gemini 3 Flash]
    E -->|Structured Metadata| D[(Knowledge Store)]
    C -->|Thinking Level: High| F{Gemini 3 Reasoning}
    F -->|Autonomous Tool Call| G[search_local_records]
    G -->|Context Retrieval| D
    D -->|Search Results| F
    F -->|Synthesized Answer| A
    
    ## 🧪 Technical Implementation
Cerebro is an autonomous knowledge management agent built on Django, leveraging the Gemini 3 Flash reasoning capabilities. 
Unlike traditional RAG pipelines that simply retrieve text, Cerebro utilizes Sequential Function Calling and the ThinkingLevel.
HIGH configuration to perform deep analysis before taking action.

The system architecture features a Multimodal Ingestion Engine that processes image data using types.Part.from_bytes, storing structured insights in a relational database. 
When queried via the Agentic Chat endpoint, Cerebro initiates a high-reasoning 'Thinking' phase. 
If it determines that local context is required, it autonomously triggers the search_local_records tool.

We solved the complexity of 'Thinking' responses by implementing a Custom Part Extraction Logic that isolates the model's final synthesis from its internal reasoning chain. 
This ensures a clean, user-ready output while maintaining the 'Wow Factor' of seeing an AI decide how to research. 
This setup provides a scalable foundation for future video and audio synthesis modules.    
    
🌟 Key Features
Multimodal Perception: Real-time analysis of Images (PNG/JPG), and planned support for Video/Audio.

Agentic Autonomy: Uses Sequential Function Calling to query local databases without human intervention.

Deep Reasoning: Leverages the ThinkingLevel.HIGH parameter for complex research synthesis.

Thought Signatures: Designed to maintain reasoning context across multi-turn research sessions.

🛠️ Tech Stack
Framework: Django 5.2 (Python)

AI Model: Gemini 3 Flash Preview (v1alpha)

Database: SQLite/PostgreSQL

Analysis: Google GenAI SDK

🚀 Getting Started
pip install -r requirements.txt

python manage.py migrate

python manage.py runserver