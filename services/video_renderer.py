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

ZODIAC_SIGNS = {
    "मेष": "♈", "वृषभ": "♉", "मिथुन": "♊", "कर्क": "♋",
    "सिंह": "♌", "कन्या": "♍", "तुला": "♎", "वृश्चिक": "♏",
    "धनु": "♐", "मकर": "♑", "कुंभ": "♒", "मीन": "♓"
}

def create_badge_image(text, size=(720, 1280)):
    """Creates a transparent image with the Zodiac badge at the top."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font_path = "static/assets/NotoSansDevanagari-Regular.ttf"
        font = ImageFont.truetype(font_path, 60)
    except IOError:
        return np.array(img)
        
    # Draw a gold rounded rectangle badge
    badge_w = 400
    badge_h = 100
    start_x = (size[0] - badge_w) // 2
    start_y = 150
    draw.rounded_rectangle(
        [(start_x, start_y), (start_x + badge_w, start_y + badge_h)],
        fill=(218, 165, 32, 220), radius=20
    )
    draw.text((size[0]//2, start_y + 20), text, font=font, fill=(0, 0, 0, 255), anchor="mt")
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
        
    # 2.5 ZODIAC BADGE (Only for Rasis, not intro)
    badge_clips = []
    if rasi in ZODIAC_SIGNS:
        badge_text = f"{rasi} {ZODIAC_SIGNS[rasi]}"
        badge_arr = create_badge_image(badge_text, size=(720, 1280))
        badge_clip = ImageClip(badge_arr).with_duration(duration)
        badge_clips.append(badge_clip)
        
    # 3. COMPOSITE
    video = CompositeVideoClip([bg_clip] + badge_clips + sub_clips)
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

def apply_bgm(video):
    from moviepy import AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.MultiplyVolume import MultiplyVolume
    from moviepy.audio.fx.AudioLoop import AudioLoop
    
    bgm_path = "static/assets/bgm.mp3"
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path)
        # Loop background music for the duration of the video
        bgm_looped = bgm.with_effects([AudioLoop(duration=video.duration)])
        bgm_low = bgm_looped.with_effects([MultiplyVolume(0.18)]) # 8% volume
        final_audio = CompositeAudioClip([video.audio, bgm_low])
        return video.with_audio(final_audio)
    return video

def build_short(rasi):
    """Combines Intro + Rasi into a single Short video and applies BGM."""
    from moviepy import VideoFileClip, concatenate_videoclips
    
    video_dir = "static/video"
    intro_path = os.path.join(video_dir, "intro.mp4")
    rasi_path = os.path.join(video_dir, f"{rasi}.mp4")
    final_path = os.path.join(video_dir, f"final_{rasi}.mp4")
    
    clips = []
    if os.path.exists(intro_path):
        clips.append(VideoFileClip(intro_path))
    if os.path.exists(rasi_path):
        clips.append(VideoFileClip(rasi_path))
        
    if not clips:
        return
        
    final_clip = concatenate_videoclips(clips)
    final_clip = apply_bgm(final_clip)
    
    final_clip.write_videofile(
        final_path, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None
    )
    for c in clips:
        c.close()
    final_clip.close()
    
    return f"final_{rasi}.mp4"

def combine_all_videos():
    """
    Combines Intro + all 12 individual Rasi MP4s into one master video.
    """
    logger.info("Starting Phase 5: Combining Intro and 12 videos into Master Video")
    from moviepy import VideoFileClip, concatenate_videoclips
    
    video_dir = "static/video"
    master_path = os.path.join(video_dir, "master_all_rasis.mp4")
    json_path = "data/daily_predictions.json"
    
    with open(json_path, "r", encoding="utf-8") as f:
        predictions = json.load(f)
        
    clips = []
    
    intro_path = os.path.join(video_dir, "intro.mp4")
    if os.path.exists(intro_path):
        clips.append(VideoFileClip(intro_path))
        
    # Ensure they are combined in the correct astrological order
    rasi_predictions = predictions.get("predictions", {})
    for rasi in rasi_predictions.keys():
        v_path = os.path.join(video_dir, f"{rasi}.mp4")
        if os.path.exists(v_path):
            clips.append(VideoFileClip(v_path))
            
    if not clips:
        raise FileNotFoundError("No individual videos found to combine.")
        
    final_clip = concatenate_videoclips(clips)
    final_clip = apply_bgm(final_clip)
    
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
