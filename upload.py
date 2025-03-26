from uploader import Uploader
import os
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
CLIENT_KEY = os.getenv("TIKTOK_CLIENT_KEY")
CLIENT_SECRET = os.getenv("TIKTOK_CLIENT_SECRET")

uploader = Uploader(
  api_token=ACCESS_TOKEN, 
  api_refresh_token=REFRESH_TOKEN,
  client_key=CLIENT_KEY,
  client_secret=CLIENT_SECRET
)
uploader.upload("output.mp4")