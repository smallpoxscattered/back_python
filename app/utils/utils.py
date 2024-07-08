import numpy as np
from scipy import ndimage
import copy


def process_matrix(matrix, pixel_value, start_num):
    new_matrix = copy.deepcopy(matrix)
    result = np.zeros_like(matrix)

    binary_matrix = (matrix == pixel_value).astype(int)

    structure = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    labeled_array, num_features = ndimage.label(binary_matrix, structure=structure)

    sizes = ndimage.sum(binary_matrix, labeled_array, range(1, num_features + 1))

    conv = ndimage.convolve(binary_matrix, structure, mode="constant", cval=0)
    endpoints = (conv <= 2) & binary_matrix

    num = start_num
    for i in range(1, num_features + 1):
        component = labeled_array == i
        component_endpoints = np.logical_and(component, endpoints)
        if np.any(component_endpoints):
            result[component_endpoints] = sizes[i - 1]
            new_matrix[component] = num
        else:
            new_matrix[component] = num
            boundary_points = np.argwhere(component)
            if len(boundary_points) > 1:
                for iii in range(len(boundary_points) - 1):
                    if np.abs(boundary_points[iii] - boundary_points[iii + 2]).sum() == 2:
                        result[boundary_points[iii][0], boundary_points[iii][1]] = sizes[i - 1]
                        result[boundary_points[iii + 2][0], boundary_points[iii + 2][1]] = sizes[i - 1]
                        break
        num -= 1

    return result, new_matrix, num


if __name__ == "__main__":
    matrix = np.array(
        [
            [255, 255, 255, -1, 255, -1, 0, -1, 255],
            [255, -300, 255, -300, -1, -300, -1, -300, -1],
            [255, 255,  255,   0, 0, -1, 255, -1, 0],
            [-1, -300, -1, -300, -1, -300, -1, -300, -1],
            [0, 0, 0, 0, 0, -1, 255, -1, 255],
            [-1, -300, -1, -300, -1, -300, -1, -300, -1],
            [255, -1, 255, 255, 255, -1, 0, -1, 255],
        ]
    )

    matrix[matrix == 0] = 1
    pixel_value = 255
    for row in matrix:
        print("\t".join(map(str, row)))
    import time

    a = time.time()
    result, new_matrix, _ = process_matrix(matrix, pixel_value, -2)
    print(time.time() - a)
    print(result[::2, ::2])
    # print(matrix[::2, ::2])
    print(new_matrix[::2, ::2])
