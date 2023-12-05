# -*- coding:UTF-8 -*-
# file   : VideoUtil.py
# time   : 2023/11/29 
# author : panghu
# Desc   :
import math

from moviepy.editor import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def clip_audio(input_path, output_path):
    AudioFileClip(input_path).write_audiofile(output_path)


def split_video(video_path, clip_length):
    # 加载视频
    video = VideoFileClip(video_path)

    # 计算视频总长度（秒）
    video_duration = video.duration

    # 计算需要切割成多少个片段
    num_clips = math.ceil(video_duration / clip_length)

    # 切割并保存每个片段
    for i in range(num_clips):
        start_time = i * clip_length
        end_time = min((i + 1) * clip_length, video_duration)
        clip = video.subclip(start_time, end_time)
        clip.write_videofile(f"clip_{i + 1}.mp4")
