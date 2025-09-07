from http.server import BaseHTTPRequestHandler
import json
import zipfile
import io
import re
from datetime import datetime


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
            format_type = data.get('format', 'json').lower()

            if not articles or not isinstance(articles, list):
                self.send_error_response(
                    400, 'No articles provided or articles not in list format')
                return

            if format_type == 'json':
                self.generate_json_download(articles)
            elif format_type == 'zip':
                self.generate_zip_download(articles)
            else:
                self.send_error_response(
                    400, f'Unsupported format: {format_type}. Supported formats: json, zip')

        except Exception as e:
            print(f"Unexpected error in download do_POST: {e}")
            self.send_error_response(500, f'Internal server error: {str(e)}')

    def generate_json_download(self, articles):
        """Generate JSON file download"""
        try:
            # Create comprehensive JSON structure
            export_data = {
                'export_info': {
                    'generated_at': datetime.now().isoformat(),
                    'total_articles': len(articles),
                    'format': 'json',
                    'generator': 'Universal News Scraper'
                },
                'articles': articles
            }

            json_content = json.dumps(
                export_data, indent=2, ensure_ascii=False)
            json_bytes = json_content.encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Disposition',
                             'attachment; filename="news_articles.json"')
            self.send_header('Content-Length', str(len(json_bytes)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json_bytes)

        except Exception as e:
            print(f"Error generating JSON download: {e}")
            self.send_error_response(
                500, f'Failed to generate JSON file: {str(e)}')

    def generate_zip_download(self, articles):
        """Generate ZIP file download with individual text files and JSON"""
        try:
            # Create in-memory ZIP file
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Add individual article text files
                for i, article in enumerate(articles, 1):
                    if 'error' in article:
                        continue

                    title = article.get('title', f'Article {i}')
                    # Clean filename
                    filename = self.clean_filename(title)
                    content = self.format_article_text(article)

                    zip_file.writestr(f"{i:03d}_{filename}.txt", content)

                # Add comprehensive JSON file
                export_data = {
                    'export_info': {
                        'generated_at': datetime.now().isoformat(),
                        'total_articles': len([a for a in articles if 'error' not in a]),
                        'format': 'zip_with_json',
                        'generator': 'Universal News Scraper'
                    },
                    'articles': articles
                }

                json_content = json.dumps(
                    export_data, indent=2, ensure_ascii=False)
                zip_file.writestr("articles_data.json", json_content)

                # Add README file
                readme_content = self.generate_readme(articles)
                zip_file.writestr("README.txt", readme_content)

            zip_data = zip_buffer.getvalue()

            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition',
                             'attachment; filename="news_articles.zip"')
            self.send_header('Content-Length', str(len(zip_data)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(zip_data)

        except Exception as e:
            print(f"Error generating ZIP download: {e}")
            self.send_error_response(
                500, f'Failed to generate ZIP file: {str(e)}')

    def clean_filename(self, title):
        """Clean title for use as filename"""
        # Remove or replace invalid filename characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', title)
        filename = re.sub(r'\s+', '_', filename)
        filename = filename.strip('._')

        # Limit length
        if len(filename) > 50:
            filename = filename[:47] + "..."

        return filename or "untitled"

    def format_article_text(self, article):
        """Format article as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append(f"TITLE: {article.get('title', 'No title')}")
        lines.append("=" * 80)

        if article.get('date'):
            lines.append(f"DATE: {article['date']}")

        if article.get('url'):
            lines.append(f"SOURCE: {article['url']}")

        if article.get('scraped_at'):
            lines.append(f"SCRAPED: {article['scraped_at']}")

        lines.append("")
        lines.append("CONTENT:")
        lines.append("-" * 40)
        lines.append(article.get('content', 'No content available'))
        lines.append("")
        lines.append("=" * 80)

        return "\n".join(lines)

    def generate_readme(self, articles):
        """Generate README file for ZIP archive"""
        total_articles = len([a for a in articles if 'error' not in a])
        error_count = len([a for a in articles if 'error' in a])

        readme = f"""Universal News Scraper Export
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONTENTS:
- {total_articles} article text files (001_*.txt, 002_*.txt, etc.)
- articles_data.json: Complete data in JSON format
- README.txt: This file

STATISTICS:
- Successfully scraped: {total_articles} articles
- Errors encountered: {error_count} articles
- Total URLs processed: {len(articles)} articles

FILE NAMING:
- Text files are numbered sequentially (001, 002, etc.)
- Filenames are cleaned versions of article titles
- Special characters are replaced with underscores

JSON FORMAT:
The articles_data.json file contains the complete export data including:
- Export metadata (generation time, statistics)
- Full article data with all extracted fields
- Error information for failed scrapes

USAGE NOTES:
- Text files are formatted for easy reading
- JSON file can be imported into data analysis tools
- All content is extracted from publicly available sources
- Please respect copyright and fair use guidelines

Generated by Universal News Scraper
https://github.com/crusaders7/news-scraper-vercel
"""
        return readme

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
