#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import re
import shutil
from pathlib import Path

def process_mtx(mtx_path: Path, dry_run: bool = False) -> Path:
    """
    处理单个 .mtx 文件：
      1) 跳过所有以 % 开头的注释行
      2) 跳过第一行非注释的维度行（如：80016 80016 196115）
      3) 对后续每行，仅保留前两个字段（u v）
      4) 输出为同名 .txt 文件
    返回生成的 txt 路径
    """
    out_path = mtx_path.with_suffix(".txt")
    if not dry_run:
        with mtx_path.open("r", encoding="utf-8", errors="ignore") as fin, \
             out_path.open("w", encoding="utf-8") as fout:

            saw_dim_line = False  # 是否已经跳过过维度行
            for line in fin:
                s = line.strip()
                if not s:
                    continue
                if s.startswith("%"):
                    # 注释行全部跳过
                    continue
                if not saw_dim_line:
                    # 第一行非注释行视为维度行（如 "n m nnz"），跳过一次
                    saw_dim_line = True
                    continue

                # 剩下的应是三元组：i j w（或多空白分隔）
                parts = re.split(r"\s+", s)
                if len(parts) < 2:
                    # 不合规的行，跳过
                    continue
                # 只保留前两个字段
                u, v = parts[0], parts[1]
                fout.write(f"{u} {v}\n")

    print(f"[OK] {'(dry-run) ' if dry_run else ''}Wrote: {out_path}")
    return out_path


def clean_subfolder_keep(keep_path: Path, folder: Path, dry_run: bool = False):
    """
    删除子文件夹内除了 keep_path 以外的所有文件和文件夹。
    """
    for entry in folder.iterdir():
        if entry.resolve() == keep_path.resolve():
            continue
        if dry_run:
            print(f"[DEL preview] {entry}")
            continue
        try:
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
            print(f"[DEL] {entry}")
        except Exception as e:
            print(f"[WARN] Failed to delete {entry}: {e}")


def find_first_mtx(folder: Path) -> Path | None:
    mtx_files = list(folder.glob("*.mtx"))
    if not mtx_files:
        # 有些数据可能是 .mtx.gz 或其他后缀，这里只按你的描述找 .mtx
        return None
    # 按你的场景，子文件夹中“有一个mtx文件”，取第一个
    return mtx_files[0]


def main(root_dir: Path, dry_run: bool = False):
    if not root_dir.is_dir():
        raise ValueError(f"路径不是文件夹：{root_dir}")

    # 只遍历第一层子文件夹（按你的描述）
    subfolders = [p for p in root_dir.iterdir() if p.is_dir()]
    if not subfolders:
        print(f"[INFO] 没有发现子文件夹：{root_dir}")
        return

    for sub in sorted(subfolders):
        mtx = find_first_mtx(sub)
        if not mtx:
            print(f"[SKIP] 子文件夹中未找到 .mtx：{sub}")
            continue

        print(f"[PROC] {mtx}")
        out_txt = process_mtx(mtx, dry_run=dry_run)
        # 清理：保留 out_txt，删除其余
        clean_subfolder_keep(out_txt, sub, dry_run=dry_run)

    print("[DONE] 全部处理完成。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="预处理 MatrixMarket .mtx 文件为无权边列表，并清理子文件夹。"
    )
    parser.add_argument("root", type=str, help="包含多个子文件夹的上层目录路径")
    parser.add_argument("--dry-run", action="store_true",
                        help="预演模式：只打印将执行的操作，不做任何改动")
    args = parser.parse_args()

    main(Path(args.root).expanduser().resolve(), dry_run=args.dry_run)
