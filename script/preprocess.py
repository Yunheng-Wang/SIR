import os
import shutil

def process_edges_file(edges_path, output_path):
    # 将 .edges 的前两列复制为 .txt（每行两个点）
    with open(edges_path, "r", encoding="utf-8", errors="ignore") as f_in, \
         open(output_path, "w", encoding="utf-8") as f_out:
        for line in f_in:
            parts = line.strip().split()
            if len(parts) >= 2:
                f_out.write(f"{parts[0]} {parts[1]}\n")

def find_all_edges_under(dir_path):
    """递归查找 dir_path 下所有以 .edges 结尾的文件，返回绝对路径列表。"""
    results = []
    for root, _, files in os.walk(dir_path):
        for fn in files:
            if fn.endswith(".edges"):
                results.append(os.path.join(root, fn))
    return results

def unique_output_path(base_dir, base_name, taken_paths):
    """
    在 base_dir 下生成不重名的输出路径：
    base_name 通常是 xxx.txt；若重名，则追加 _1, _2, ...
    taken_paths 是已占用路径的集合，避免冲突。
    """
    name, ext = os.path.splitext(base_name)
    candidate = os.path.join(base_dir, base_name)
    idx = 1
    while candidate in taken_paths or os.path.exists(candidate):
        candidate = os.path.join(base_dir, f"{name}_{idx}{ext}")
        idx += 1
    return candidate

def process_directory(a_dir):
    """
    对于目录 a_dir：
    - 递归查找其下所有 .edges（可能藏在子目录 b 中）
    - 把生成的 .txt 统一写在 a_dir 下
    - 处理完成后，删掉 a_dir 下除这些 .txt 之外的所有文件/文件夹（包括 b）
    """
    edges_files = find_all_edges_under(a_dir)
    if not edges_files:
        print(f"[跳过] {a_dir} 下未找到 .edges 文件。")
        return

    generated_txts = set()

    for edges_path in edges_files:
        # 以原 .edges 文件名作为基名；输出到 a_dir
        base = os.path.basename(edges_path).replace(".edges", ".txt")
        out_path = unique_output_path(a_dir, base, generated_txts)
        process_edges_file(edges_path, out_path)
        generated_txts.add(out_path)
        print(f"处理完成: {edges_path} -> {out_path}")

    # 清理：删除 a_dir 下除生成的 txt 外的所有内容（包括子目录 b）
    for entry in os.listdir(a_dir):
        abs_path = os.path.join(a_dir, entry)
        if abs_path in generated_txts:
            continue
        try:
            if os.path.isfile(abs_path) or os.path.islink(abs_path):
                os.remove(abs_path)
                print(f"已删除文件: {abs_path}")
            elif os.path.isdir(abs_path):
                shutil.rmtree(abs_path)
                print(f"已删除文件夹: {abs_path}")
        except Exception as e:
            print(f"删除失败 {abs_path}: {e}")

def process_all(root_folder):
    """
    遍历 root_folder 下的**一级目录**（以及 root_folder 本身）作为 a 目录处理。
    这样每个 a 目录都会把其子树中的 .edges 汇总生成到 a，并清理 a 中非 .txt 内容。
    """
    # 先处理 root_folder 自身作为 a
    process_directory(root_folder)

    # 再处理 root_folder 下的每个一级子目录作为 a
    for name in os.listdir(root_folder):
        a_dir = os.path.join(root_folder, name)
        if os.path.isdir(a_dir):
            process_directory(a_dir)

if __name__ == "__main__":
    folder = "/home/dreams/Users/yunhengwang/DataSet_SIR/Brain_Networks"
    process_all(folder)
