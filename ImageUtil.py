# -*- coding:UTF-8 -*-
# file   : ImageUtil.py
# time   : 2023/11/29 
# author : panghu
# Desc   : 图片处理工具类

from rembg import remove
from PIL import Image
import io


def remove_bg(input_path, output_path):
    # 从文件读取图片
    with open(input_path, "rb") as input_file:
        input_data = input_file.read()

    # 使用rembg移除背景
    output_data = remove(input_data)

    # 将结果保存为图片
    with open(output_path, "wb") as output_file:
        output_file.write(output_data)
