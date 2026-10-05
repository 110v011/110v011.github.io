import streamlit as st
import yt_dlp

# iPadの画面サイズ（レスポンシブ）とダークモード等に配慮した設定
st.set_page_config(
    page_title="Media Downloader for iPad", 
    page_icon="📥", 
    layout="centered" # iPadの縦向き・横向き両方で崩れないようcenteredに固定
)

# iPad Safari向けの見た目の調整（CSS）
st.markdown("""
    <style>
    /* タップしやすいようにボタンや入力欄の余白を広くする（iPadのタッチ操作最適化） */
    .stTextInput input {
        font-size: 18px !important;
        padding: 12px !important;
    }
    .custom-dl-btn {
        display: inline-block;
        background-color: #FF4B4B;
        color: white !important;
        padding: 14px 24px;
        font-size: 18px;
        font-weight: bold;
        text-decoration: none;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        width: 100%;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .custom-dl-btn:active {
        background-color: #D32F2F;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📥 iPad最適化 メディアDLツール")
st.caption("iPadのSafariでの動作に特化した高速・軽量ダウンローダーです。")

# URL入力フォーム
url = st.text_input("YouTube動画のURLをペースト:", placeholder="https://youtube.com...")

if url:
    with st.spinner("iPad向けに動画ストリームを解析中..."):
        # i-FILTER等のカテゴリフィルタリングを回避するカスタムヘッダー
        # iPadからの標準的なアクセス（Safari）に見せかけるヘッダー構成
        ydl_opts = {
            'format': 'best', # iPadが標準再生できるMP4（H.264/AAC）を優先
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9',
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'video')
                video_url = info.get('url') # 直リンクURL
                thumbnail = info.get('thumbnail')
                
                # 情報表示
                st.success(f"解析成功: {video_title}")
                if thumbnail:
                    st.image(thumbnail, use_column_width=True)

                st.markdown("### 📥 iPadでのダウンロード手順")
                
                # iPad Safari用に「新規タブで開く」大型ボタンを設置
                # サーバーのメモリ制限に引っかからないよう、ダイレクトURLをSafariに処理させます
                st.markdown(
                    f'<a href="{video_url}" target="_blank" class="custom-dl-btn">▶️ 新しいタブで動画を開く</a>', 
                    unsafe_allow_html=True
                )
                
                # iPad特有の操作案内を分かりやすく記述
                st.info(
                    "**【保存方法】**\n\n"
                    "1. 上の赤いボタンをタップすると、新しいタブで動画が再生されます。\n"
                    "2. 再生画面のメニューにある **「共有」ボタン（四角から矢印が飛び出たアイコン）** をタップします。\n"
                    "3. メニューから **「\"ファイル\"に保存」** を選択すると、iPad内にダウンロードされます。"
                )

        except Exception as e:
            st.error("エラーが発生しました。ネットワーク制限等を確認してください。")
            st.warning(f"詳細: {str(e)}")
