import os
import os
import shutil

folder = "/home/dreams/Users/yunhengwang/DataSet_SIR/Inside/Network/Brain Networks"


# 遍历文件夹内的所有文件
for file in os.listdir(folder):
    if file.endswith(".txt"):  # 只处理txt文件
        file_path = os.path.join(folder, file)
        # 获取文件名（不带后缀）
        base_name = os.path.splitext(file)[0]
        # 新文件夹路径
        new_dir = os.path.join(folder, base_name)
        # 创建文件夹（如果不存在）
        os.makedirs(new_dir, exist_ok=True)
        # 移动文件到新文件夹
        shutil.move(file_path, os.path.join(new_dir, file))

print("所有 txt 文件已移动到对应文件夹中 ✅")