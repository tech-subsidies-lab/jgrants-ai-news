import json
import urllib.parse
import urllib.request

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

    subsidies = data.get("result", [])

    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公募中の補助金一覧</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f8f9fa; color: #333; }
        .container { max-width: 900px; margin: 0 auto; }
        h1 { font-size: 1.8em; margin-bottom: 20px; color: #1a252f; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }
        .card { background: #fff; border: 1px solid #e1e4e8; padding: 20px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
        .title { font-size: 1.2em; font-weight: bold; margin-bottom: 10px; }
        .title a { color: #0056b3; text-decoration: none; }
        .title a:hover { text-decoration: underline; }
        .meta { font-size: 0.88em; color: #586069; display: flex; flex-wrap: wrap; gap: 15px; align-items: center; }
        .tag { background: #e1f5fe; color: #0288d1; padding: 2px 8px; border-radius: 4px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="container">
        <h1>現在募集中の補助金一覧</h1>
"""

    if not subsidies:
        html_content += "        <p>該当する補助金は見つかりませんでした。</p>\n"
    else:
        for item in subsidies:
            subsidy_id = item.get("id", "")
            title = item.get("title", "名称なし")
            inst_name = item.get("institution_name")
            target_area = item.get("target_area_search", "全国")
            end_date = item.get("acceptance_end_datetime", "不明")

            detail_url = f"https://www.jgrants-portal.go.jp/subsidy/{subsidy_id}" if subsidy_id else "#"

            if end_date != "不明" and "T" in end_date:
                end_date = end_date.split("T")[0]

            inst_html = f"<span><strong>制度名:</strong> {inst_name}</span> | " if inst_name else ""

            html_content += f"""
        <div class="card">
            <div class="title"><a href="{detail_url}" target="_blank" rel="noopener">{title}</a></div>
            <div class="meta">
                {inst_html}
                <span><strong>対象地域:</strong> <span class="tag">{target_area}</span></span>
                <span><strong>受付終了日:</strong> {end_date}</span>
            </div>
        </div>"""

    html_content += """
    </div>
</body>
</html>
"""

    output_path = "index.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"成功: {len(subsidies)} 件のデータを取得し、{output_path} に保存しました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
