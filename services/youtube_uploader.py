import os
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.logger import logger

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Authenticates the user and returns a YouTube service object."""
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        logger.debug("Found existing token.json, loading credentials...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if not os.path.exists('client_secrets.json'):
            logger.error("client_secrets.json is missing for YouTube authentication.")
            raise FileNotFoundError("client_secrets.json is missing! You must create OAuth 2.0 credentials in Google Cloud Console and save them to the project root.")
            
        logger.info("Starting local OAuth flow for YouTube authentication...")
        flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
        # We run a local server to capture the authorization code
        creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            
    return build('youtube', 'v3', credentials=creds)

def upload_video_to_youtube(video_path, metadata):
    """
    Uploads a video to YouTube with the provided metadata.
    """
    logger.info(f"Starting YouTube Upload for {video_path}")
    youtube = get_authenticated_service()

    privacy_status = os.environ.get('YOUTUBE_PRIVACY_STATUS', 'private')
    logger.info(f"YouTube Upload Privacy Status: {privacy_status}")

    body = {
        'snippet': {
            'title': metadata.get('title'),
            'description': metadata.get('description'),
            'tags': metadata.get('tags'),
            'categoryId': metadata.get('categoryId')
        },
        'status': {
            'privacyStatus': privacy_status,
            'selfDeclaredMadeForKids': False
        }
    }

    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    logger.debug("Executing YouTube insert request...")
    response = insert_request.execute()
    vid_id = response.get('id')
    logger.info(f"Successfully uploaded to YouTube. Video ID: {vid_id}")
    return vid_id
