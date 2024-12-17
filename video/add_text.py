import os
import sys
import argparse
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import VideoFileClip

LEN_Y = 100

def get_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Add text to video")
    parser.add_argument("--input", type=str, required=True, help="Path to the input video file")
    parser.add_argument("--output", type=str, required=True, help="Path to save the output video file")
    parser.add_argument("--text", type=str, required=True, help="Text to add to the video")
    parser.add_argument("--font", type=str, required=True, help="Text font")
    return parser.parse_args()

def add_text_to_video(input_video_path, output_video_path, text, font_path):
    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    LEN_X = int(width / height * LEN_Y)
    fps = cap.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    temp_video_path = "temp_video.mp4"
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width - LEN_X, height - LEN_Y))

    # Load a font
    font = ImageFont.truetype(font_path, 64)

    text_x, text_y = 50, 50
    text_color_box = (0, 0, 0)
    text_color = (255, 255, 255)

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to a PIL image
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Draw the text on the frame
        draw = ImageDraw.Draw(frame_pil)

        draw.text((text_x - 1, text_y - 1), text, font=font, fill=text_color_box)
        draw.text((text_x + 1, text_y - 1), text, font=font, fill=text_color_box)
        draw.text((text_x - 1, text_y + 1), text, font=font, fill=text_color_box)
        draw.text((text_x + 1, text_y + 1), text, font=font, fill=text_color_box)
        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Crop the bottom 50 rows
        frame_pil = frame_pil.crop((0, 0, frame_pil.width - LEN_X, frame_pil.height - LEN_Y))

        # Convert the PIL image back to a frame
        frame = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

        # Write the frame to the output video
        out.write(frame)

    # Release resources
    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Add original background music
    video_clip = VideoFileClip(temp_video_path)
    original_audio = VideoFileClip(input_video_path).audio
    video_with_audio = video_clip.with_audio(original_audio)

    video_with_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

    # Remove temporary video file
    os.remove(temp_video_path)

if __name__ == "__main__":
    args = get_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    add_text_to_video(args.input, args.output, args.text, args.font)