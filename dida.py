import torch

# 创建一个4维张量 [1, 2, 3, 3]
tensor = torch.randn(1, 2, 3, 3)

# 使用unfold函数
# 参数说明:
# dimension: 要展开的维度
# size: 每个展开块的大小
# step: 每次移动的步长

# 在第2维(索引1)上展开,大小为2,步长为1
unfolded = tensor.unfold(1, 2, 1)

print("原始张量形状:", tensor.shape)
print("展开后的张量形状:", unfolded.shape)
print("\n原始张量:")
print(tensor)
print("\n展开后的张量:")
print(unfolded)