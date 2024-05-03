import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

card = cv2.imread('C:/Users/lego/Pictures/Saved Pictures/qr5.jpg',0) # загрузка карточки
width = card.shape[0]
length = card.shape[1]

def threshold(image): # перевод в строго чёрно-белую версию
    image = cv2.threshold(image, 40, 255, cv2.THRESH_BINARY)
    image = image[1]
    for y in range(width):
        for x in range(length):
            if image[y][x] == 0:
                image[y][x] = 1
    return image


card = threshold(card)
cv2.imshow('before', card) # просмотр до
cv2.waitKey(10) # ставим 0 если хотим, чтобы сразу не исчезало

#print(width)
#print(length)


def check_which_side_is_up(image): # проверка каокой из углов сверху
    for y in range(width):
        for x in range(length):
            if card[y][x] == 1:
                if x < length//2:
                    return 'left'
                else:
                    return 'right'


def rotate(image, angle: int): # поворот на угл
    width = image.shape[0]
    length = image.shape[1]
    turn_matrix = cv2.getRotationMatrix2D((length // 2, width // 2), angle, 1.0)
    rotated_image = cv2.warpAffine(image, turn_matrix, (length,width))
    return rotated_image


def cut_rectangle(image, left_top_corner: tuple[int, int], right_bottom_corner: tuple[int, int]): # обрезка по верхнему левому и нижнему правому углам
    cropped_img = image
    x1, x2, y1, y2 = left_top_corner[0], right_bottom_corner[0], left_top_corner[1], right_bottom_corner[1]
    cropped_img = cropped_img[y1:y2, x1:x2]
    return cropped_img


def finding_dots_if_right_higher(image): # находит точки для анализа если правый угол сверху
    coordinates = []
    counter = 0
    for y in range(width):
        for x in range(length):
            if image[y][x - 1] == 255 and image[y][x] == 1 and image[y + 1][x] == 1 and image[y - 1][x] == 255:
                if counter == 0:
                    coordinates.append((x, y))
                    last_x = x
                    last_y = y
                    counter += 1
                else:
                    if x != last_x and y != last_y:
                        last_x = x
                        last_y = y
                        coordinates.append((x, y))
                        counter += 1
                if counter == 14: # counter отвечает за количество точек, а соответственно и за точность определения угла
                     return coordinates


def finding_dots_if_left_higher(image): # находит точки для анализа если левый угол сверху
    coordinates = []
    counter = 0
    for y in range(width):
        for x in range(length):
            if counter == 0:
                if image[y][x - 1] == 255 and image[y][x] == 1:
                    coordinates.append((x, y))
                    last_x = x
                    last_y = y
                    counter += 1
            else:
                if image[y][x] == 1 and image[y][x + 1] == 255 and image[y + 1][x] == 1 and image[y - 1][x] == 255:
                    if x != last_x and y != last_y:
                        coordinates.append((x, y))
                        last_x = x
                        last_y = y
                        counter += 1
            if counter == 14: # counter отвечает за количество точек, а соответственно и за точность определения угла
                    return coordinates


def finding_angle(dots): #ищет угол для поворота на основании точек
    x = 13 # отвечает за точность в пределах ранее установленного количества точек
    opposite_side = dots[x][1] - dots[1][1]
    close_side = dots[1][0] - dots[x][0]
    tan = opposite_side/close_side
    #print(tan)
    angle = math.atan(tan)
    angle = math.degrees(angle)
    #print(angle)
    angle = round(angle)
    angle = -angle
    return angle


def finding_left_top_corner(image): # нахождение левого верхнего угла
    for y in range(width):
        for x in range(length):
                if image[y][x] == 1 and image[y + 1][x - 1] == 255:
                    dot = (x, y)
                    return dot


def finding_card_sides_sizes(image): # нахождение размеров карточки

    left_top_corner = finding_left_top_corner(image)
    y1 = left_top_corner[1]
    x1 = left_top_corner[0]

    for x in range(length):
        if image[y1][x - 1] == 1:
            if image[y1][x] == 255:
                x2 = x - 1
    square_length = x2 - x1

    for y in range(width):
        if image[y - 1][x1] == 1:
            if image[y][x1] == 255:
                y2 = y - 1
    square_width = y2 - y1

    sizes = (square_length, square_width)
    return sizes


def rotate_card(card): # главная функция, которая использует все предыдущие
    if check_which_side_is_up(card) == 'left':
        dots = finding_dots_if_left_higher(card)
    else:
        dots = finding_dots_if_right_higher(card)

    angle = finding_angle(dots)
    #print(angle)
    #print(dots)
    card = rotate(card, angle)

    for y in range(width): # перевод в строгий чёрно-белый
        for x in range(length):
            if card[y][x] > 1:
                card[y][x] = 255

    cv2.imshow('after', card)
    cv2.waitKey(0)
    # показ после поворота

    sizes = finding_card_sides_sizes(card)
    left_top_corner = finding_left_top_corner(card)
    square_length = sizes[0]
    square_width = sizes[1]

    right_bottom_corner = (left_top_corner[0] + square_length, left_top_corner[1] + square_width)
    #print(left_top_corner,right_bottom_corner)
    card = cut_rectangle(card, left_top_corner, right_bottom_corner) #обрезка
    return card


card = rotate_card(card)

cv2.imshow('after', card)
cv2.waitKey(0) #показ после