import numpy as np
import random
from collections import deque


def generate_adaptive_number_wall(rows, cols):
    grid = np.ones((rows, cols), dtype=int)  # 1 表示岛屿，0 表示墙

    def is_valid_coord(x, y):
        return 0 <= x < rows and 0 <= y < cols

    def get_neighbors(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return [
            (x + dx, y + dy) for dx, dy in directions if is_valid_coord(x + dx, y + dy)
        ]

    def is_invalid_island(x, y):
        neighbors = get_neighbors(x, y)
        wall_count = sum(1 for nx, ny in neighbors if grid[nx, ny] == 0)
        is_on_edge = x == 0 or x == rows - 1 or y == 0 or y == cols - 1
        if is_on_edge:
            return random.random() < 0.7
        else:
            return wall_count != 2

    def is_valid_wall(x, y):
        neighbors = get_neighbors(x, y)
        wall_count = sum(1 for nx, ny in neighbors if grid[nx, ny] == 0)
        return wall_count <= 1

    def should_convert_to_wall(x, y):
        if grid[x, y] == 0:
            return False
        return is_invalid_island(x, y) and is_valid_wall(x, y)

    def plan_route(x, y):
        if not is_valid_coord(x, y) or grid[x, y] == 0:
            return

        if should_convert_to_wall(x, y):
            grid[x, y] = 0  # 将岛屿变成墙

            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                plan_route(nx, ny)

    # 随机选择一个边界点作为起点
    edge_points = (
        [(0, j) for j in range(cols)]
        + [(rows - 1, j) for j in range(cols)]
        + [(i, 0) for i in range(1, rows - 1)]
        + [(i, cols - 1) for i in range(1, rows - 1)]
    )
    start_point = random.choice(edge_points)
    grid[start_point] = 0  # 将起点设为墙

    x, y = start_point
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    random.shuffle(directions)
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        plan_route(nx, ny)
    
    return grid


def gene_map(size=(20, 20)):
    def is_valid_coord(x, y):
        return 0 <= x < size[0] and 0 <= y < size[1]
    def get_neighbors(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        return [
            (x + dx, y + dy) for dx, dy in directions if is_valid_coord(x + dx, y + dy)
        ]
    def has_point(x, y):
        neighbors = get_neighbors(x, y)
        return np.sum([grid[nx, ny] != 0 for nx, ny in neighbors]) == 1

    def visualize_connected_ones(matrix):
        
        m, n = len(matrix), len(matrix[0])
        visited = [[False for _ in range(n)] for _ in range(m)]
        result = [[0 for _ in range(n)] for _ in range(m)]
        
        def dfs(i, j):
            if i < 0 or i >= m or j < 0 or j >= n or matrix[i][j] == 0 or visited[i][j]:
                return 0
            
            visited[i][j] = True
            count = 1
            
            # 检查4个方向：上、下、左、右
            directions = [(-1,0), (1,0), (0,-1), (0,1)]
            for di, dj in directions:
                count += dfs(i + di, j + dj)
            
            return count
        
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == 1 and not visited[i][j]:
                    size = dfs(i, j)
                    # 填充连通域的大小
                    for x in range(m):
                        for y in range(n):
                            if visited[x][y] and result[x][y] == 0:
                                result[x][y] = size
        
        return result
    def process_matrix(matrix):
        rows, cols = len(matrix), len(matrix[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]

        def dfs(i, j, num):
            if (i < 0 or i >= rows or j < 0 or j >= cols or
                visited[i][j] or matrix[i][j] != num):
                return
            
            visited[i][j] = True
            if (i, j) != start:
                matrix[i][j] = 0
            
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(i + di, j + dj, num)

        for i in range(rows):
            for j in range(cols):
                if not visited[i][j] and matrix[i][j] != 0 and has_point(i, j):
                    start = (i, j)
                    dfs(i, j, matrix[i][j])
        
        return matrix
    def process_mat(matrix):
        rows, cols = len(matrix), len(matrix[0])
        visited = [[False for _ in range(cols)] for _ in range(rows)]

        def dfs(i, j, num):
            if (i < 0 or i >= rows or j < 0 or j >= cols or
                visited[i][j] or matrix[i][j] != num):
                return
            
            visited[i][j] = True
            if (i, j) != start:
                matrix[i][j] = 0
            
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                dfs(i + di, j + dj, num)

        for i in range(rows):
            for j in range(cols):
                if not visited[i][j] and matrix[i][j] != 0:
                    start = (i, j)
                    dfs(i, j, matrix[i][j])
        
        return matrix
    grid = generate_adaptive_number_wall(*size)
    while(np.sum(grid != 0) < 3 or np.max(visualize_connected_ones(grid)) > size[0]):
        grid = generate_adaptive_number_wall(*size)
    return grid, process_mat(process_matrix(visualize_connected_ones(grid)))


if __name__ == "__main__":
    result = gene_map((20, 20))
    print("生成结果图：")
    print(result[0])
    print("生成的路径图：")
    print(result[1])
