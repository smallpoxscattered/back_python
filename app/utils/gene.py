import numpy as np
from scipy import ndimage
import random
from numba import jit
from PIL import Image
from .utils import process_matrix
from scipy.signal import convolve2d


def expanded_to_original(y, x):
    if y % 2 == 0 and x % 2 == 0:
        return y // 2, x // 2
    else:
        return None


def get_surrounding_value_vectorized(matrix):
    padded = np.pad(matrix, ((1, 1), (1, 1)), constant_values=300)
    neighbors = np.stack([
        padded[:-2, 1:-1],  # up
        padded[2:, 1:-1],   # down
        padded[1:-1, :-2],  # left
        padded[1:-1, 2:],   # right
    ])

    mask = (neighbors != 300) & (neighbors != -1)

    first_valid = np.where(mask, neighbors, np.inf)
    first_valid = np.min(first_valid, axis=0)
    return first_valid


def check_surrounding_points_vectorized(matrix):
    padded = np.pad(matrix, ((1, 1), (1, 1)), constant_values=-1)

    up = padded[:-2, 1:-1]
    down = padded[2:, 1:-1]
    left = padded[1:-1, :-2]
    right = padded[1:-1, 2:]

    valid_points = (matrix != -1) & (matrix != 300)
    kernel = np.ones((3, 3))
    kernel[1, 1] = 0
    wall_count = np.sum(((up == -1), (down == -1), (left == -1), (right == -1)), axis=0)
    high_wall_count = (wall_count >= 3)
    matrix_mask = (matrix == -1)
    conv_result = (convolve2d(valid_points * high_wall_count, kernel, mode='same', boundary='fill', fillvalue=0) * matrix_mask) == 2
    return conv_result


def check_surrounding_values_equal_vectorized(matrix):
    padded = np.pad(matrix, ((1, 1), (1, 1)), constant_values=300)

    neighbors = np.stack([
        padded[:-2, 1:-1],  # up
        padded[2:, 1:-1],   # down
        padded[1:-1, :-2],  # left
        padded[1:-1, 2:],   # right
    ])

    mask = (neighbors != 300) & (neighbors != -1)

    valid_neighbors = mask.sum(axis=0)

    first_valid = np.where(mask, neighbors, np.inf)
    first_valid = np.min(first_valid, axis=0)
    
    equal_neighbors = ((neighbors == first_valid) & mask).sum(axis=0)

    result = (equal_neighbors == valid_neighbors) & (valid_neighbors > 0) & (matrix == -1)
    return result


def generate_numbers(image_path, n_log, resize=None):
    with Image.open(image_path) as img:
        if resize:
            img = img.resize(resize, Image.NEAREST)
        original = np.array(img)
    if len(original.shape) == 3:
        Original = original[:, :, 0]  

    h, w = Original.shape
    Original = np.array(Original, dtype=np.int32) + 1

    expanded = np.full((h * 2 - 1, w * 2 - 1), -1)
    ans_expanded = np.full((h * 3 - 2, w * 3 - 2), -1)

    expanded[::2, ::2] = Original
    expanded[1::2, 1::2] = 300
    point = [[0, 1], [1, 0], [2, 1], [1, 2], [0, 3], [3, 0], [2, 3], [3, 2]]
    for _ in range(2):
        for i, j in point:
            temp_point = np.full_like(expanded, False, dtype=bool)
            temp_point[i::4, j::4] = True
            mask = check_surrounding_points_vectorized(
                expanded
            ) & check_surrounding_values_equal_vectorized(expanded)
            wall_coords = np.column_stack(np.where(mask * temp_point))
            if wall_coords.shape[0] < 2:
                continue
            
            np.random.shuffle(wall_coords)
            wall_coords = wall_coords[::2]
            values = get_surrounding_value_vectorized(expanded)
            
            for _ in range(random.randint(n_log - 3, n_log + 3)):
                if wall_coords.shape[0] < 2:
                    break
                wall_coords_temp = wall_coords[::2]
                expanded[wall_coords_temp[:, 0], wall_coords_temp[:, 1]] = values[wall_coords_temp[:, 0], wall_coords_temp[:, 1]]
                wall_coords = wall_coords[1::2]
    result = np.zeros_like(expanded, dtype=int)
    expanded_result = np.zeros_like(expanded, dtype=int)
    start_num = -2
    for label in np.unique(Original):
        if label == -1:  
            continue
        result_temp, new_matrix, new_num = process_matrix(expanded, label, start_num)
        result[new_matrix < -1] = new_matrix[new_matrix < -1]
        start_num = new_num - 1
        expanded_result[result_temp > 0] = (result_temp[result_temp > 0] + 1) // 2
    for i in range(3):
        for j in range(3):
            ans_expanded[i::3, j::3] = result[min(i, 1)::2, min(j, 1)::2]
    return expanded_result[::2, ::2], result[::2, ::2], ans_expanded, original


def gene_map(Serial_number, size=None):
    Serial_number += 6000000
    image_path = f"data/labels_colored/{Serial_number}.png"
    result = generate_numbers(image_path, 6, size)
    return result[0].tolist(), result[1].tolist(), result[2].tolist(), result[3].tolist()


if __name__ == '__main__':
    result = gene_map(1, (32, 32))
    print("生成结果图：")
    print(result[0])
    print("生成的路径图：")
    print(result[1])
    print("中间墙")
    print(result[2])
    
    # maze = np.array([
    #     [255, 255, 255, 0, 255],
    #     [255,   0, 255, 0,   0],
    #     [255, 255, 255, 0,   0],
    #     [  0, 0,   0,  255, 255],
    #     [255, 255, 255,  0, 255]
    # ])
    # result = generate_numbers('data/maze.png', 6)

    # # 打印结果
    # print("原矩阵：")
    # print(maze)
    # print("生成结果图：")
    # print(result[0])
    # print("生成的路径图：")
    # print(result[1])
    # print("中间墙")
    # print(result[2])

