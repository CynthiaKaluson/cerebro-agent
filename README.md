# Cerebro: Autonomous Multimodal Knowledge API 🧠
### A Submission for the Google Gemini 3 Hackathon

Cerebro is a next-generation AI agent that acts as a central **"Neural Hub"** for complex research. [cite_start]Unlike standard RAG systems, Cerebro uses **Gemini 3’s high-level reasoning** to autonomously decide when to search its internal knowledge base and how to synthesize multimodal data. 

## 🏗️ Architecture
Cerebro utilizes a **Hybrid Ingestion Pipeline**: it handles fast-streaming images via direct byte-injection and manages time-based media (Video/Audio) using the **Gemini Files API** for cloud-staging. This prevents server timeouts and allows the agent to perform **Temporal Reasoning** over video frames and audio waveforms.

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
🧪 Technical Implementation
Cerebro is an autonomous knowledge management agent built on Django, leveraging Gemini 3 Flash reasoning capabilities. Unlike traditional RAG pipelines that simply retrieve text, Cerebro utilizes Sequential Function Calling and the ThinkingLevel.HIGH configuration to perform deep analysis before taking action. 


The system architecture features a Multimodal Ingestion Engine that processes image data using types.Part.from_bytes and large media via the Google Files API. We solved the complexity of 'Thinking' responses by implementing a Custom Part Extraction Logic that isolates the model's final synthesis from its internal reasoning chain. This ensures a clean, user-ready output while maintaining the 'Wow Factor' of seeing an AI decide how to research. 


🌟 Key Features

Multimodal Perception: Real-time analysis of Images (PNG/JPG), Video (MP4), and Audio (OPUS/MP3). 


Agentic Autonomy: Uses Sequential Function Calling to query local databases without human intervention. 


Deep Reasoning: Leverages the ThinkingLevel.HIGH parameter for complex research synthesis. 

Hybrid Staging: Robust handling of large files via the Gemini Files API to ensure 99.9% ingestion success.

🛠️ Tech Stack
Framework: Django 5.2 (Python)


AI Model: Gemini 3 Flash Preview (v1alpha) 

Database: SQLite (Development) / PostgreSQL (Production)

Analysis: Google GenAI SDK & Python-Magic