# -*- coding:UTF-8 -*-
# file   : SCRUtil.py
# time   : 2023/11/29 
# author : panghu
# Desc   :

import os
import shutil
from VideoUtil import clip_audio
from AudioUtil import upload_file


def start_task(video_path, auto_path, output_path, finish_path):
    for file in os.listdir(video_path):
        if file == ".DS_Store":
            continue
        file_path = os.path.join(video_path, file)
        clip_audio(file_path, f"{auto_path}/{'.'.join(file.split('.')[:-1])}.wav")
        print(f"{file}的音频已抽离")
        dst_path = os.path.join(finish_path, file)
        shutil.move(file_path, dst_path)
    upload_file(auto_path, output_path, finish_path)
