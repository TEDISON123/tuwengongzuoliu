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

PORT = 8080
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DESKTOP_DIR = os.path.expanduser("~/Desktop/小红书图文")

os.makedirs(DESKTOP_DIR, exist_ok=True)

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
                'exists': os.path.exists(DESKTOP_DIR)
            }
            self.wfile.write(json.dumps(status_data, ensure_ascii=False).encode('utf-8'))
            return
        elif self.path == '/':
            self.path = '/index.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save_to_desktop':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                files = data.get('files', [])
                
                os.makedirs(DESKTOP_DIR, exist_ok=True)
                
                saved_files = []
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
                    'files': [f['name'] for f in saved_files]
                }
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps(resp, ensure_ascii=False).encode('utf-8'))
                print(f"[SUCCESS] 成功保存 {len(saved_files)} 张图片至 {DESKTOP_DIR}")
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
        print(f"Server started at http://localhost:{PORT}")
        print(f"Target desktop folder: {DESKTOP_DIR}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
