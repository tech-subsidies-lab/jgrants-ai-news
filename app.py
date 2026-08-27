import json
import urllib.parse
import urllib.request
import os
import time

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def generate_ai_text(prompt, retries=2):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        print("【警告】GEMINI_API_KEY が設定されていません。")
        return "<p>※本補助金の詳細解説・要件については、jGrants公式サイトおよび公募要領をご確認ください。</p>"
    
    # エンドポイントを v1 / gemini-1.5-flash に変更
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode("utf-8"), 
                headers=headers, 
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait_time = 15 * (attempt + 1)
                print(f"429 Rate Limit検知。{wait_time}秒待機して再試行します...")
                time.sleep(wait_time)
            elif e.code == 404:
                # v1beta へのフォールバック試行
                print(f"v1で404が発生したため、v1betaで試行します...")
                fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
                try:
                    req_fb = urllib.request.Request(
                        fallback_url, 
                        data=json.dumps(payload).encode("utf-8"), 
                        headers=headers, 
                        method="POST"
                    )
                    with urllib.request.urlopen(req_fb, timeout=30) as response_fb:
                        res_data_fb = json.loads(response_fb.read().decode("utf-8"))
                        return res_data_fb["candidates"][0]["content"]["parts"][0]["text"]
                except Exception as fb_err:
                    print(f"フォールバック失敗: {fb_err}")
                    break
            else:
                print(f"HTTP Error {e.code}: {e.reason}")
                break
        except Exception as e:
            print(f"Gemini API Error: {e}")
            break
            
    return "<p>※本補助金の詳細解説・要件については、jGrants公式サイトおよび公募要領をご確認ください。</p>"

BASE_URL = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"

params = {
    "keyword": "IT",
    "acceptance": "1",
    "sort": "created_date",
    "order": "DESC",
}

