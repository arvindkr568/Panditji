import os
import json
import textwrap
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, VideoClip
from services.logger import logger

def parse_vtt(vtt_path):
    """Parses edge-tts VTT file into a list of subtitle dictionaries."""
    subs = []
    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    current_sub = {}
    for line in lines:
        if '-->' in line:
            start_str, end_str = line.split('-->')
            
            def parse_time(t_str):
                t_str = t_str.strip().replace(',', '.')
                h, m, s = t_str.split(':')
                return int(h)*3600 + int(m)*60 + float(s)
                
            current_sub['start'] = parse_time(start_str)
            current_sub['end'] = parse_time(end_str)
        elif line.strip() and not line.strip().isdigit() and 'WEBVTT' not in line:
            current_sub['text'] = line.strip()
            subs.append(current_sub)
            current_sub = {}
    return subs

def create_subtitle_image(text, size=(720, 1280)):
    """Creates a transparent subtitle image using Pillow."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        font_path = "static/assets/NotoSansDevanagari-Regular.ttf"
        font = ImageFont.truetype(font_path, 42)
    except IOError:
        raise FileNotFoundError("Hindi Font not found in static/assets/")
        
    lines = textwrap.wrap(text, width=28)
    line_height = 55
    total_text_height = len(lines) * line_height
    start_y = size[1] - total_text_height - 100 # 100px from bottom
    
    # Draw translucent background for subtitle readability
    draw.rounded_rectangle(
        [(20, start_y - 20), (size[0] - 20, start_y + total_text_height + 20)],
        fill=(0, 0, 0, 180), radius=10
    )
    
    current_y = start_y
    for line in lines:
        draw.text((size[0]//2, current_y), line, font=font, fill=(255, 255, 255, 255), anchor="mt")
        current_y += line_height
        
    return np.array(img)

def render_single_video(rasi):
    """
    Renders a single Phase 5 Video for a specific Rasi.
    """
    logger.info(f"Starting Phase 4: Rendering video for Rasi: {rasi}")
    audio_dir = "static/audio"
    video_dir = "static/video"
    bg_path = "static/assets/fav_panditji.png"
    
    os.makedirs(video_dir, exist_ok=True)
    
    if not os.path.exists(bg_path):
        raise FileNotFoundError("Background image missing. Ensure fav_panditji.png is in static/assets/")
        
    # PREPARE BACKGROUND FOR FAST ANIMATION
    bg_large = Image.open(bg_path).convert('RGB').resize((800, 1422))
    bg_large_arr = np.array(bg_large)
    
    audio_path = os.path.join(audio_dir, f"{rasi}.mp3")
    vtt_path = os.path.join(audio_dir, f"{rasi}.vtt")
    video_path = os.path.join(video_dir, f"{rasi}.mp4")
    
    if not os.path.exists(audio_path) or not os.path.exists(vtt_path):
        raise FileNotFoundError(f"Audio or VTT missing for {rasi}. Run Phase 3 first.")
        
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    
    # 1. ANIMATE BACKGROUND (Breathing / Pan Effect)
    def get_bg_frame(t):
        phase = (1 - math.cos(t * 2 * math.pi / 8.0)) / 2 
        x_offset = int(phase * 80)
        y_offset = int(phase * 142)
        return bg_large_arr[y_offset:y_offset+1280, x_offset:x_offset+720]
        
    bg_clip = VideoClip(frame_function=get_bg_frame, duration=duration)
    
    # 2. RENDER SUBTITLES FROM VTT
    subs = parse_vtt(vtt_path)
    sub_clips = []
    for sub in subs:
        sub_arr = create_subtitle_image(sub['text'], size=(720, 1280))
        clip = ImageClip(sub_arr).with_start(sub['start']).with_end(min(sub['end'], duration))
        sub_clips.append(clip)
        
    # 3. COMPOSITE
    video = CompositeVideoClip([bg_clip] + sub_clips)
    video = video.with_audio(audio_clip)
    
    # 4. EXPORT
    video.write_videofile(
        video_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast",
        logger=None # Suppressing MoviePy's progress bar
    )
    logger.debug(f"Successfully rendered video to {video_path}")
    
    audio_clip.close()
    video.close()
    
    return {
        "rasi": rasi,
        "url": f"/video/{rasi}.mp4"
    }

def combine_all_videos():
    """
    Combines all 12 individual Rasi MP4s into one master video.
    """
    logger.info("Starting Phase 5: Combining all 12 videos into Master Video")
    from moviepy import VideoFileClip, concatenate_videoclips
    
    video_dir = "static/video"
    master_path = os.path.join(video_dir, "master_all_rasis.mp4")
    json_path = "data/daily_predictions.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
        predictions = json.load(f)
        
    clips = []
    # Ensure they are combined in the correct astrological order
    for rasi in predictions.keys():
        v_path = os.path.join(video_dir, f"{rasi}.mp4")
        if os.path.exists(v_path):
            clips.append(VideoFileClip(v_path))
            
    if not clips:
        raise FileNotFoundError("No individual videos found to combine.")
        
    final_clip = concatenate_videoclips(clips)
    
    final_clip.write_videofile(
        master_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac", 
        preset="ultrafast",
        logger=None
    )
    
    for clip in clips:
        clip.close()
    final_clip.close()
    
    logger.info(f"Phase 5 Complete: Master video saved to {master_path}")
    return {
        "status": "success",
        "url": "/video/master_all_rasis.mp4"
    }
