import cv2
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import os

# Define the scopes needed
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    # Load credentials
    creds = None
    if os.path.exists('youtube_upload/token.json'):
        creds = Credentials.from_authorized_user_file('youtube_upload/token.json')
    # If there are no valid credentials available, prompt the user to log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'youtube_upload/client_secret.json', SCOPES, redirect_uri='http://localhost:8080/')
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('youtube_upload/token.json', 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def extract_middle_frame(video_file):
    # Open the video file
    cap = cv2.VideoCapture(video_file)
    # Get the total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Set the middle frame index
    middle_frame_index = total_frames // 2
    # Set the frame index to the middle frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame_index)
    # Read the middle frame
    ret, frame = cap.read()
    # Release the video capture object
    cap.release()
    # Return the middle frame
    return frame

def upload_video_with_thumbnail(youtube, video_file, thumbnail_file, title, description, tags=[]):
    request_body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'thumbnails': {
                'default': {'url': thumbnail_file}
            }
        },
        'status': {
            'privacyStatus': 'public'  # or 'private' or 'unlisted'
        }
    }
    media_file = MediaFileUpload(video_file)
    response = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media_file
    ).execute()

    print("Video id '{}' was successfully uploaded.".format(response['id']))
    return format(response['id'])

