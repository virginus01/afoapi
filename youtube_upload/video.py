import asyncio
import os
import random
import re
from urllib import request
import cv2
from dotenv import load_dotenv
from gtts import gTTS
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, ImageClip, ColorClip
import pyttsx3
from PIL import Image
import requests

from .post import extract_middle_frame, get_authenticated_service, upload_video_with_thumbnail
# client = OpenAI()

engine = pyttsx3.init()



async def generate_audio(text):
    rn = random.randint(1, 1000000000)
    output_path = f'youtube_upload/media_output/temp/{rn}-output.mp3'

    # Initialize pyttsx3 engine
    engine = pyttsx3.init()

    # Set properties for the voice
    voices = engine.getProperty('voices')

    # You can change the index to select a different voice
    engine.setProperty('voice', voices[1].id)  # Change to the voice you want

    # Save text to speech
    engine.save_to_file(text, output_path)
    engine.runAndWait()

    # sys.exit()
    return AudioFileClip(output_path)


async def generate_text_clip(text, audio_duration, background_image_path, caption, sub_caption):
    # Create text clip
    audio_clip = None
    audio_clip = await generate_audio(text)
    duration = audio_clip.duration

    # Load background image and define its size
    background_clip = (ImageClip(background_image_path)
                       # Set your desired size here
                       .resize(width=500, height=500)
                       .set_duration(duration)
                       .crossfadein(0.5))

    # Get the size of the background image
    image_width, image_height = background_clip.size

    # Create the text clip
    center = TextClip(text, size=(image_width, image_height), fontsize=18, method="caption", color='yellow',
                      font='Arial', align='center').set_duration(duration)
    center_width, center_height = center.size

    # Define padding
    padding = 5

    # Calculate the width of the overlay
    overlay_width = image_width - (2 * padding)

    # Create a color clip to serve as a background for the text
    color_clip = ColorClip(
        size=(overlay_width, center_height + (2 * padding)), color=(0, 0, 0))
    color_clip = color_clip.set_opacity(.7)

    # Composite text clip over color clip
    clip_to_overlay = CompositeVideoClip(
        [color_clip.set_position('center'), center.set_position('center')])

    # Position the composite clip on the background image
    clip_to_overlay = clip_to_overlay.set_position(
        ('center', image_height/2 - clip_to_overlay.size[1]/2)).set_duration(audio_duration)

    # Add audio to the composite clip
    clip_to_overlay = clip_to_overlay.set_audio(audio_clip)

    return clip_to_overlay, duration, background_clip


async def add_background(video_clip, background_image_path):
    # Load background image and resize it to have the same height and width
    background_clip = ImageClip(
        background_image_path).resize(width=500, height=500)
    # Set the duration of the background clip to match the duration of the video clip
    # Get the size of the background image
    image_width, image_height = background_clip.size

    background_clip = background_clip.set_duration(video_clip.duration)
    # Combine the background clip and the input video clip
    return CompositeVideoClip([background_clip, video_clip], size=(image_width, image_height))


async def generate_scene(scene_text, background_image_path, watermark=None, caption=None, sub_caption=None):
    txt_clip, duration, background_clip = await generate_text_clip(scene_text, 5, background_image_path, caption, sub_caption)

    # Get the size of the background image
    image_width, image_height = background_clip.size

    # Composite text clip over background
    scene_clip = CompositeVideoClip(
        [background_clip, txt_clip], size=(image_width, image_height))

    # Set duration based on audio
    scene_clip = scene_clip.set_duration(duration)

    return scene_clip


async def split(scene_text, background_image_path, watermark=None, caption=None, sub_caption=None):
    splitted_text = re.split(r'\.(?= )|,|:', scene_text)

    # Filter out empty strings from the list
    splitted_text = [x.strip() for x in splitted_text if x.strip()]

    vs = []
    for t in splitted_text:
        if t is not None:
            v = await generate_scene(t, background_image_path,
                                     watermark=None, caption=None, sub_caption=None)
            vs.append(v)

    return concatenate_videoclips(vs)


def resize_image_p(p_input_image_path, p_output_image_path, width, height):
    """Resize an image while maintaining a 16:9 aspect ratio."""
    original_image = Image.open(p_input_image_path)

    # Calculate height based on the provided width and 16:9 aspect ratio
    height = int(width * 9 / 16)

    resized_image = original_image.resize((width, height))
    resized_image.save(p_output_image_path)

    return p_output_image_path

def upload_to_youtube(final_video_path, title, description, tags):
    print(f"uploading {final_video_path}")
    # Authenticate and create a service
    youtube = get_authenticated_service()

    # Path to the video file you want to upload
    video_file_path = final_video_path

    # Title and description of the video
    video_title = title
    video_description = description

    # Tags (optional)
    video_tags = tags

    # Extract the middle frame as an image
    middle_frame = extract_middle_frame(video_file_path)
    # Save the middle frame as an image
    cv2.imwrite('youtube_upload/thumbnail.jpg', middle_frame)

    # Upload the video with the thumbnail
    return upload_video_with_thumbnail(youtube, video_file_path, 'youtube_upload/thumbnail.jpg', video_title, video_description, video_tags)

def download_and_resize_image(url, width, height):
    response = requests.get(url)
    image_path = "youtube_upload/downloaded_image.png"  # You can change the filename and extension as needed
    with open(image_path, 'wb') as f:
        f.write(response.content)
    image = Image.open(image_path)
    height = int(width * 9 / 16)
    resized_image = image.resize((width, height))
    resized_image.save(image_path)
    return image_path


async def generate_video(scenes, title, description, tags):
    final_clips = []
    watermark = "Watermark"
    caption = "Caption"
    final_video_path = "youtube_upload/output_video.mp4"
    
    for scene in scenes:
        scene_text = scene["text"]
        sub_caption = scene["sub_caption"]
        background_image_url = scene["background_image"]
        # Download and resize the image
        background_image_path = download_and_resize_image(background_image_url, 500, 500)

        scene_text = "Yes, this is testing 2. You can visit example.com now"
        scene_clip = await split(scene_text, background_image_path, watermark, caption, sub_caption)
        final_clips.append(scene_clip)

    final_clip = concatenate_videoclips(final_clips)

    background_image_path = resize_image_p(
        # Default background image path
        "youtube_upload/background_beam.png", "youtube_upload/background_beam.png", 500, 500)
    final_clip_with_background = await add_background(final_clip, background_image_path)
    
    final_clip_with_background.write_videofile(
        final_video_path, fps=30)
    
    
    return upload_to_youtube(final_video_path, title, description, tags)
    
    
async def process_video():
    try:
        VIDEO_API_LINK = str(os.getenv('VIDEO_API_LINK'))
        api_link = VIDEO_API_LINK
        response = requests.get(api_link, timeout=10)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            data = response.json()  # Parse JSON response
            
            for video in data:
              video_id = await generate_video(video["scenes"], video["title"], video["description"], video["tags"])
              update_link = f"{api_link}?id={video["id"]}&video_id={video_id}"
              requests.get(update_link, timeout=10)
              print(f"updated via {update_link}")
        else:
            print(f"Failed to visit {api_link}. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred for {api_link}: {e}")
        
        
if __name__ == "__main__":
    #load_dotenv(".env.prod")
    #asyncio.run(process_video())
    pass