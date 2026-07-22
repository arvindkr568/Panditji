import os
import json
from dotenv import load_dotenv
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from services.logger import logger

# Load environment variables from .env file if it exists
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Authenticates the user and returns a YouTube service object."""
    creds = None
    
    # 1. Try to load token from environment variable first
    token_env = os.environ.get('YOUTUBE_TOKEN_JSON')
    if token_env:
        try:
            info = json.loads(token_env)
            creds = Credentials.from_authorized_user_info(info, SCOPES)
            logger.debug("Loaded YouTube credentials from YOUTUBE_TOKEN_JSON env var.")
        except json.JSONDecodeError:
            logger.warning("YOUTUBE_TOKEN_JSON is not valid JSON. Falling back to token.json file.")
            
    # 2. Fallback to token.json file
    if not creds and os.path.exists('token.json'):
        logger.debug("Found existing token.json, loading credentials...")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in or refresh.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            logger.info("Refreshing expired YouTube access token...")
            creds.refresh(Request())
            
            # Save the refreshed credentials
            with open('token.json', 'w') as token_file:
                token_file.write(creds.to_json())
        else:
            # 3. We need to do a new OAuth flow. Let's get the client_secrets.
            client_secrets_env = os.environ.get('YOUTUBE_CLIENT_SECRETS_JSON')
            
            if client_secrets_env:
                logger.info("Starting local OAuth flow using YOUTUBE_CLIENT_SECRETS_JSON...")
                try:
                    client_config = json.loads(client_secrets_env)
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                except json.JSONDecodeError:
                    raise ValueError("YOUTUBE_CLIENT_SECRETS_JSON is not valid JSON!")
            elif os.path.exists('client_secrets.json'):
                logger.info("Starting local OAuth flow using client_secrets.json...")
                flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            else:
                logger.error("No client secrets found for YouTube authentication.")
                raise FileNotFoundError("Could not find YOUTUBE_CLIENT_SECRETS_JSON in .env, or client_secrets.json file!")
                
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
    
    # Check if we are running in the staging environment (dry run) or production
    is_dry_run = os.environ.get('META_DRY_RUN', 'true').lower() == 'true'
    
    # If the GitHub variable is explicitly set, use it.
    # Otherwise, fallback to 'public' for Production, and 'private' for Staging.
    explicit_status = os.environ.get('YOUTUBE_PRIVACY_STATUS')
    if explicit_status:
        privacy_status = explicit_status
    else:
        privacy_status = 'private' if is_dry_run else 'public'
        
    logger.info(f"YouTube Upload Privacy Status: {privacy_status} (Dry Run: {is_dry_run})")

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
