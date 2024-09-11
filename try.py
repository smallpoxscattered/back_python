import os
import re

def is_code_file(filename):
    # 定义代码文件的扩展名
    code_extensions = ['.py', '.java', '.cpp', '.c', '.js', '.html', '.css', '.php', '.rb', '.go']
    return any(filename.endswith(ext) for ext in code_extensions)

def export_code(folder_path, output_file):
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if is_code_file(file):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, folder_path)
                    outfile.write(f"\n\n--- {relative_path} ---\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            outfile.write(infile.read())
                    except UnicodeDecodeError:
                        outfile.write(f"无法读取文件: {relative_path}\n")

# 使用示例
folder_path = 'app'  # 替换为您的目标文件夹路径
output_file = 'exported_code.txt'     # 输出文件名
export_code(folder_path, output_file)
print(f"所有代码已导出到 {output_file}")