import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'src', 'ai_agent'))

# Change to the ai_agent directory to run the server
os.chdir('src/ai_agent')

from server import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)