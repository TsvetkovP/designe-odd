import logging
import uvicorn
from handlers import app
from dotenv import load_dotenv

logging.basicConfig(level=logging.WARNING)

load_dotenv()

if __name__ == "__main__":
    uvicorn.run(app)
