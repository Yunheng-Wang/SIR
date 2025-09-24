import os
import re
import sys
import time
import argparse
import logging
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


# --- 配置日志 ---
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- 可识别为下载文件的正则（可扩展） ---
FILE_EXTENSIONS = (
    "zip", "tar", "tar.gz", "tgz", "gz", "bz2", "7z",
    "txt", "mtx", "edges", "graph", "json", "csv", "arff",
    "mat", "bin", "xml", "zst"
)
# 构造一个用于检测的正则
EXT_RE = re.compile(r".+\.(" + r"|".join([re.escape(e).replace(r"\.", "") for e in FILE_EXTENSIONS]) + r")($|\?)", re.IGNORECASE)

# 也接受包含 '/download' 或 'Download' 的链接
DOWNLOAD_PATTERN = re.compile(r"/download|download", re.IGNORECASE)


def is_download_link(href: str):
    if not href:
        return False
    href = href.split('#', 1)[0]  # 去掉 fragment
    if EXT_RE.search(href):
        return True
    if DOWNLOAD_PATTERN.search(href):
        return True
    return False


def fetch_page_links(url: str, session: requests.Session, timeout=20):
    logger.info(f"Fetching page: {url}")
    r = session.get(url, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        # 构造绝对 URL
        abs_url = urljoin(url, href)
        if is_download_link(abs_url):
            links.add(abs_url)
    logger.info(f"Found {len(links)} candidate download links on the page.")
    return sorted(links)


def make_filename_from_url(url: str):
    parsed = urlparse(url)
    name = os.path.basename(parsed.path)
    if not name:
        # fallback to sanitized url
        name = parsed.netloc + parsed.path.replace("/", "_")
    # if name has query params that matter, append safe suffix
    if parsed.query:
        # keep short
        q = re.sub(r'[^0-9A-Za-z]+', '_', parsed.query)
        name = f"{name}__{q}"
    return name


def head_file_size(url: str, session: requests.Session, timeout=20):
    try:
        r = session.head(url, allow_redirects=True, timeout=timeout)
        if r.status_code >= 400:
            return None
        size = r.headers.get("Content-Length")
        return int(size) if size and size.isdigit() else None
    except Exception:
        return None


def download_one(url: str, out_dir: str, session: requests.Session, timeout=60, max_retries=3):
    local_name = make_filename_from_url(url)
    out_path = os.path.join(out_dir, local_name)
    tmp_path = out_path + ".part"

    # 如果已经完整存在并大小一致 -> 跳过
    remote_size = head_file_size(url, session)
    if os.path.exists(out_path) and remote_size is not None:
        if os.path.getsize(out_path) == remote_size:
            logger.info(f"Skip (exists & size match): {local_name}")
            return ("skipped", url, out_path)

    # 支持断点续传（如果服务器支持 Accept-Ranges）
    resume_byte_pos = 0
    if os.path.exists(tmp_path):
        resume_byte_pos = os.path.getsize(tmp_path)

    headers = {"User-Agent": "Mozilla/5.0 (compatible; nr-scraper/1.0)"}
    if resume_byte_pos > 0:
        headers["Range"] = f"bytes={resume_byte_pos}-"

    attempt = 0
    while attempt < max_retries:
        attempt += 1
        try:
            with session.get(url, headers=headers, stream=True, timeout=timeout, allow_redirects=True) as r:
                if r.status_code in (416,):  # Range not satisfiable (maybe file complete)
                    if os.path.exists(tmp_path):
                        os.rename(tmp_path, out_path)
                        logger.info(f"Renamed partial to final (status 416): {local_name}")
                        return ("downloaded", url, out_path)
                    else:
                        raise RuntimeError(f"Range not satisfiable and no partial file for {url}")
                if r.status_code >= 400:
                    raise RuntimeError(f"HTTP {r.status_code} for {url}")

                # 获取总大小（用于进度条）
                total = None
                cl = r.headers.get("Content-Length")
                if cl and cl.isdigit():
                    total = int(cl)
                    # 如果是 Range 请求， total 是剩余大小；合并计算显示总远端大小时需要加 resume_byte_pos
                    if "Range" in headers:
                        total += resume_byte_pos

                mode = "ab" if resume_byte_pos > 0 else "wb"
                chunk_size = 1024 * 32
                # 使用 tqdm 显示进度
                with open(tmp_path, mode) as f, tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    initial=resume_byte_pos,
                    desc=local_name,
                    leave=False,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
                # 下载完成，重命名
                os.replace(tmp_path, out_path)
                logger.info(f"Downloaded: {local_name}")
                return ("downloaded", url, out_path)
        except Exception as e:
            logger.warning(f"[Attempt {attempt}/{max_retries}] Error downloading {url}: {e}")
            time.sleep(2 ** attempt)  # 指数退避
            # 如果是续传失败，下次尝试删除部分文件并从头开始
            if os.path.exists(tmp_path) and attempt == max_retries:
                logger.info("Max retries reached; leaving partial file for inspection.")
                return ("failed", url, str(e))
    return ("failed", url, "max_retries_exceeded")


def main():
    parser = argparse.ArgumentParser(description="Scrape asn.php page for download links and download files.")
    parser.add_argument("--url", type=str, default="https://networkrepository.com/bio.php", help="Page URL to scrape")
    parser.add_argument("--output", type=str, default="./downloads", help="Output directory")
    parser.add_argument("--concurrency", type=int, default=3, help="Number of concurrent downloads")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay (s) between page fetches / requests to be polite")
    parser.add_argument("--timeout", type=int, default=60, help="Request timeout in seconds")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; nr-scraper/1.0)"})

    try:
        links = fetch_page_links(args.url, session, timeout=args.timeout)
        if not links:
            logger.warning("No download links found. Exiting.")
            return

        # 你可以在这里扩展：如果页面有多个分页或更多相关页面，需要把那些页面的 URL 也加入 links_to_scrape 并重复抓取。
        # 默认只抓取传入的页面上发现的链接。
        logger.info(f"Preparing to download {len(links)} files with concurrency={args.concurrency}")

        results = []
        # 使用线程池并发下载
        with ThreadPoolExecutor(max_workers=args.concurrency) as exe:
            future_to_url = {}
            # 先给每个下载任务做一点延迟排布，避免瞬时并发冲击
            for i, link in enumerate(links):
                # 包装一个小 closure 来稍微延迟提交（可以根据需要删除）
                future = exe.submit(download_one, link, args.output, session, args.timeout, 3)
                future_to_url[future] = link
                time.sleep(args.delay / max(1, args.concurrency))  # 防止高并发瞬间炸掉目标站点

            # 收集结果
            for fut in as_completed(future_to_url):
                try:
                    res = fut.result()
                    results.append(res)
                except Exception as e:
                    link = future_to_url.get(fut, "<unknown>")
                    logger.error(f"Download task raised for {link}: {e}")
                    results.append(("failed", link, str(e)))

        # 总结
        downloaded = [r for r in results if r[0] == "downloaded"]
        skipped = [r for r in results if r[0] == "skipped"]
        failed = [r for r in results if r[0] == "failed"]
        logger.info("==== Done ====")
        logger.info(f"Downloaded: {len(downloaded)}  Skipped: {len(skipped)}  Failed: {len(failed)}")
        if failed:
            logger.info("Failed items:")
            for f in failed:
                logger.info(f" - {f[1]}  ({f[2]})")
    finally:
        session.close()


if __name__ == "__main__":
    main()
    # python crawling.py --output ./downloads --concurrency 4 --delay 1.0 --url "https://networkrepository.com/bn.php"
