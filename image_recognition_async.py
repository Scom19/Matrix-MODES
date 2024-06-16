import json
import cv2
import numpy as np
import asyncio

async def rounding_up(matrix):
    result = np.zeros_like(matrix)
    result[matrix > 120] = 1
    return result

async def split_matrix(matrix, rows, cols):
    row_size, col_size = rows // 7, cols // 7
    parts = []
    for i in range(7):
        for j in range(7):
            part = matrix[i * row_size: (i + 1) * row_size, j * col_size: (j + 1) * col_size]
            parts.append(part)

    central_parts = []
    for i in range(1, 6):
        for j in range(1, 6):
            central_parts.append(parts[i * 7 + j])
    return central_parts

async def replace_based_on_center(parts):
    replaced_parts = []
    for part in parts:
        center_pixel = part[len(part) // 2, len(part[0]) // 2]
        replaced_part = np.full_like(part, center_pixel)
        replaced_parts.append(replaced_part)

    return replaced_parts

async def combine_parts(rounded_parts):
    combined_matrix = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            part_index = i * 5 + j
            combined_matrix[i, j] = 1 if np.sum(rounded_parts[part_index]) > 0 else 0
    return combined_matrix

async def read_from_json(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
    return data

async def load_json_to_matrices(filename):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)

    matrices = {}
    for key, value in data.items():
        matrices[key] = np.array(value)

    return matrices

async def compare_matrices(matrix1, matrices_from_json):
    for key, matrix2 in matrices_from_json.items():
        if np.array_equal(matrix1, matrix2):
            return key
    return None

async def image_optimization(image):
    enlarged_image = cv2.resize(image, (70, 70), interpolation=cv2.INTER_CUBIC)
    optimized_image_path = 'optimized_image.png'
    cv2.imwrite(optimized_image_path, enlarged_image)
    return optimized_image_path

async def mainer(cb_img_np, json_file):
    cb_img_np = cv2.cvtColor(cb_img_np, cv2.COLOR_BGR2GRAY)
    cb_img = await image_optimization(cb_img_np)
    cb_img = cv2.imread(cb_img, 0)
    cb_img_np = np.array(cb_img)
    lines, columns = cb_img_np.shape[:2]
    the_converted_image = await combine_parts(await replace_based_on_center(await split_matrix(await rounding_up(cb_img_np), lines, columns)))
    return await compare_matrices(the_converted_image, await load_json_to_matrices(json_file))
