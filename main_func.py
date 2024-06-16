import asyncio
from image_recognition_async import *
from ultralytics import YOLO
import numpy as np
import os
import cv2
import random
import imutils

model = YOLO('best.pt')

async def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

async def four_point_transform(image, pts):
    rect = await order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    return warped

async def crop_images(img, coordinates):
    images = []
    for coords in coordinates:
        left, top, right, bottom = map(int, coords)
        cropped_img = img[top-5:bottom+5, left-5:right+5]
        images.append(cropped_img)
    return images

async def get_processed_photo(photo):
    photo = cv2.imread(photo)
    results = model(photo, conf=0.8)
    im_array = results[0].plot()
    return im_array

async def save_crop_photos(img, save_dir):
    results = model(img, conf=0.8)
    await asyncio.gather(*[result.save_crop(save_dir) for result in results])

async def save_image_with_sequence_number(image, directory, base_name):
    if not os.path.exists(directory):
        os.makedirs(directory)
    files = os.listdir(directory)
    number = len(files) + 1
    file_name = os.path.join(directory, f"{base_name}{number}.jpg")
    cv2.imwrite(file_name, image)
    print(f"Изображение сохранено как {file_name}")


from copy import deepcopy

async def draw_bounding_box(image, box, card_name):
    color = (random.randint(70, 255), random.randint(70, 255), random.randint(70, 255))
    box = [int(num) for num in box]
    start_x, start_y, end_x, end_y = box
    cv2.rectangle(image, (start_x, start_y), (end_x, end_y), color, 4)

    font = cv2.FONT_HERSHEY_SIMPLEX
    bottom_left_corner_of_text = (10, 30)
    font_scale = 1
    line_type = 0
    thickness = 5
    cv2.putText(image, card_name, (start_x, start_y - 6), font, font_scale, color, thickness)
    return image

async def find_largest_contour(image):
    # Переводим изображение в оттенки серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Применяем пороговую обработку для получения бинарного изображения
    _, thresh = cv2.threshold(gray, 127, 255, 0)
    # Инвертируем бинарное изображение
    thresh = cv2.bitwise_not(thresh)
    # Находим контуры на инвертированном бинарном изображении
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

async def get_results_photo2(img):
    ans = None
    answers = []
    if img is None:
        print("Error: The image is empty or not loaded correctly.")
        return answers, img
    copy_img = deepcopy(img)
    results = model(img, verbose=False, conf=0.7)
    boxes = results[0].boxes.xyxy.cpu().tolist()
    images = await crop_images(img, boxes)
    for i in range(len(images)):
        image = images[i]
        if image is None or image.size == 0:
            print(f"Error: The cropped image at index {i} is empty.")
            continue
        orig = image
        image = cv2.GaussianBlur(image, (5, 5), 0)
        edged = cv2.Canny(image, 120, 255)
        cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts += await find_largest_contour(image)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
        screenCnt = None
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                if screenCnt is not None:
                    warped = await four_point_transform(orig, screenCnt.reshape(4, 2))
                    try:
                        ans = await mainer(warped, 'image_database.json')
                        await draw_bounding_box(copy_img, boxes[i], ans)
                    except:
                        pass
                    if ans not in answers and ans != None:
                        answers.append(ans)
                    break
    return answers, copy_img
