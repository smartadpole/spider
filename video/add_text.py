import os
import sys
import argparse
from moviepy import VideoFileClip, TextClip, CompositeVideoClip

def get_args():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Add text to video")
    parser.add_argument("--input", type=str, required=True, help="Path to the input video file")
    parser.add_argument("--output", type=str, required=True, help="Path to save the output video file")
    parser.add_argument("--text", type=str, required=True, help="Text to add to the video")
    return parser.parse_args()

def add_text_to_video(input_video_path, output_video_path, text):
    # Load the video
    video = VideoFileClip(input_video_path)

    # Create a text clip
    text_clip = TextClip(text, fontsize=24, color='white', font="/home/hao/.local/share/fonts/simhei.ttf")
    text_clip = text_clip.set_position(('left', 'top')).set_duration(video.duration)

    # Composite the text clip on the video
    result = CompositeVideoClip([video, text_clip])

    # Write the result to a file
    result.write_videofile(output_video_path, codec='libx264')

if __name__ == "__main__":
    args = get_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    add_text_to_video(args.input, args.output, args.text)