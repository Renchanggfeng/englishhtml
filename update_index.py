# -*- coding: utf-8 -*-
"""
自动生成 index.html 导航卡片。
用法：新增/删除本文件夹里的 *.html 后，双击运行本脚本（或 python update_index.py）。

每个页面可在 <head> 里自描述（全部可选）：
  <meta name="page-tag"    content="分类标签">     默认：学习页面
  <meta name="page-desc"   content="一句话简介">   默认：（取页面标题）
  <meta name="page-order"  content="50">           默认：900（按文件名排序垫底）
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "index.html")

META_RE = re.compile(r'<meta\s+name="page-(tag|desc|order)"\s+content="([^"]*)"', re.I)
TITLE_RE = re.compile(r"<title>([^<]*)</title>", re.I)

CARD = """    <a class="card" href="{fname}" target="_blank">
      <span class="tag">{tag}</span>
      <h2>{title}</h2>
      <p>{desc}</p>
      <span class="go">打开 → {fname}</span>
    </a>"""


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def collect():
    pages = []
    for fname in os.listdir(HERE):
        if not fname.lower().endswith(".html") or fname.lower() == "index.html":
            continue
        path = os.path.join(HERE, fname)
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                head = f.read(4000)  # meta 都在文件头部
        except OSError as e:
            print(f"跳过无法读取的文件 {fname}: {e}")
            continue

        metas = dict(META_RE.findall(head))
        title = (TITLE_RE.search(head) or [None, fname])[1].strip() or fname
        try:
            order = int(metas.get("order") or 900)
        except ValueError:
            order = 900
        pages.append({
            "fname": fname,
            "title": esc(title),
            "tag": esc(metas.get("tag", "").strip() or "学习页面"),
            "desc": esc(metas.get("desc", "").strip() or title),
            "order": order,
        })
    pages.sort(key=lambda p: (p["order"], p["fname"]))
    return pages


def main():
    with open(INDEX, encoding="utf-8") as f:
        html = f.read()

    begin, end = "<!-- CARDS:BEGIN", "<!-- CARDS:END"
    if begin not in html or end not in html:
        sys.exit(f"index.html 里找不到 {begin} / {end} 标记，未做修改。")

    cards = "\n".join(CARD.format(**p) for p in collect())
    new_html = re.sub(
        re.escape(begin) + r".*?" + re.escape(end),
        begin + " —— 此区域由 update_index.py 自动生成，手工修改会被覆盖 -->\n"
        + cards + "\n" + end,
        html,
        count=1,
        flags=re.S,
    )

    with open(INDEX, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_html)
    print(f"完成：index.html 已更新，共 {len(collect())} 个页面。")


if __name__ == "__main__":
    main()
    try:
        input("\n按回车退出...")
    except EOFError:
        pass
