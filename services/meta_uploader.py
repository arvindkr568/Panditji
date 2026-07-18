import os
import requests
from services.logger import logger

# Requires setting these environment variables or pulling them from a .env file
# os.environ.get('META_PAGE_ACCESS_TOKEN')
# os.environ.get('META_PAGE_ID')

def upload_video_to_facebook(video_path, metadata):
    """
    Uploads a video to a Facebook Page using the Graph API.
    Facebook allows direct file uploads via multipart/form-data.
    """
    page_access_token = os.environ.get('META_PAGE_ACCESS_TOKEN')
    page_id = os.environ.get('META_PAGE_ID')
    dry_run = os.environ.get('META_DRY_RUN', 'false').lower() == 'true'
    
    logger.info(f"Starting Facebook Page upload for {video_path} (Dry-run: {dry_run})")
    
    if dry_run:
        mock_id = "mock_facebook_video_id_12345"
        logger.info(f"[DRY-RUN] Mock uploaded to Facebook. Video ID: {mock_id}")
        return mock_id
        
    if not page_access_token or not page_id:
        logger.error("Missing META_PAGE_ACCESS_TOKEN or META_PAGE_ID.")
        raise ValueError("Missing META_PAGE_ACCESS_TOKEN or META_PAGE_ID environment variables. You must generate these in the Meta Developer Portal.")
        
    url = f"https://graph.facebook.com/v19.0/{page_id}/videos"
    
    # We combine title and description for the Facebook post text
    post_text = f"{metadata.get('title')}\n\n{metadata.get('description')}"
    
    payload = {
        'description': post_text,
        'access_token': page_access_token
    }
    
    with open(video_path, 'rb') as f:
        files = {
            'source': f
        }
        
        logger.debug(f"Executing POST request to {url}")
        response = requests.post(url, data=payload, files=files)
        
    if response.status_code != 200:
        logger.error(f"Facebook API Error: {response.text}")
        raise Exception(f"Facebook API Error: {response.text}")
        
    vid_id = response.json().get('id')
    logger.info(f"Successfully uploaded to Facebook. Video ID: {vid_id}")
    return vid_id
