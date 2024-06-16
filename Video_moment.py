import cv2
from main_func import *
import asyncio

async def extract_frames(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    size = (frame_width, frame_height)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        result = await get_results_photo2(frame)
        _, processed_frame = result
        frames.append(processed_frame)

    cap.release()
    return frames, fps, size, fourcc

async def save_video(frames, output_path, fps, size, fourcc):
    out = cv2.VideoWriter(output_path, fourcc, fps, size)

    for frame in frames:
        out.write(frame)

    out.release()
