# Atlas Financial Assistant 🏦

**Atlas** is a sophisticated, GenAI-powered financial assistant designed to handle complex banking queries with professional precision. It utilizes a state-of-the-art Hybrid Intelligence core (Gemini + Llama) to provide accurate information on loans, savings, mortgages, and general financial advice.

## ✨ Key Features

*   **Hybrid Intelligence Core**: Seamlessly switches between Google's Gemini and Groq's Llama models for optimal performance and robustness.
*   **Stateful Conversations**: Powered by **LangGraph**, enabling the AI to maintain context and manage complex multi-step workflows.
*   **Financial RAG Engine**: Optimized Retrieval-Augmented Generation for retrieving specific banking policies, rates, and product details.
*   **Live Web Search**: Integrated with **Tavily** and **DuckDuckGo** to fetch real-time financial data when internal knowledge is insufficient.
*   **Sleek Cyber-Finance UI**: A modern, glassmorphism-based interface built with React and Framer Motion, featuring a "living" background and dynamic animations.

## 🚀 Tech Stack

-   **Frontend**: React, Vite, Framer Motion, Lucide Icons (Vanilla CSS for custom glassmorphism).
-   **Backend**: Python (FastAPI).
-   **AI Orchestration**: LangGraph, LangChain.
-   **LLMs**: Google Gemini 1.5 Flash, Llama 3 (via Groq).
-   **Search Tools**: Tavily API, DuckDuckGo, Wikipedia.

## 📂 Project Structure

-   `backend/`
    -   `app/agents/` - Core AI logic, graph definitions, and prompt engineering.
    -   `main.py` - FastAPI entry point.
-   `frontend/` - React application source code.

## ⚡ Quick Start

### 1. Prerequisites
-   Python 3.10+
-   Node.js & npm

### 2. Backend Setup
```bash
# Navigate to the root folder
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r backend/requirements.txt

# Run the backend server
uvicorn backend.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Environment Variables
Create a `.env` file in the root `backend/` directory with the following keys:
```ini
GOOGLE_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
TAVILY_API_KEY=your_tavily_key
```

## 📸 Screenshots
*(Add screenshots of the Atlas UI here)*

## 🤝 Contribution
Feel free to fork this repository and submit pull requests to enhance Atlas's capabilities!
