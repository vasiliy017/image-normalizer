#!/usr/bin/env python3
"""
Простий веб-сервер для порівняння іконок з папок 'in' та 'out'
"""
import os
import json
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class ComparisonHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # API endpoint для отримання списку файлів
        if path == '/api/images':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            in_folder = Path('in')
            out_folder = Path('out')

            in_files = []
            out_files = []

            if in_folder.exists():
                in_files = sorted([f.name for f in in_folder.glob('*.png')])

            if out_folder.exists():
                out_files = sorted([f.name for f in out_folder.glob('*.png')])

            data = {
                'in': in_files,
                'out': out_files
            }

            self.wfile.write(json.dumps(data).encode())
            return

        # Serve файли з папок
        if path.startswith('/files/in/'):
            filename = path.replace('/files/in/', '')
            filepath = Path('in') / filename
            if filepath.exists() and filepath.suffix.lower() == '.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                return

        if path.startswith('/files/out/'):
            filename = path.replace('/files/out/', '')
            filepath = Path('out') / filename
            if filepath.exists() and filepath.suffix.lower() == '.png':
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
                return

        # Serve comparison.html для кореневої路徑
        if path == '/' or path == '':
            self.path = '/comparison.html'
            # Шукаємо comparison.html в scriptsirectорії
            comparison_path = Path(__file__).parent / 'comparison.html'
            if not comparison_path.exists():
                # Копіюємо з scratchpad якщо він є там
                import shutil
                src = Path('/private/tmp/claude-501/-Users-vasiliy-git-my-image-normalization/79dde261-3d2c-490a-8e71-b49fcbdac354/scratchpad/comparison.html')
                if src.exists():
                    shutil.copy(src, comparison_path)

        # Default handler для інших файлів
        super().do_GET()

    def log_message(self, format, *args):
        print(f"[SERVER] {format % args}")


if __name__ == '__main__':
    port = 8000

    # Перевіряємо чи існує comparison.html
    comp_file = Path('comparison.html')
    if not comp_file.exists():
        print("⚠️  Файл comparison.html не знайдено. Копіюю...")
        import shutil
        src = Path('/private/tmp/claude-501/-Users-vasiliy-git-my-image-normalization/79dde261-3d2c-490a-8e71-b49fcbdac354/scratchpad/comparison.html')
        if src.exists():
            shutil.copy(src, comp_file)
            print("✅ Файл скопійовано")
        else:
            print("❌ Не вдалося знайти исходний файл comparison.html")
            exit(1)

    server = HTTPServer(('localhost', port), ComparisonHandler)
    print(f"""
╔════════════════════════════════════════╗
║  🖼️  Порівняння іконок - Viewer        ║
╚════════════════════════════════════════╝

✨ Сервер запущено на http://localhost:{port}

Нажміть CTRL+C для зупинки сервера
    """)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Сервер зупинено")
        exit(0)
