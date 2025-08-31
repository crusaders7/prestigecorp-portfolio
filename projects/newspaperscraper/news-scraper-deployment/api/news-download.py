# api/news-download.py
from http.server import BaseHTTPRequestHandler
import json
from urllib.parse import quote
import io
import zipfile


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error_response(400, 'No data received')
                return

            post_data = self.rfile.read(content_length)

            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, f'Invalid JSON data: {str(e)}')
                return
            except UnicodeDecodeError as e:
                self.send_error_response(
                    400, f'Invalid UTF-8 encoding: {str(e)}')
                return

            articles = data.get('articles', [])
            if not articles or not isinstance(articles, list):
                self.send_error_response(
                    400, 'No articles provided or articles not in list format')
                return

            filename = data.get('filename', 'articles.json')
            filename = quote(filename)
            file_format = data.get('format', 'json').lower()

            if file_format == 'zip':
                try:
                    # Create a ZIP file in memory
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        # Add articles as JSON
                        zip_file.writestr(
                            'articles.json', json.dumps(articles, indent=2))

                        # Add individual text files for each article
                        for i, article in enumerate(articles):
                            if 'title' in article and 'content' in article:
                                article_filename = f"article_{i+1}_{article.get('title', 'untitled')[:50]}.txt"
                                # Clean filename
                                article_filename = ''.join(
                                    c for c in article_filename if c.isalnum() or c in '._- ')
                                article_content = f"Title: {article.get('title', 'No title')}\n"
                                article_content += f"Date: {article.get('date', 'No date')}\n"
                                article_content += f"URL: {article.get('url', 'No URL')}\n\n"
                                article_content += article.get(
                                    'content', 'No content')
                                zip_file.writestr(
                                    article_filename, article_content)

                    zip_buffer.seek(0)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/zip')
                    self.send_header(
                        'Content-Disposition', f'attachment; filename="{filename.replace(".json", ".zip")}"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(zip_buffer.read())

                except Exception as e:
                    print(f"Error creating ZIP file: {e}")
                    self.send_error_response(
                        500, f'Failed to create ZIP file: {str(e)}')

            else:
                try:
                    # Default: return JSON
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Content-Disposition',
                                     f'attachment; filename="{filename}"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(articles, indent=2).encode())
                except Exception as e:
                    print(f"Error creating JSON response: {e}")
                    self.send_error_response(
                        500, f'Failed to create JSON response: {str(e)}')

        except Exception as e:
            print(f"Unexpected error in download do_POST: {e}")
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def send_error_response(self, code, message):
        try:
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {'error': message}
            self.wfile.write(json.dumps(error_response).encode())
        except Exception as e:
            print(f"Failed to send error response: {e}")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Internal server error')
            except:
                print(
                    f"Critical error - unable to send any response: {message}")
