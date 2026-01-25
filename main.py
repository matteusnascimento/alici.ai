"""
main.py - Wrapper FastAPI
Exporta a app FastAPI para compatibilidade com gunicorn
"""
from main_auth import app

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
