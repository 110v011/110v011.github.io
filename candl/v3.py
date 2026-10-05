import streamlit as st
import yt_dlp

st.set_page_config(
    page_title="Educational Media Research Tool",  # 教育・研究用に見えるタイトルに変更
    page_icon="📚", # アイコンもエンタメ感を消す
    layout="centered"
)

# UIカモフラージュ（i-FILTERの目視確認対策：一見するとただの教育用リンク集に見せる）
st.markdown("""
    <style>
    .stTextInput input { font-size: 18px !important; padding: 12px !important; }
    .custom-dl-btn {
        display: inline-block;
        background-color: #1A73E8; /* Googleライクな青色に変更 */
        color: white !important;
        padding: 14px 24px;
        font-size: 18px;
        font-weight: bold;
        text-decoration: none;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📚 メディア学術解析・検証ツール")
st.caption("本システムは、オンライン動画のエンコーディングおよびストリーミング検証用の研究環境です。")

url = st.text_input("検証対象のオブジェクトURLを入力:", placeholder="https://...")

if url:
    with st.spinner("プロキシキャッシュの整合性を確認中..."):
        
        # カテゴリ外ブロック（未分類ブロック）およびDPI（深層パケット解析）対策の超強化ヘッダー
        ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'http_headers': {
                # iPad Safariの最新環境に偽装
                'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/605.1.15',
                # Google検索を経由してきたかのように見せかける（カテゴリ偽装の補強）
                'Referer': 'https://google.com',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
                # プロキシの「カテゴリ未分類」スキャンをパスするための各種キャッシュ制御ヘッダー
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Dest': 'document',
            }
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Verified Object')
                video_url = info.get('url')
                
                st.success(f"解析完了: {video_title}")
                
                st.markdown("### 📥 iPad用データストリーム出力")
                # 新規タブ展開
                st.markdown(
                    f'<a href="{video_url}" target="_blank" class="custom-dl-btn">▶️ ストリームデータを別タブで開く</a>', 
                    unsafe_allow_html=True
                )
                
                st.info(
                    "**【保存手順】**\n\n"
                    "1. 上の青いボタンをタップして別タブを開きます。\n"
                    "2. iPad Safariの「共有（矢印）アイコン」をタップします。\n"
                    "3. 「\"ファイル\"に保存」を選択してください。"
                )

        except Exception as e:
            st.error("アクセス拒否またはネットワークエラーが発生しました。")
            st.warning("i-FILTER等のプロキシにより上位ドメインが遮断されている可能性があります。")
