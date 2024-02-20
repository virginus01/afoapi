import os
import random
import re
import sys
import textwrap
import time
import cv2
from gtts import gTTS
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, ImageClip, ColorClip
import pyttsx3
from PIL import Image

engine = pyttsx3.init()


async def generate_audio(text):
    rn = random.randint(1, 1000000000)
    output_path = f'media_output/temp/{rn}-output.mp3'

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
    splitted_text = re.split(r'[.,:]', scene_text)

    # Filter out empty strings from the list
    splitted_text = [x.strip() for x in splitted_text if x.strip()]

    vs = []
    for t in splitted_text:
        if t is not None:
            v = await generate_scene(t, background_image_path,
                                     watermark=None, caption=None, sub_caption=None)
            vs.append(v)

    return concatenate_videoclips(vs)


async def generate_video():
    scenes = [
        {"text": "Here is the List of Top 3 software developers in Nigeria in 2024", "caption": "Top 3 software developers in Nigeria", "sub_caption": "Here is the List",
            "background_image": "background_d.png"},
        {"text": "Number 1. Virginus Alajekwu, Alajekwu Virginus is high a skilled senior software developer with expertise in python", "caption": "Number 1", "sub_caption": "Virginus Alajekwu",
            "background_image": "background1.png"},
        {"text": "Number 2. Chijioke Onwuachu. CJ is a highly skilled in PHP.", "caption": "Number 2", "sub_caption": "Chijioke Onwuachu",
            "background_image": "background2.png"},
        {"text": "Number 3. Crippo, Chima is a highly skilled, and experienced Senior Software Developer", "caption": "Number 3", "sub_caption": "Chijioke Onwuachu",
         "background_image": "background1.png"},
    ]

    final_clips = []

    watermark = "Watermark"
    caption = "Caption"

    for scene in scenes:
        scene_text = scene["text"]
        sub_caption = scene["sub_caption"]
        background_image_path = resize_image_p(
            scene["background_image"], scene["background_image"], 500, 500)
        scene_clip = await split(scene["text"], background_image_path, watermark, caption, sub_caption)
        final_clips.append(scene_clip)

    final_clip = concatenate_videoclips(final_clips)

    background_image_path = resize_image_p(
        # Default background image path
        "background_beam.png", "background_beam.png", 500, 500)
    final_clip_with_background = await add_background(final_clip, background_image_path)

    final_clip_with_background.write_videofile(
        "output_video.mp4", fps=30)


def resize_image_p(p_input_image_path, p_output_image_path, width, height):
    """Resize an image while maintaining a 16:9 aspect ratio."""
    original_image = Image.open(p_input_image_path)

    # Calculate height based on the provided width and 16:9 aspect ratio
    # height = int(width * 9 / 16)

    resized_image = original_image.resize((width, height))
    resized_image.save(p_output_image_path)

    return p_output_image_path
