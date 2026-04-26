# test_key.py — run this first to confirm key loads
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
print("✅ Key found:", key[:10] + "..." if key else "❌ NOT FOUND")