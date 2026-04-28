const { ChatGoogleGenerativeAI } = require('@langchain/google-genai');
const { SQLDatabase } = require('@langchain/community/utilities');
const { createSqlAgent } = require('@langchain/community/agent_toolkits/sql/base');

const SYSTEM_PROMPT = `
You are a SQL expert for a rideshare dataset (Fetii Austin).
Translate the user's question into syntactically-correct SQL for Postgres.
- Use only existing tables/columns (trips, riders, ride_demo).
- Prefer explicit JOINs and snake_case.
- If timestamps are stored as text, filter sensibly (e.g., LIKE, CAST).
- After executing SQL, summarize results briefly and clearly.
Return BOTH the SQL you ran and the final answer.
`;

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Get environment variables
    const databaseUrl = process.env.DATABASE_URL;
    const geminiKey = process.env.GOOGLE_API_KEY;

    if (!databaseUrl || !geminiKey) {
      return res.status(500).json({ 
        error: 'Missing required environment variables',
        details: 'Ensure DATABASE_URL and GOOGLE_API_KEY are set'
      });
    }

    // Create database connection
    const db = new SQLDatabase.fromUri(databaseUrl, {
      includeTables: ['trips', 'riders', 'ride_demo']
    });

    // Initialize LLM
    const llm = new ChatGoogleGenerativeAI({
      model: 'gemini-2.5-flash-lite-preview-06-17',
      temperature: 0,
      maxOutputTokens: 512,
      googleApiKey: geminiKey,
    });

    // Create SQL agent
    const agent = createSqlAgent({
      llm,
      db,
      verbose: true,
      systemMessage: SYSTEM_PROMPT
    });

    // Execute query
    const result = await agent.invoke({ input: message }, { stream: false });
    const answer = result.output || result;

    res.status(200).json({ 
      success: true,
      answer 
    });

  } catch (error) {
    console.error('Chat API Error:', error);
    res.status(500).json({ 
      error: 'Failed to process query',
      details: error.message 
    });
  }
};
