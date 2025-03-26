import os
import time
import requests
import urllib.parse

class Uploader:


  def __init__(self, api_token, api_refresh_token, client_key, client_secret):
    self.api_token = api_token
    self.api_refresh_token = api_refresh_token
    self.client_key = client_key
    self.client_secret = client_secret

    self.video_size = None


  def refresh_token(self):
    url = "https://open.tiktokapis.com/v2/oauth/token/"

    # set authorization headers
    headers = {
      "Content-Type": "application/x-www-form-urlencoded"
    }

    # define the request payload
    payload = {
      "refresh_token": self.api_refresh_token,
      "client_key": self.client_key,
      "client_secret": self.client_secret,
      "grant_type": "refresh_token"
    }

    encoded_payload = urllib.parse.urlencode(payload)

    # make the request
    response = requests.post(url, data=encoded_payload, headers=headers)

    # print response
    print(response.status_code, response.json())

    # set refresh and access tokens
    self.api_token = response.json()["access_token"]
    self.api_refresh_token = response.json()["refresh_token"]


  def calculate_video_size(self, video_path):
    try:
      file_size = os.path.getsize(video_path)
      return file_size
    except FileNotFoundError:
      return None


  def calculate_chunk_size(self):
    MB = 1024 * 1024
    MAX_CHUNK_SIZE = 50 * MB
    return MAX_CHUNK_SIZE

  
  def upload(self, video_path, retries=3):
    # out of retries
    if retries == 0:
      print("Failed to upload video after 3 retries.")
      return
    
    url = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"

    # set authorization headers
    headers = {
      "Authorization": f"Bearer {self.api_token}",
      "Content-Type": "application/json"
    }

    # define the request payload
    video_size = self.calculate_video_size(video_path)
    self.video_size = video_size

    # TODO: figure out chunk size, currently only doing 1 chunk
    # chunk_size = self.calculate_chunk_size()
    payload = {
      "source_info": {
        "source": "FILE_UPLOAD",
        "video_size": video_size,
        "chunk_size": video_size,
        "total_chunk_count": 1
      }
    }

    print("Video Info:", payload)

    # make the request
    response = requests.post(url, json=payload, headers=headers)

    # invalid token, retry with refresh token
    if response.status_code == 401:
      print("Access token is invalid. Trying to refresh token.")
      self.refresh_token()
      return self.upload_video(video_path, retries - 1)

    # print response
    print(response.status_code, response.json())
  
    # set upload URL and publish ID
    upload_url = response.json()["data"]["upload_url"]
    publish_id = response.json()["data"]["publish_id"]

    # upload the video
    try:
      self.upload_video(upload_url, video_path)
      self.monitor_upload(publish_id)
    except Exception as e:
      print("Failed to upload video.", e)
      return
  
  def upload_video(self, upload_url, video_path):
    with open(video_path, "rb") as video_file:
      video_data = video_file.read()

    headers = {
      "Content-Type": "video/mp4",
      "Content-Range": f"bytes 0-{self.video_size - 1}/{self.video_size}",
      "Content-Length": f"{self.video_size}"
    }

    response = requests.put(upload_url, data=video_data, headers=headers)
    print("Response:", response.status_code)

    if response.status_code == 201:
      print("Uploaded successfully!")
    else:
      print("Failed to upload video.", response.status_code, response.json())
      return
  

  def monitor_upload(self, publish_id):
    url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"

    headers = {
      "Authorization": f"Bearer {self.api_token}",
      "Content-Type": "application/json"
    }

    payload = {
      "publish_id": publish_id
    }

    status = "PROCESSING_UPLOAD"
    while status == "PROCESSING_UPLOAD":
      response = requests.post(url, json=payload, headers=headers)
      
      if response.status_code == 200 and "data" in response.json() and "status" in response.json()["data"]:
        status = response.json()["data"]["status"]
        print("Upload status:", status)
        print(response.json())
      else:
        print("Failed to fetch status.", response.status_code, response.json())
        break  # exit loop if request fails

      if status == "PROCESSING_UPLOAD":
        time.sleep(10)  # wait for 10 seconds before checking again

    print("Final status:", status)
