import json
import cv2
import numpy as np
import matplotlib.pyplot as plt

def rounding_up(matrix): # заменяет все числа на 1 и 0
    """
    массив, что содержит в себе все цвета каждого пикселя преобразует числа цветов в 1 и нолики (0 - чёрный цвет, а 1 - белый цвет)
    """
    result = np.zeros_like(matrix)
    result[matrix > 120] = 1
    return result

def split_matrix(matrix, rows, cols):
    """
    разделяет список на 49 частей (то есть разделяет весь массив, картинку на матрицу 7 на 7 клеток), после избавляется от крайних столбцов и строк => выводит матрицу 5 на 5
    """
    row_size, col_size = rows // 7, cols // 7
    parts = []
    for i in range(7):
        for j in range(7):
            part = matrix[i * row_size : (i + 1) * row_size, j * col_size : (j + 1) * col_size]
            parts.append(part)

    central_parts = []
    for i in range(1, 6):
        for j in range(1, 6):
            central_parts.append(parts[i * 7 + j])
    
    return central_parts

def replace_based_on_center(parts):
    """
    округляет каждую часть списка до 1 или 0 на основе цвета центрального пикселя
    """
    replaced_parts = []
    for part in parts:
        center_pixel = part[len(part) // 2, len(part[0]) // 2]
        replaced_part = np.full_like(part, center_pixel)
        replaced_parts.append(replaced_part)
    return replaced_parts

def combine_parts(rounded_parts):
    """
    сохраняет всё в виде матрицы 5 на 5, где каждая клетка равна либо положительному числу, либо нулю
    """
    combined_matrix = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            part_index = i * 5 + j
            combined_matrix[i, j] = 1 if np.sum(rounded_parts[part_index]) > 0 else 0
    return combined_matrix

def read_from_json(filename):
    # Открытие файла для чтения
    with open(filename, 'r') as json_file:
        # Загрузка данных из файла
        data = json.load(json_file)
    return data

def load_json_to_matrices(filename):
    """
    загрузка базы данных в список matrices и преобразование его в словарь numpy
    """
    with open(filename, 'r') as json_file:
        data = json.load(json_file)

    matrices = {}
    for key, value in data.items():
        matrices[key] = np.array(value)
    
    return matrices

def compare_matrices(matrix1, matrices_from_json):
    """
    сравнение нашей матрицы с матрицами из базы данных
    """
    for key, matrix2 in matrices_from_json.items():
        if np.array_equal(matrix1, matrix2):
            return key
    return None

def image_optimization(image_path):
    """
    Изменяет качество картинки до изображение в 70 на 70 пикселей
    """
    image = cv2.imread(image_path)
    enlarged_image = cv2.resize(image, (70, 70), interpolation=cv2.INTER_CUBIC)
    optimized_image_path = 'optimized_image.png'
    cv2.imwrite(optimized_image_path, enlarged_image)
    return optimized_image_path

def main(picture, json_file): 
    """
    Финальная функция, что содержит в себе все предыдущие. main возвращает номер карточки и вариант её ответа, если же данная картачка не
    совпадает ни с одной из карточек из базы данных, то возвращается None. (Принимает на вход саму картинку и файл с базой данных)
    """
    cb_img = image_optimization(picture)
    cb_img = cv2.imread(cb_img, 0)
    cb_img_np = np.array(cb_img)
    plt.imshow(cb_img_np, cmap='gray')
    lines, columns = cb_img.shape
    the_converted_image = combine_parts(replace_based_on_center(split_matrix(rounding_up(cb_img_np), lines, columns)))
    return compare_matrices(the_converted_image, load_json_to_matrices(json_file))
