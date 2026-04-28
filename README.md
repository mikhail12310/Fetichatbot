# Fetichatbot 🤖

https://github.com/user-attachments/assets/f8849b85-dc90-4bd3-8c11-cbef5388a53b

Fetichatbot is a powerful, intelligent SQL Chatbot that allows users to chat with their data. Built with **FastAPI** and powered by **Google Gemini** models via **LangChain**, it enables natural language querying of structured datasets (CSV, Excel, Parquet) through an interactive web interface.

## 🚀 Features

- **Natural Language to SQL**: Ask questions in plain English and get answers directly from your data.
- **Multi-Format Ingestion**: Upload `.csv`, `.xlsx`, `.xls`, and `.parquet` files for instant analysis.
- **Dynamic Database Sync**: Automatically detects and loads data files from the `data/` directory.
- **Intelligent Fallback**: Smartly rotates between different Gemini models (Flash, Pro, Lite) to ensure high availability and performance.
- **Persistent Caching**: Speeds up repeated questions by caching responses locally.
- **Premium UI**: A sleek, modern chat interface with real-time status updates and file upload capabilities.

## 📁 Project Structure

```text
Fetichatbot/
├── backend/
│   ├── main.py             # FastAPI Server & API Endpoints
│   ├── agent.py            # LangChain SQL Agent & LLM Logic
│   ├── db_builder.py       # Database Management & File Ingestion
│   ├── requirements.txt    # Python Dependencies
│   └── database.sqlite     # Local SQLite Database
├── frontend copy/
│   ├── index.html          # Web Interface
│   ├── style.css           # Modern Styling
│   └── script.js           # Frontend Logic & API Integration
├── data/                   # Permanent datasets (CSV/Excel/Parquet)
└── .env                    # Environment variables (API Keys)
```

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Fetichatbot.git
cd Fetichatbot
```

### 2. Set up the Backend
Navigate to the backend directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file in the root directory and add your Google API Key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 🏃 Running the Application

### Start the Backend
From the root directory:
```bash
python backend/main.py
```
The server will start at `http://localhost:8000`.

### Launch the Frontend
Simply open `frontend copy/index.html` in your web browser, or use a live server extension in your IDE.

## 🌐 Deployment

### Frontend
The frontend is purely static and can be hosted for free on **GitHub Pages**, **Vercel**, or **Netlify**.

### Backend
The backend requires a Python environment. Recommended hosting platforms:
- **Render / Railway**: Ideal for SQLite-based apps with persistent disk support.
- **Vercel**: Requires a `vercel.json` configuration and ideally a migration to a cloud database like **Supabase** (as SQLite is read-only on Vercel).

## 🔒 Security
- Ensure your `.env` file is included in `.gitignore` to prevent API keys from being pushed to public repositories.
- The backend includes CORS configuration to allow secure communication with the frontend.

---
Built with ❤️ using FastAPI, LangChain, and Google Gemini.
