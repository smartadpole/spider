import os
import sys
import argparse
import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np

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
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width - LEN_X, height - LEN_Y))

    # Load a font
    font = ImageFont.truetype(font_path, 64)

    text_x, text_y = 50, 50
    BG_RATE = 0.5

    # Process each frame
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame to a PIL image
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Create a transparent overlay
        overlay = Image.new('RGBA', frame_pil.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)

        background_color = frame_pil.getpixel((text_x, text_y))
        brightness = sum(background_color[:3]) / 3
        text_color = (0, 0, 0) if brightness > 128 else (255, 255, 255)

        # Draw a background ellipse with the opposite color
        text_bbox = draw.textbbox((text_x, text_y), text, font=font)
        text_size = (text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1])
        expand = 30
        ellipse_bbox = [text_x - expand, text_y - expand, text_x + text_size[0] + expand, text_y + text_size[1] + expand]
        draw.ellipse(ellipse_bbox, fill=background_color + (128,))  # 50% opacity

        draw.text((text_x, text_y), text, font=font, fill=text_color)

        # Blend the overlay with the original frame
        frame_pil = Image.alpha_composite(frame_pil.convert('RGBA'), overlay).convert('RGB')

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

if __name__ == "__main__":
    args = get_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    add_text_to_video(args.input, args.output, args.text, args.font)