#!/usr/bin/python3 python
# encoding: utf-8
'''
@author: 孙昊
@contact: smartadpole@163.com
@file: youtube.py
@time: 2024/7/12 下午4:07
@desc: 
'''
import sys, os
from googleapiclient.discovery import build

CURRENT_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(CURRENT_DIR, '../../'))

import argparse


def GetArgs():
    parser = argparse.ArgumentParser(description="",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--key", type=str, help="google api key")
    parser.add_argument("--query", type=str, help="")
    parser.add_argument("--output", type=str, default="videos", help="")

    args = parser.parse_args()
    return args


def search_videos(api_key, query, max_results):
    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        q=query,
        type="video"
    )
    response = request.execute()

    videos = []
    for item in response['items']:
        video_data = {
            'title': item['snippet']['title'],
            'description': item['snippet']['description'],
            'published_at': item['snippet']['publishedAt'],
            'video_id': item['id']['videoId']
        }
        videos.append(video_data)
    return videos

def main():
    args = GetArgs()
    query = args.query
    output = os.path.join(args.output, args.query)
    output = output.replace(" ", "_")
    os.makedirs(output, exist_ok=True)

    max_results = 100
    videos = search_videos(args.key, query, max_results)
    for video in videos:
        video_id = video['video_id']
        video_url = f'https://www.youtube.com/watch?v={video_id}'

        print(f"Title: {video['title']}")
        print(f"Description: {video['description']}")
        print(f"Published At: {video['published_at']}")
        print(f"Video ID: {video['video_id']}")
        print(f"Video url: {video_url}")
        print("\n")

        # Use youtube-dl or similar tool to download the video
        file = os.path.join(output, f"{video_id}.mp4")
        os.system(f'yt-dlp {video_url} -o {file}')



if __name__ == '__main__':
    main()