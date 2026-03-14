import uvicorn
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=port,
        reload=False,
        log_level="info",
    )