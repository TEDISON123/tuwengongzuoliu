#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书高清卡片无头浏览器一键导出引擎 (Headless PNG Exporter)
利用系统内置 Edge / Chrome 原生无头模式，秒级将 3:4 比例卡片 HTML 导出为 1080×1440 高清真实 PNG。
免除第三方重型依赖，开箱即用。
"""

import os
import sys
import argparse
import subprocess
import time

# 确保在 Windows 控制台中支持 UTF-8 打印
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium-browser",
]

def find_browser_executable() -> str:
    """自动检测系统内置可用的 Chromium 无头浏览器路径"""
    for path in BROWSER_CANDIDATES:
        if os.path.exists(path):
            return path
    
    # 尝试在系统 PATH 中检测
    for name in ["msedge", "chrome", "chromium", "google-chrome"]:
        try:
            res = subprocess.run(["where", name] if os.name == "nt" else ["which", name],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0 and res.stdout.strip():
                first_path = res.stdout.strip().splitlines()[0]
                if os.path.exists(first_path):
                    return first_path
        except Exception:
            pass
    return ""

def export_single_card(browser_exe: str, html_path: str, png_path: str, width: int = 540, height: int = 720, scale: int = 2) -> bool:
    """渲染并截取单张卡片"""
    abs_html = os.path.abspath(html_path)
    abs_png = os.path.abspath(png_path)
    uri = "file:///" + abs_html.replace("\\", "/")

    if os.path.exists(abs_png):
        try:
            os.remove(abs_png)
        except OSError:
            pass

    args = [
        browser_exe,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--force-device-scale-factor={scale}",
        "--virtual-time-budget=6000",
        f"--window-size={width},{height}",
        f"--screenshot={abs_png}",
        uri
    ]

    try:
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        return os.path.exists(abs_png) and os.path.getsize(abs_png) > 1024
    except Exception as e:
        print(f"❌ 截屏失败: {html_path}, 错误: {e}")
        return False

def export_deck_to_png(deck_dir: str, scale: int = 2) -> list:
    """
    将指定目录下的全部图文卡片 (page_*.html) 批量转存为高清 PNG
    scale=2 时输出分辨率为 1080×1440 (小红书官方推荐 3:4 黄金比例)
    """
    browser_exe = find_browser_executable()
    if not browser_exe:
        print("⚠️ 未找到可用的 Edge 或 Chrome 浏览器可执行文件，无法执行自动截图。")
        return []

    deck_dir = os.path.abspath(deck_dir)
    html_files = sorted([f for f in os.listdir(deck_dir) if f.startswith("page_") and f.endswith(".html")])
    if not html_files:
        print(f"⚠️ 目录 {deck_dir} 中未找到符合 page_*.html 的卡片文件。")
        return []

    print(f"📸 [Headless Exporter] 正在调用浏览器引擎导出 3:4 高清 PNG...")
    print(f"   ➔ 浏览器内核: {os.path.basename(browser_exe)}")
    print(f"   ➔ 导出分辨率: {540 * scale} × {720 * scale} px (2x Retina)")

    exported_files = []
    t0 = time.time()
    for hf in html_files:
        html_path = os.path.join(deck_dir, hf)
        png_name = os.path.splitext(hf)[0] + ".png"
        png_path = os.path.join(deck_dir, png_name)

        ok = export_single_card(browser_exe, html_path, png_path, width=540, height=720, scale=scale)
        if ok:
            size_kb = round(os.path.getsize(png_path) / 1024, 1)
            print(f"   ✅ 已生成高清图: {png_name} ({size_kb} KB)")
            exported_files.append(png_path)
        else:
            print(f"   ❌ 导出失败: {hf}")

    cost = round(time.time() - t0, 1)
    print(f"🎉 [Success] 批量截图完成！共生成 {len(exported_files)} 张高清图片，耗时 {cost} 秒。")
    return exported_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小红书 3:4 图文卡片高清导出引擎")
    parser.add_argument("--dir", type=str, required=True, help="卡片 html 所在目录")
    parser.add_argument("--scale", type=int, default=2, help="缩放倍率 (默认 2，即 1080x1440)")
    args = parser.parse_args()

    export_deck_to_png(args.dir, scale=args.scale)
