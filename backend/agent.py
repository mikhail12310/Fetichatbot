import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
import time

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "database.sqlite")

import json

CACHE_PATH = os.path.join(os.path.dirname(__file__), "response_cache.json")

def load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=4)

# Load cache once at startup
response_cache = load_cache()

class RateLimiter:
    def __init__(self, requests_per_minute=5):
        self.delay = 60.0 / requests_per_minute
        self.last_request_time = 0

    def wait(self, label=""):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            print(f"[{label}] Rate limiting: Sleeping for {sleep_time:.2f}s to respect Gemini quota...")
            time.sleep(sleep_time)
        self.last_request_time = time.time()

# Global limiter for ALL LLM calls
llm_limiter = RateLimiter(requests_per_minute=4)

class ThrottledChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    def _generate(self, *args, **kwargs):
        llm_limiter.wait("Internal Agent Step")
        return super()._generate(*args, **kwargs)
    
    async def _agenerate(self, *args, **kwargs):
        llm_limiter.wait("Internal Agent Step (Async)")
        return await super()._agenerate(*args, **kwargs)

def get_agent(model_name="gemini-2.5-flash"):
    # Only initialize if the database exists
    if not os.path.exists(DB_PATH):
        return None
        
    db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
    
    # Initialize the Throttled LLM
    llm = ThrottledChatGoogleGenerativeAI(
        model=model_name, 
        temperature=0,
        max_retries=3
    )
    
    # Create the SQL agent
    agent_executor = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="tool-calling",
        verbose=True,
        max_iterations=10
    )
    
    return agent_executor

def query_agent(question: str) -> str:
    print(f"\n--- New Question Received: '{question}' ---")
    
    # Check cache first
    if question in response_cache:
        print(f"Result found in persistent cache. Returning instantly.")
        return response_cache[question]

    # Try models in order of likelihood to work
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-pro-latest",
        "gemini-2.5-flash-lite"
    ]
    
    last_error = ""
    for model in models_to_try:
        try:
            print(f"Step 1: Attempting to connect with model '{model}'...")
            agent = get_agent(model)
            if not agent:
                print("Error: Database not found.")
                return "I don't have any data yet. Please upload some files to get started."
            
            print(f"Step 2: Sending query to '{model}' brain...")
            response = agent.invoke({"input": question})
            output = response.get("output", "I could not find an answer.")
            
            # If the model returns a list of dictionaries (like gemini-flash-latest does), extract the text
            if isinstance(output, list) and len(output) > 0 and isinstance(output[0], dict):
                print("Note: Extracting text from complex model response.")
                output = output[0].get("text", str(output))
            elif isinstance(output, dict):
                output = output.get("text", str(output))
            
            print(f"Step 3: Success! Updating persistent cache.")
            response_cache[question] = output
            save_cache(response_cache)
            return output
        except Exception as e:
            last_error = str(e)
            print(f"Model {model} failed. Reason: {last_error}")
            if "429" in last_error or "404" in last_error:
                print("Falling back to next available model...")
                continue
            break
            
    print("Step 4: All models exhausted. Final failure.")
    return f"All models failed. Last error: {last_error}"