try:
    url = f"{BASE_URL}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    with urllib.request.urlopen(req, timeout=10) as response:
        res_body = response.read().decode("utf-8")
        data = json.loads(res_body)

    subsidies = data.get("result", [])[:10]

    ad_code = """
    <div class="ad-banner" style="text-align: center; margin: 30px 0;">
        <a href="https://px.a8.net/svt/ejp?a8mat=4BAEXG+8FN3AQ+4JGQ+C3J0H" rel="nofollow">
        <img border="0" width="336" height="280" alt="おすすめサービス" src="https://www29.a8.net/svt/bgt?aid=260826388510&wid=001&eno=01&mid=s00000021185002032000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4BAEXG+8FN3AQ+4JGQ+C3J0H" alt="">
    </div>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IT補助金・助成金ナビ | 公募中の最新支援情報まとめ</title>
    <meta name="description" content="現在公募中のIT関連補助金・助成金の最新情報を一挙掲載。対象地域や受付締切日、わかりやすい活用ポイントを解説しています。">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.8; margin: 0; padding: 20px; background-color: #f4f6f9; color: #333; }}
        .container {{ max-width: 850px; margin: 0 auto; }}
        .hero {{ background: #ffffff; padding: 25px 30px; border-radius: 8px; border: 1px solid #e1e4e8; margin-bottom: 25px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }}
        .hero h1 {{ font-size: 1.8em; margin: 0 0 10px 0; color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 8px; }}
        .hero p {{ margin: 0; color: #4a5568; font-size: 0.95em; line-height: 1.6; }}
        .section-title {{ font-size: 1.4em; color: #1a252f; margin-bottom: 15px; padding-left: 8px; border-left: 4px solid #0056b3; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03); }}
        .title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .title a {{ color: #0056b3; text-decoration: none; }}
        .title a:hover {{ text-decoration: underline; }}
        .meta {{ font-size: 0.88em; color: #586069; display: flex; flex-wrap: wrap; gap: 15px; align-items: center; }}
        .tag {{ background: #e1f5fe; color: #0288d1; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="hero">
            <h1>IT補助金・助成金ナビ</h1>
            <p>当サイトは、デジタル化や設備投資、業務効率化を目指す中小企業・個人事業主様に向けて、公的に募集されている全国の補助金・助成金情報をわかりやすくまとめたポータルサイトです。対象地域や公募締切、制度ごとの活用メリットやおすすめポイントを解説しています。</p>
        </header>

        {ad_code}

        <h2 class="section-title">現在募集中の補助金・助成金一覧</h2>
"""

    for item in subsidies:
        subsidy_id = item.get("id", "")
        title = item.get("title", "名称なし")
        inst_name = item.get("institution_name")
        target_area = item.get("target_area_search", "全国")
        end_date = item.get("acceptance_end_datetime", "不明")
        target_summary = item.get("target_summary", "詳細情報は公募要領をご確認ください。")

        if end_date != "不明" and "T" in end_date:
            end_date = end_date.split("T")[0]

        detail_filename = f"subsidy-{subsidy_id}.html"

        print(f"生成中: {title[:20]}...")
        prompt = f"""
補助金「{title}」（概要：{target_summary}）についてのWeb解説記事を作成してください。
以下の3セクション構成で、HTMLタグ（<p>, <h3>, <ul>, <li>）を用いてまとめて出力してください。

1. 【はじめに】: 読者の関心を引き、どのような補助金かを簡潔に解説（<p>2〜3文）
2. 【詳細解説】: どのような企業・事業者におすすめか、申請・導入のメリット、活用事例を具体的に解説（<h3>や<ul>を使用）
3. 【まとめ】: 申請に向けた注意点やアドバイス（<p>2〜3文）

出力は上記の解説部分のHTMLコードのみにしてください。
"""
        ai_article = generate_ai_text(prompt)
        time.sleep(3)

        clean_summary = target_summary.replace("<", "").replace(">", "")[:110]
        meta_desc = f"{title}の概要・活用メリット・申請手順を徹底解説。{clean_summary}..."

        inst_meta_html = ""
        if inst_name and str(inst_name).strip().lower() not in ["none", "null", ""]:
            inst_meta_html = f"<p><strong>制度名:</strong> {inst_name}</p>"

        detail_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}の解説と活用ガイド - IT補助金・助成金ナビ</title>
    <meta name="description" content="{meta_desc}">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.8; margin: 0; padding: 20px; background-color: #f4f6f9; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .back-link-box {{ margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #edf2f7; }}
        .back-link {{ color: #0056b3; text-decoration: none; font-weight: bold; font-size: 0.95em; display: inline-block; }}
        .back-link:hover {{ text-decoration: underline; }}
        h1 {{ font-size: 1.6em; color: #1a252f; margin-top: 10px; margin-bottom: 20px; line-height: 1.4; border-bottom: 3px solid #0056b3; padding-bottom: 10px; }}
        h2 {{ font-size: 1.3em; color: #0056b3; border-left: 4px solid #0056b3; padding-left: 10px; margin-top: 35px; margin-bottom: 15px; }}
        .meta-box {{ background: #e1f5fe; padding: 15px 20px; border-radius: 6px; margin: 20px 0; border: 1px solid #b3e5fc; }}
        .meta-box p {{ margin: 6px 0; }}
        .toc {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 15px 20px; margin: 25px 0; }}
        .toc-title {{ font-weight: bold; margin-bottom: 10px; border-bottom: 1px solid #dee2e6; padding-bottom: 5px; }}
        .toc ul {{ margin: 0; padding-left: 20px; }}
        .toc li {{ margin-bottom: 6px; }}
        .toc a {{ color: #0056b3; text-decoration: none; }}
        .toc a:hover {{ text-decoration: underline; }}
        .btn {{ display: inline-block; background: #0056b3; color: #fff; padding: 12px 24px; border-radius: 5px; text-decoration: none; font-weight: bold; margin-top: 15px; text-align: center; }}
        .btn:hover {{ background: #004085; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="back-link-box">
            <a href="index.html" class="back-link">← 補助金一覧に戻る</a>
        </div>

        <h1>{title}</h1>
        
        <nav class="toc">
            <div class="toc-title">目次</div>
            <ul>
                <li><a href="#overview">1. 補助金の基本概要</a></li>
                <li><a href="#guide">2. ポイント解説・活用ガイド</a></li>
            </ul>
        </nav>

        {ad_code}

        <section id="overview">
            <h2>1. 補助金の基本概要</h2>
            <div class="meta-box">
                {inst_meta_html}
                <p><strong>対象地域:</strong> {target_area}</p>
                <p><strong>受付終了日:</strong> {end_date}</p>
            </div>
        </section>

        {ad_code}

        <section id="guide">
            <h2>2. ポイント解説・活用ガイド</h2>
            {ai_article}
            <p style="text-align: center; margin-top: 30px;">
                <a href="https://www.jgrants-portal.go.jp/subsidy/{subsidy_id}" target="_blank" rel="noopener" class="btn">jGrants 公式サイトで申請要領を確認する</a>
            </p>
        </section>

        {ad_code}
    </div>
</body>
</html>"""

        with open(detail_filename, "w", encoding="utf-8") as f:
            f.write(detail_html)

        card_inst_html = f"<span><strong>制度名:</strong> {inst_name}</span> | " if inst_name and str(inst_name).strip().lower() not in ["none", "null", ""] else ""
        html_content += f"""
        <div class="card">
            <div class="title"><a href="{detail_filename}">{title}</a></div>
            <div class="meta">
                {card_inst_html}
                <span><strong>対象地域:</strong> <span class="tag">{target_area}</span></span>
                <span><strong>受付終了日:</strong> {end_date}</span>
            </div>
        </div>"""

    html_content += """
    </div>
</body>
</html>"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("サイト生成処理が正常に完了しました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
