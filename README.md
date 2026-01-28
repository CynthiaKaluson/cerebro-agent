# Cerebro AI Agent 🧠

## Architecture Overview
The following diagram illustrates how Cerebro processes multimodal inputs and uses Gemini 3 Reasoning to call local database tools.

```mermaid
graph TD
    A[User/Client] -->|Multimodal Upload| B(Django API: process-file)
    A -->|Text Query| C(Django API: chat)
    B -->|Ingest| D[(PostgreSQL/SQLite)]
    B -->|Analysis| E[Gemini 3 Flash]
    E -->|Metadata| D
    C -->|Reasoning| F{Gemini 3 Thinking}
    F -->|Tool Call| G[search_local_records]
    G -->|Context| D
    D -->|Results| F
    F -->|Final Answer| A


Cerebro: Autonomous Multimodal Research Agent
Built for the Google Gemini 3 Hackathon

Cerebro is a central "brain" that uses Gemini 3's advanced reasoning to synthesize knowledge across text, audio, and video.

🚀 Key Features (WIP)
- Multimodal Synthesis: Reasoning across MP4, MP3, and PDF.
- Agentic Workflows: Autonomous tool-use for deep research.
- Thought Signatures: Persistent reasoning states.

🛠️ Tech Stack
- Backend: Django & Django REST Framework
- AI: Google Gemini 3 (Flash & Pro)
- Database: PostgreSQL