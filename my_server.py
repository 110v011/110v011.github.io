from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
from urllib.parse import parse_qs, urlparse, urljoin
import traceback
import re  # HTML書き換え用の正規表現ライブラリ

class UltimateProxyServer(BaseHTTPRequestHandler):
    
    # 最初のURL入力画面
    def show_input_form(self, message="", detail_error=""):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        
        error_box = f"""
        <div style="background: #fff0f0; border: 1px solid #ffcccc; color: red; padding: 15px; margin-top: 20px; text-align: left;">
            <strong>❌ エラー:</strong> {message}
            <pre style="background: #222; color: #fff; padding: 10px; overflow-x: auto; font-size: 13px;">{detail_error}</pre>
        </div>
        """ if message else ""

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>全自動リンク中継プロキシ</title>
            <style>
                body {{ font-family: sans-serif; max-width: 700px; margin: 60px auto; padding: 0 20px; text-align: center; }}
                input[type="url"] {{ width: 80%; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 15px; }}
                input[type="submit"] {{ padding: 12px 24px; font-size: 16px; background-color: #e11d48; color: white; border: none; border-radius: 4px; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h1>🚀 サーバーを経由してインターネットを閲覧</h1>
            <p>今すぐurlを入力してウェブをブラウズ</p>
            <form method="GET" action="/fetch">
                <input type="url" name="target_url" value="https://example.com" required>
                <input type="submit" value="🔍ブラウズする">
            </form>
            {error_box}
        </body>
        </html>
        """
        self.wfile.write(html.encode("utf-8"))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        
        if parsed_url.path == "/fetch":
            query_params = parse_qs(parsed_url.query)
            target_url_list = query_params.get("target_url", [])
            
            if target_url_list:
                target_url = target_url_list[0].strip()
                if not target_url.startswith(("http://", "https://")):
                    target_url = "https://" + target_url

                try:
                    # 1. サーバーがターゲットサイトのデータを取得
                    req = urllib.request.Request(
                        target_url, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        content_type = response.headers.get('Content-Type', 'text/html')
                        raw_data = response.read()
                        
                        # 2. もしデータがHTML（ウェブページ）なら、中のリンクをすべて書き換える
                        if "text/html" in content_type:
                            html_text = raw_data.decode('utf-8', errors='ignore')
                            
                            # 自分のサーバー（トンネルアドレス）のベースURLを取得
                            my_host = self.headers.get('Host')
                            my_proxy_url = f"https://{my_host}/fetch?target_url="
                            
                            # HTML内の href="..." と src="..." を見つけ出す正規表現
                            # 相手サイトの相対パス（/page2）を絶対パス（https://site.com）に直した上で、自分のプロキシURLを頭に付与する
                            def replace_link(match):
                                attr = match.group(1) # 'href' または 'src'
                                quote = match.group(2) # '"' または "'"
                                url = match.group(3) # 中身のURL
                                
                                # 内部リンク（#chpter1など）や javascript: は書き換えない
                                if url.startswith(("#", "javascript:", "data:")):
                                    return match.group(0)
                                
                                # 不完全なURLを完全なURLに変換
                                full_url = urljoin(target_url, url)
                                # 自分のプロキシURLを頭にくっつける
                                return f'{attr}={quote}{my_proxy_url}{full_url}{quote}'
                            
                            # 正規表現で一括置換
                            pattern = r'(href|src)=(["\'])(.*?)\2'
                            html_text = re.sub(pattern, replace_link, html_text)
                            raw_data = html_text.encode('utf-8')

                        # 3. クライアントにデータを返却
                        self.send_response(200)
                        self.send_header("Content-type", content_type)
                        # セキュリティ制限を緩和して無理やり表示させる
                        self.send_header("Content-Security-Policy", "default-src * 'unsafe-inline' 'unsafe-eval' data: blob:;")
                        self.end_headers()
                        self.wfile.write(raw_data)
                        
                except Exception as e:
                    self.show_input_form(message=f"アクセス失敗: {e}", detail_error=traceback.format_exc())
            else:
                self.show_input_form(message="URLがありません。")
        else:
            self.show_input_form()

def run():
    host = "0.0.0.0"
    port = 8000
    server = HTTPServer((host, port), UltimateProxyServer)
    print(f"🚀 リンク自動巡回型プロキシが起動しました (ポート:{port})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました。")
        server.server_close()

if __name__ == "__main__":
    run()
