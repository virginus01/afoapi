import os
import textwrap
import time
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, ImageClip, ColorClip
import pyttsx3

engine = pyttsx3.init()


async def generate_audio(text):
    engine.save_to_file(text, 'output.mp3')
    engine.runAndWait()
    return AudioFileClip("output.mp3")


async def generate_text_clip(text, audio_duration, background_clip, caption, sub_caption):
    # Load background image
    image_width, image_height = background_clip.size

    # Create text clip
    center = TextClip(text, fontsize=30, color='yellow',
                      font='Arial', align='center').set_duration(audio_duration)
    center_width, center_height = center.size

    # Define padding
    padding = 10

    # Calculate the width of the overlay
    overlay_width = image_width - (2 * padding)

    # Create a color clip to serve as a background for the text
    color_clip = ColorClip(
        size=(overlay_width, center_height + (2 * padding)), color=(0, 0, 0))
    color_clip = color_clip.set_opacity(.5)

    # Composite text clip over color clip
    clip_to_overlay = CompositeVideoClip(
        [color_clip.set_position('center'), center.set_position('center')])

    # Position the composite clip on the background image
    clip_to_overlay = clip_to_overlay.set_position(
        ('center', image_height/2 - clip_to_overlay.size[1]/2)).set_duration(audio_duration)

    return clip_to_overlay


async def add_background(video_clip, background_image_path):
    background_clip = ImageClip(
        background_image_path).set_duration(video_clip.duration)
    return CompositeVideoClip([background_clip, video_clip])


async def generate_scene(scene_text, background_image_path, watermark=None, caption=None, sub_caption=None):

    audio_clip = await generate_audio(scene_text)

    # Load background image and resize to match video size
    background_clip = (ImageClip(background_image_path)
                       .resize(width=1080, height=1200)
                       .set_duration(audio_clip.duration)
                       .crossfadein(0.5)
                       .crossfadeout(0.5))

    txt_clip = await generate_text_clip(scene_text, audio_clip.duration, background_clip, caption, sub_caption)

    # Composite text clip over background
    scene_clip = CompositeVideoClip(
        [background_clip.set_audio(audio_clip), txt_clip])

    # Set duration based on audio
    scene_clip = scene_clip.set_duration(audio_clip.duration)

    return scene_clip


async def generate_video():
    scenes = [
        {"text": "Here is the List of Top 3 software developers in Nigeria in 2024", "caption": "Top 3 software developers in Nigeria", "sub_caption": "Here is the List",
            "background_image": "background_d.png"},
        {"text": "Virginus C. Alajekwu is a highly skilled", "caption": "Number 1", "sub_caption": "Virginus Alajekwu",
            "background_image": "background1.png"},
        {"text": "CJ is a highly skilled.", "caption": "Number 2", "sub_caption": "Chijioke Onwuachu",
            "background_image": "background2.png"},
        {"text": "Kelvin is a highly skilled and experienced Senior Software Developer", "caption": "Number 3", "sub_caption": "Chijioke Onwuachu",
            "background_image": "background1.png"},
    ]

    final_clips = []

    watermark = "Watermark"
    caption = "Caption"

    for scene in scenes:
        scene_text = scene["text"]
        sub_caption = scene["sub_caption"]
        background_image_path = scene["background_image"]
        scene_clip = await generate_scene(scene["text"], background_image_path, watermark, caption, sub_caption)
        final_clips.append(scene_clip)

    final_clip = concatenate_videoclips(final_clips)

    background_image_path = "background_default.png"  # Default background image path
    final_clip_with_background = await add_background(final_clip, background_image_path)

    final_clip_with_background.write_videofile("output_video.mp4", fps=24)
