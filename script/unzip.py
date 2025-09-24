import os
import zipfile
import tarfile

def extract_file(file_path, dest_dir):
    """
    解压单个文件到目标目录，成功后删除原压缩包
    """
    try:
        if file_path.endswith(".zip"):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(dest_dir)
        elif file_path.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2")):
            with tarfile.open(file_path, 'r:*') as tar_ref:
                tar_ref.extractall(dest_dir)
        else:
            print(f"跳过不支持的文件: {file_path}")
            return
        print(f"解压完成: {file_path} -> {dest_dir}")
        
        # 解压成功后删除原文件
        os.remove(file_path)
        print(f"已删除压缩包: {file_path}")

    except Exception as e:
        print(f"解压失败 {file_path}: {e}")


def extract_all_in_folder(folder_path):
    """
    遍历文件夹，解压所有压缩文件
    """
    for root, _, files in os.walk(folder_path):
        for f in files:
            file_path = os.path.join(root, f)
            # 解压后存放到同名文件夹
            dest_dir = os.path.splitext(file_path)[0]
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            extract_file(file_path, dest_dir)


if __name__ == "__main__":
    folder = "/home/dreams/Users/yunhengwang/DataSet_SIR/Brain_Networks"  # 修改为你的目标文件夹路径
    extract_all_in_folder(folder)

