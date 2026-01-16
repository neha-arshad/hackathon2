#!/usr/bin/env python
"""
Startup script for the Todo App API
"""

import uvicorn
import os
from main import app

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )