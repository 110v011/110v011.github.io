import streamlit as st
import yt_dlp
import io
import sys
import base64
import random
import time

# ページの設定
st.set_page_config(
    page_title="Ultimate YouTube Downloader",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ Candl")
st.caption("完全対応 ｜ 暗号化URL ｜ 速度スロットリング ｜ 端末直下保存")

# 🔍 対策1: ネットワーク監視システム（iFilter等）のパケット検知を避けるためのURL難読化デコーダー
def decode_url(encoded_str):
    try:
        # Base64または十六進数で隠蔽されたURLを復元する
        if encoded_str.startswith("http"):
            return encoded_str
        return base64.b64decode(encoded_str.encode()).decode()
    except:
        return encoded_str

# タブ機能で入力方法を分ける
tab1, tab2 = st.tabs(["通常URL入力", "🔒 暗号化URL入力（iFilter完全回避）"])

with tab1:
    url_input = st.text_input("YouTubeの動画URLを入力してください:", placeholder="https://youtube.com...", key="normal_url")

with tab2:
    st.markdown("""
    💡 **iFilterなどの強力なネットワーク監視対策:**
    社内や学校のWi-Fiで「youtube」という文字列自体がパケット監視で弾かれる場合、URLをBase64等に暗号化して入力することで、ネットワーク機器の自動ブロックを完全にすり抜けます。
    """)
    encrypted_url = st.text_area("暗号化（Base64等）されたURLを入力:", placeholder="aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g/dj0...", key="enc_url")

# クッキー設定（YouTube側のログイン規制・403エラー回避用）
with st.sidebar:
    st.header("⚙️ 上級者用・回避オプション")
    use_cookies = st.checkbox("YouTubeのCookies（クッキー）を使用する", value=False)
    cookie_text = ""
    if use_cookies:
        cookie_text = st.text_area("Netscape形式のクッキーテキストを貼り付け:", height=150, placeholder="# Netscape HTTP Cookie File...")

# 選択されたURLの確定
target_url = url_input if url_input else decode_url(encrypted_url)

# 画質フォーマットの選択
download_type = st.selectbox(
    "画質・フォーマットを選択してください:",
    [
        "動画: 高画質固定 (720p / 結合なし・超高速・安全)",
        "動画: 最高画質 (1080p以上 / サーバー側でFFmpeg結合)",
        "動画: 標準画質 (480p / 容量＆通信量節約)",
        "音声のみ: MP3形式 (高音質 192kbps)"
    ]
)

if target_url:
    if st.button("🌟 制限を全回避してダウンロードファイルを生成"):
        
        with st.spinner("ディープ・ステルスモードで動画データを取得中..."):
            
            buffer = io.BytesIO()
            
            # 🛡️ 対策2: 人間のアクセス挙動に似せるためのランダムな遅延（スキャン検知防止）
            time.sleep(random.uniform(0.5, 2.0))
            
            # 🛡️ 対策3: 最新のChrome/Edge/Safari等のUser-Agentリストからランダムに偽装（固定UAによるパターン検知を打破）
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
            ]
            chosen_ua = random.choice(user_agents)
            
            # 高度なyt-dlpステルスオプション
            ydl_opts = {
                'outtmpl': '-',  # メモリへのストリーミング出力
                'logtostderr': True,
                'quiet': True,
                
                # --- 強力なネットワーク・Bot制限回避オプション ---
                'nocheckcertificate': True,         # iFilterのSSLデコード（割り込み）によるエラーの完全回避
                'geo_bypass': True,                 # 地域制限・IPブロックの自動回避
                'rm_cache_dir': True,               # キャッシュを残さず不審な挙動としてマークされるのを防ぐ
                'no_warnings': True,
                
                # 🛡️ 対策4: 短時間での大量バースト通信を抑え、iFilterの「異常トラフィック検知」に引っかからないようにする
                'ratelimit': 5 * 1024 * 1024,       # ダウンロード速度を5MB/sに制限（あえてゆっくり落とす）
                'fragment_retries': 10,             # 通信が一時的に遮断されても10回まで自動リトライ
                'retry_sleep_functions': {'http': lambda n: 5 * (n + 1)}, # リトライ時に間隔をあける
                
                'http_headers': {
                    'User-Agent': chosen_ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                    'Sec-Fetch-Mode': 'navigate',
                    'Connection': 'keep-alive',
                },
                
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios', 'android', 'web'], # 複数のクライアントタイプを混ぜてYouTubeのAI検知を翻弄
                        'skip': ['dash', 'hls']
                    }
                }
            }
            
            # クッキーによる認証追加（ログイン必須動画や、IPごと規制された場合の突破口）
            if use_cookies and cookie_text:
                cookie_file = "temp_cookies.txt"
                with open(cookie_file, "w") as f:
                    f.write(cookie_text)
                ydl_opts['cookiefile'] = cookie_file
            
            # フォーマット選択の分岐
            if "720p" in download_type:
                ydl_opts['format'] = 'best[height<=720][ext=mp4]/best[height<=720]'
                mime_type = "video/mp4"
                file_ext = "mp4"
            elif "最高画質" in download_type:
                ydl_opts['format'] = 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]'
                ydl_opts['merge_output_format'] = 'mp4'
                mime_type = "video/mp4"
                file_ext = "mp4"
            elif "480p" in download_type:
                ydl_opts['format'] = 'best[height<=480][ext=mp4]/best[height<=480]'
                mime_type = "video/mp4"
                file_ext = "mp4"
            else:
                ydl_opts['format'] = 'ba/b'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                mime_type = "audio/mpeg"
                file_ext = "mp3"
                
            try:
                # 1. タイトルの取得
                title_opts = {'quiet': True, 'nocheckcertificate': True}
                if use_cookies and cookie_text:
                    title_opts['cookiefile'] = "temp_cookies.txt"
                    
                with yt_dlp.YoutubeDL(title_opts) as ydl:
                    info = ydl.extract_info(target_url, download=False)
                    title = info.get('title', 'video')
                    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c in ' ._-']).strip()
                
                # 2. メモリへのパイプダウンロード実行
                class StreamToBuffer(object):
                    def __init__(self, buf):
                        self.buf = buf
                    def write(self, data):
                        self.buf.write(data)
                    def flush(self):
                        pass

                original_stdout = sys.stdout
                try:
                    sys.stdout = StreamToBuffer(buffer)
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([target_url])
                finally:
                    sys.stdout = original_stdout
                
                buffer.seek(0)
                file_data = buffer.getvalue()
                
                # クッキー一時ファイルの削除
                import os
                if os.path.exists("temp_cookies.txt"):
                    os.remove("temp_cookies.txt")
                
                if len(file_data) > 0:
                    st.success("🎉 Candl")
                    st.download_button(
                        label="📥 Dl",
                        data=file_data,
                        file_name=f"{safe_title}.{file_ext}",
                        mime=mime_type,
                        use_container_width=True
                    )
                else:
                    st.error("Error_Data_Min")
                    
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
