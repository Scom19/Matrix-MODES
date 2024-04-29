import json
import cv2
import numpy as np
import matplotlib.pyplot as plt

def rounding_up(matrix): # заменяет все числа на 1 и 0
    """
    массив, что содержит в себе все цвета каждого пикселя преобразует числа цветов в 1 и нолики (0 - чёрный цвет, а 1 - белый цвет)
    """
    result = np.zeros_like(matrix)
    result[matrix > 128] = 1
    return result

def split_matrix(matrix, rows, cols):
    """
    разделяет список на 25 частей (то есть разделяет весь массив, картинку на матрицу 5 на 5 клеток)
    """
    row_size, col_size = rows // 5, cols // 5
    parts = []
    for i in range(5):
        for j in range(5):
            part = matrix[i * row_size : (i + 1) * row_size, j * col_size : (j + 1) * col_size]
            parts.append(part)
    return parts

def round_to_majority(parts):
    """
    округляет каждую часть списка до 1 или нолика в зависимости от того, какbх сзначений там больше, единиц или ноликов, после чего сохраняет\n
    список в виде матрицы 5 на 5, в котором есть только нули и положительные повторяющиеся цифры
    """
    rounded_parts = []
    for part in parts:
        count_ones = np.count_nonzero(part)
        count_zeros = part.size - count_ones
        if count_ones >= count_zeros:
            rounded_part = np.ones_like(part)
        else:
            rounded_part = np.zeros_like(part)
        rounded_parts.append(rounded_part)
    return rounded_parts

def combine_parts(rounded_parts):
    """
    сохраняет всё в виде матрицы 5 на 5, где каждая клетка равна либо положительному числу, либо нулю
    """
    combined_matrix = np.zeros((5, 5))
    for i in range(5):
        for j in range(5):
            part_index = i * 5 + j
            combined_matrix[i, j] = np.sum(rounded_parts[part_index])
    return combined_matrix

def final_rounding(matrix):
     """
     преобразуем наш конечный список из 25 чисел в 0 и единицы, а именно исправляем баг, где числы не равные 0 могут быть больше 1, например 4260 и т.п.
     """
     matrix[matrix > 0] = 1
     return matrix

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

def main(picture, json_file): 
    """
    Финальная функция, что содержит в себе все предыдущие. main возвращает номер карточки и вариант её ответа, если же данная картачка не
    совпадает ни с одной из карточек из базы данных, то возвращается None. (Принимает на вход саму картинку и файл с базой данных)
    """
    cb_img = cv2.imread(picture, 0)
    cb_img_np = np.array(cb_img)
    plt.imshow(cb_img_np, cmap='gray')
    lines, columns = cb_img.shape
    the_converted_image = final_rounding(combine_parts(round_to_majority(split_matrix(rounding_up(cb_img_np), lines, columns))))
    return compare_matrices(the_converted_image, load_json_to_matrices(json_file))

