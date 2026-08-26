import json
import urllib.parse
import urllib.request
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
BASE_URL = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"

def generate_ai_text(prompt):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "<p>※Gemini APIキーを設定すると、ここにAIによる詳細解説文が自動生成されます。</p>"
    
    # 2026年現在の安定エンドポイント (gemini-2.0-flash)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=15) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "<p>AI解説の生成中にエラーが発生しました。</p>"

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

    subsidies = data.get("result", [])

    ad_code = """
    <div class="ad-banner" style="text-align: center; margin: 25px 0;">
        <a href="https://px.a8.net/svt/ejp?a8mat=4BAEXG+8FN3AQ+4JGQ+C3J0H" rel="nofollow">
        <img border="0" width="336" height="280" alt="" src="https://www29.a8.net/svt/bgt?aid=260826388510&wid=001&eno=01&mid=s00000021185002032000&mc=1"></a>
        <img border="0" width="1" height="1" src="https://www15.a8.net/0.gif?a8mat=4BAEXG+8FN3AQ+4JGQ+C3J0H" alt="">
    </div>
    """

    html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公募中の補助金一覧</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; color: #333; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 1.8em; margin-bottom: 20px; color: #1a252f; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
        .card {{ background: #fff; border: 1px solid #e1e4e8; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }}
        .title {{ font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }}
        .title a {{ color: #0056b3; text-decoration: none; }}
        .title a:hover {{ text-decoration: underline; }}
        .meta {{ font-size: 0.88em; color: #586069; display: flex; flex-wrap: wrap; gap: 15px; align-items: center; }}
        .tag {{ background: #e1f5fe; color: #0288d1; padding: 2px 8px; border-radius: 4px; font-weight: 500; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>現在募集中の補助金一覧</h1>
        {ad_code}
"""

    for item in subsidies:
        subsidy_id = item.get("id", "")
        title = item.get("title", "名称なし")
        inst_name = item.get("institution_name", "")
        target_area = item.get("target_area_search", "全国")
        end_date = item.get("acceptance_end_datetime", "不明")
        target_summary = item.get("target_summary", "詳細情報は公募要領をご確認ください。")

        if end_date != "不明" and "T" in end_date:
            end_date = end_date.split("T")[0]

        detail_filename = f"subsidy-{subsidy_id}.html"

        prompt = f"補助金名「{title}」の概要です：「{target_summary}」。この記事について、どんな企業や事業者におすすめか、申請するメリットを簡潔にわかりやすく日本語HTMLタグ（<h3>, <p>, <ul>等）を含めて解説してください。"
        ai_article = generate_ai_text(prompt)

        detail_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - 詳細解説</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        h1 {{ font-size: 1.6em; color: #1a252f; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
        .back-link {{ display: inline-block; margin-bottom: 20px; color: #0056b3; text-decoration: none; }}
        .meta-box {{ background: #e1f5fe; padding: 15px; border-radius: 6px; margin: 20px 0; }}
        .btn {{ display: inline-block; background: #0056b3; color: #fff; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-top: 15px; }}
    </style>
</head>
<body>
    <div class="container">
        <a href="index.html" class="back-link">← 一覧に戻る</a>
        <h1>{title}</h1>
        
        {ad_code}

        <div class="meta-box">
            <p><strong>制度名:</strong> {inst_name}</p>
            <p><strong>対象地域:</strong> {target_area}</p>
            <p><strong>受付終了日:</strong> {end_date}</p>
        </div>

        <h2>AIによるポイント解説</h2>
        {ai_article}

        {ad_code}

        <p style="text-align: center;">
            <a href="https://www.jgrants-portal.go.jp/subsidy/{subsidy_id}" target="_blank" rel="noopener" class="btn">jGrantsで公式申請ページを見る</a>
        </p>

        {ad_code}
    </div>
</body>
</html>"""

        with open(detail_filename, "w", encoding="utf-8") as f:
            f.write(detail_html)

        inst_html = f"<span><strong>制度名:</strong> {inst_name}</span> | " if inst_name else ""
        html_content += f"""
        <div class="card">
            <div class="title"><a href="{detail_filename}">{title}</a></div>
            <div class="meta">
                {inst_html}
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

    print("個別ページおよび一覧ページの自動作成が完了しました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
