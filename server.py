#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图文工坊 · 本地服务与桌面直存后端
- 提供静态 Web 服务 (端口 8080)
- 提供 /api/save_to_desktop 接口，秒级将生成的 1080x1440 PNG 写入 ~/Desktop/小红书图文/
"""

import http.server
import socketserver
import json
import base64
import os
import sys
import shutil

PORT = 8080
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP_DIR = os.path.expanduser("~/Desktop/小红书图文")
EXAMPLES_DIR = os.path.join(WEB_DIR, "examples")

os.makedirs(DESKTOP_DIR, exist_ok=True)

# 动态引入 pipeline 模块
PIPELINE_DIR = os.path.join(WEB_DIR, "pipeline")
if PIPELINE_DIR not in sys.path:
    sys.path.insert(0, PIPELINE_DIR)

try:
    from auto_news_pipeline import generate_deck_api
except ImportError:
    generate_deck_api = None


class CreatorStudioHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            status_data = {
                'status': 'ok',
                'desktop_dir': DESKTOP_DIR,
                'exists': os.path.exists(DESKTOP_DIR),
                'pipeline_available': generate_deck_api is not None
            }
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/list_decks':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()

            decks = []
            if os.path.exists(EXAMPLES_DIR):
                for folder in sorted(os.listdir(EXAMPLES_DIR)):
                    fpath = os.path.join(EXAMPLES_DIR, folder)
                    if os.path.isdir(fpath) and not folder.startswith('.'):
                        deck_info = {
                            "id": folder,
                            "folder": folder,
                            "title": folder,
                            "has_png": os.path.exists(os.path.join(fpath, "page_1.png")),
                            "has_viewer": os.path.exists(os.path.join(fpath, "all_pages_viewer.html")),
                            "viewer_url": f"examples/{folder}/all_pages_viewer.html"
                        }
                        # 读取 campaign_config.json 或 deck_payload.json
                        cfg_path = os.path.join(fpath, "campaign_config.json")
                        payload_path = os.path.join(fpath, "deck_payload.json")
                        if os.path.exists(cfg_path):
                            try:
                                with open(cfg_path, 'r', encoding='utf-8') as cf:
                                    cfg_data = json.load(cf)
                                    deck_info["title"] = cfg_data.get("campaign_name", folder)
                                    deck_info["campaign_config"] = cfg_data
                            except Exception:
                                pass
                        elif os.path.exists(payload_path):
                            try:
                                with open(payload_path, 'r', encoding='utf-8') as pf:
                                    pdata = json.load(pf)
                                    deck_info["title"] = pdata.get("meta", {}).get("topic", folder)
                                    deck_info["deck_payload"] = pdata
                            except Exception:
                                pass

                        # 读取 audit_report.json
                        audit_path = os.path.join(fpath, "audit_report.json")
                        if os.path.exists(audit_path):
                            try:
                                with open(audit_path, 'r', encoding='utf-8') as af:
                                    deck_info["audit_report"] = json.load(af)
                            except Exception:
                                pass

                        # 读取文案包
                        pack_path = os.path.join(fpath, "publish_pack.txt")
                        if os.path.exists(pack_path):
                            try:
                                with open(pack_path, 'r', encoding='utf-8') as pkf:
                                    deck_info["publish_pack"] = pkf.read()
                            except Exception:
                                pass

                        decks.append(deck_info)

            resp = {'status': 'ok', 'decks': decks, 'total': len(decks)}
            self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/generate_deck':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                req = json.loads(post_data.decode('utf-8'))
                news_text = req.get('news_text', '').strip()
                title = req.get('title', '').strip()
                category = req.get('category', '财经/宏观经济')
                export_png = req.get('export_png', True)

                if not news_text and not title:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'news_text 或 title 不能为空'}).encode('utf-8'))
                    return

                if not news_text:
                    news_text = title

                if generate_deck_api is None:
                    raise RuntimeError("Pipeline 模块未能正常加载，请检查 Python 依赖")

                print(f"\n[API] 收到生成请求: title='{title}', news_text='{news_text[:50]}...'")
                result = generate_deck_api(
                    news_text=news_text,
                    custom_headline=title,
                    category=category,
                    export_png=export_png
                )
                print(f"[API] 图文包全套生成成功: {result.get('topic_id')}")

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'success': True, 'deck': result, 'data': result}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                print(f"[API ERROR] 生成失败: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'error', 'success': False, 'message': str(e)}, ensure_ascii=False).encode('utf-8'))
            return

        elif self.path == '/api/save_to_desktop':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                topic_id = data.get('topic_id')
                files = data.get('files', [])
                
                os.makedirs(DESKTOP_DIR, exist_ok=True)
                saved_files = []

                # 如果传入已存在的 topic_id，直接复制 examples/{topic_id}/ 下所有 PNG / 产物
                if topic_id:
                    src_dir = os.path.join(EXAMPLES_DIR, topic_id)
                    if os.path.exists(src_dir):
                        topic_desktop_dir = os.path.join(DESKTOP_DIR, topic_id)
                        os.makedirs(topic_desktop_dir, exist_ok=True)
                        for fn in sorted(os.listdir(src_dir)):
                            if fn.endswith('.png') or fn.endswith('.html') or fn == 'publish_pack.txt':
                                s_path = os.path.join(src_dir, fn)
                                d_path = os.path.join(topic_desktop_dir, fn)
                                shutil.copy2(s_path, d_path)
                                if fn.endswith('.png'):
                                    root_copy = os.path.join(DESKTOP_DIR, f"{topic_id}_{fn}")
                                    shutil.copy2(s_path, root_copy)
                                saved_files.append({
                                    'name': fn,
                                    'path': d_path
                                })
                
                # 如果传入 base64 files
                for item in files:
                    filename = item.get('name', 'card.png')
                    b64_data = item.get('data', '')
                    if ',' in b64_data:
                        b64_data = b64_data.split(',', 1)[1]
                    file_bytes = base64.b64decode(b64_data)
                    file_path = os.path.join(DESKTOP_DIR, filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_bytes)
                    saved_files.append({
                        'name': filename,
                        'size': len(file_bytes),
                        'path': file_path
                    })
                
                resp = {
                    'success': True,
                    'count': len(saved_files),
                    'target_dir': DESKTOP_DIR,
                    'saved_dir': os.path.join(DESKTOP_DIR, topic_id) if topic_id else DESKTOP_DIR,
                    'files': [f['name'] for f in saved_files]
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
                print(f"[SUCCESS] 成功保存 {len(saved_files)} 个文件至 {DESKTOP_DIR}")
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}, ensure_ascii=False).encode('utf-8'))
                print(f"[ERROR] 保存失败: {e}")
        else:
            self.send_error(404, "Endpoint not found")

if __name__ == '__main__':
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CreatorStudioHandler) as httpd:
        print(f"=======================================================")
        print(f"⚡ 小红书图文工坊一体化服务已启动: http://localhost:{PORT}")
        print(f"📂 本地静态目录: {WEB_DIR}")
        print(f"💻 桌面导出目录: {DESKTOP_DIR}")
        print(f"🛠️ 后端工业流水线状态: {'就绪 (可用)' if generate_deck_api else '未加载'}")
        print(f"=======================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
