# Fetii SQL Chatbot

A modern, professional SQL chatbot for querying rideshare data using natural language. Built with React, PostgreSQL, and Google Gemini AI.

## 🏗️ Architecture

This project has been redesigned from a Streamlit + Docker setup to a modern static frontend with serverless backend:

- **Frontend**: React (Create React App) with TailwindCSS - deployed on GitHub Pages
- **Backend**: Vercel Serverless Functions - handles AI/SQL queries
- **Database**: PostgreSQL (existing database with rideshare data)
- **AI**: Google Gemini (LangChain) - converts natural language to SQL

## 📁 Project Structure

```
Fetichatbot/
├── frontend/          # React frontend (GitHub Pages)
│   ├── src/
│   │   ├── App.js     # Main chat interface
│   │   └── index.css  # TailwindCSS styles
│   └── package.json
├── backend/           # Serverless backend (Vercel)
│   ├── api/
│   │   └── chat.js    # Chat API endpoint
│   └── package.json
├── data/
│   └── FetiiAI_Data_Austin.xlsx
└── README.md
```

## 🚀 Setup Instructions

### 1. Get Google Gemini API Key

1. Go to [AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

### 2. Deploy Backend to Vercel

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Navigate to backend directory:
   ```bash
   cd backend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Login to Vercel:
   ```bash
   vercel login
   ```

5. Deploy:
   ```bash
   vercel
   ```

6. Add environment variables in Vercel dashboard:
   - DATABASE_URL (your PostgreSQL connection string)
   - GOOGLE_API_KEY (your Gemini API key)

7. Note your Vercel app URL (e.g., `https://your-app.vercel.app`)

**Note**: Your PostgreSQL database should already have the tables (trips, riders, ride_demo) with data loaded from the original Docker setup.

### 3. Set Up Frontend

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` with your backend URL:
   ```
   REACT_APP_API_URL=https://your-vercel-app.vercel.app/api/chat
   ```

5. Test locally:
   ```bash
   npm start
   ```

### 4. Deploy to GitHub Pages

1. Push your code to GitHub

2. Install gh-pages (if not already installed):
   ```bash
   cd frontend
   npm install -D gh-pages
   ```

3. Deploy:
   ```bash
   npm run deploy
   ```

4. Enable GitHub Pages in your repository settings:
   - Go to Settings > Pages
   - Select `gh-pages` branch
   - Your site will be live at `https://yourusername.github.io/Fetichatbot/`

## 🎨 Features

- **Modern UI**: Beautiful gradient design with glassmorphism effects
- **Real-time Chat**: Interactive chat interface with loading states
- **Example Questions**: Pre-built question suggestions
- **Responsive Design**: Works on desktop and mobile
- **SQL Generation**: Automatically converts natural language to SQL
- **Data Visualization**: Returns formatted results from database queries

## 🔧 Environment Variables

### Frontend (.env)
```
REACT_APP_API_URL=https://your-vercel-app.vercel.app/api/chat
```

### Backend (Vercel Environment Variables)
```
DATABASE_URL=postgresql://username:password@host:port/database
GOOGLE_API_KEY=your_google_gemini_api_key
```

**Note**: DATABASE_URL should be your existing PostgreSQL connection string from your Docker setup.

## 📊 Database Schema

### trips
- trip_id (TEXT, PRIMARY KEY)
- user_id_booker (TEXT)
- pickup_address (TEXT)
- dropoff_address (TEXT)
- pickup_lat (FLOAT)
- pickup_lon (FLOAT)
- dropoff_lat (FLOAT)
- dropoff_lon (FLOAT)
- pickup_ts (TIMESTAMP)
- dropoff_ts (TIMESTAMP)
- rider_count (INTEGER)

### riders
- trip_id (TEXT)
- user_id (TEXT)
- PRIMARY KEY (trip_id, user_id)

### ride_demo
- user_id (TEXT, PRIMARY KEY)
- age (INTEGER)

## 🐛 Troubleshooting

### Frontend shows "API request failed"
- Check that `REACT_APP_API_URL` is set correctly in `.env`
- Ensure the backend is deployed and accessible
- Check browser console for specific error messages

### Backend returns "Missing required environment variables"
- Verify DATABASE_URL and GOOGLE_API_KEY are set in Vercel dashboard
- Make sure your PostgreSQL database is accessible from Vercel (may need to whitelist Vercel IPs)

### Database connection errors
- Verify your DATABASE_URL format is correct: `postgresql://user:password@host:port/database`
- Ensure your PostgreSQL database allows external connections
- Check if you need to whitelist Vercel's IP addresses in your database firewall

## 📝 Example Queries

- "Top 10 dropoff addresses for riders aged 18-24"
- "Average trip duration on weekends"
- "Most popular pickup locations"
- "Rider demographics by age group"
- "Total number of trips in the last month"

## 🤝 Contributing

This is a personal project, but feel free to fork and modify for your own use!

## 📄 License

MIT License
