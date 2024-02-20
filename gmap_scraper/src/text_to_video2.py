import cv2
import numpy as np
import os
import textwrap
import time
import cv2
from gtts import gTTS
from moviepy.editor import TextClip, concatenate_videoclips, AudioFileClip, CompositeVideoClip, ImageClip, ColorClip
import pyttsx3

engine = pyttsx3.init()


async def generate_audio(text):
    engine.save_to_file(text, 'outputcv.mp3')
    # tts = gTTS(text=text, lang='en')
    # tts.save("output.mp3")
    engine.runAndWait()
    return AudioFileClip("outputcv.mp3")


async def generate_video(text, filename, frame_width, frame_height, num_frames):

    generate_audio(text)
    audio_clip = await generate_audio(text)
    duration = audio_clip.duration
    # Calculate duration per frame
    frame_duration = duration / num_frames

    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video = cv2.VideoWriter(filename, fourcc, 30, (frame_width, frame_height))

    # Load background image
    background_image = cv2.imread("background.png")
    background_image = cv2.resize(
        background_image, (frame_width, frame_height))

    # Set font and text
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_scale = 2
    text_color = (0, 255, 255)  # Yellow color

    # Generate frames
    for i in range(num_frames):
        # Create a copy of the background image for each frame
        frame = background_image.copy()

        # Draw a filled rectangle as text background
        text_size = cv2.getTextSize(text, font, text_scale, 2)[0]
        text_x = int((frame_width - text_size[0]) / 2)
        text_y = int(frame_height / 2)
        cv2.rectangle(frame, (text_x - 10, text_y -
                      text_size[1] - 10), (text_x + text_size[0] + 10, text_y + 10), (0, 0, 0), -1)

        # Write text on frame
        cv2.putText(frame, text, (text_x, text_y), font,
                    text_scale, text_color, 2, cv2.LINE_AA)

        # Write frame to video multiple times to add duration
        for _ in range(int(frame_duration * 30)):  # Convert duration to frames at 30 fps
            video.write(frame)

    # Release video
    video.release()
