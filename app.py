import json
import os
import re
from string import Template
import time
import urllib.parse
import urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE")
BASE_URL = "https://api.jgrants-portal.go.jp/exp/v1/public/subsidies"

MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-3.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-flash-latest",
]


def load_template(filename):
    path = os.path.join("templates", filename)
    with open(path, "r", encoding="utf-8") as f:
        return Template(f.read())


def format_subsidy_data(subsidy_max_raw, subsidy_rate_raw):
    """補助上限額と補助率を判定し、フォーマット済みテキストとカード用バッジを生成"""
    # 1. 補助上限額の判定
    amount_text = "公募要領をご確認ください"
    amount_badge = ""

    if subsidy_max_raw and str(subsidy_max_raw).lower() != "none":
        digits_only = re.sub(r"[^\d]", "", str(subsidy_max_raw))
        if digits_only:
            val = int(digits_only)
            if val >= 100000000:
                oku = val / 100000000
                formatted = (
                    f"{int(oku)}億円" if oku.is_integer() else f"{oku:.1f}億円"
                )
            elif val >= 10000:
                man = val / 10000
                formatted = (
                    f"{int(man)}万円" if man.is_integer() else f"{man:.1f}万円"
                )
            else:
                formatted = f"{val:,}円"

            amount_text = f"最大 {formatted}"
            amount_badge = f'<span class="price-tag">💰 上限: {formatted}</span>'

    # 2. 補助率の判定
    rate_text = "公募要領をご確認ください"
    rate_badge = ""

    if subsidy_rate_raw and str(subsidy_rate_raw).lower() != "none":
        raw_str = str(subsidy_rate_raw).strip()
        if "参照" not in raw_str and "確認" not in raw_str:
            rate_text = raw_str
            rate_badge = f'<span class="rate-tag">📊 補助率: {raw_str}</span>'

    return amount_text, amount_badge, rate_text, rate_badge


def generate_ai_text(prompt, retries=2):
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "<p>※Gemini APIキーを設定すると、ここにAIによる詳細解説文が自動生成されます。</p>"

    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for model_name in MODEL_CANDIDATES:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

        for attempt in range(retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers=headers,
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    return res_data["candidates"][0]["content"]["parts"][0][
                        "text"
                    ]
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait_time = 20 * (attempt + 1)
                    print(
                        f"[{model_name}] 429 Rate Limit。{wait_time}秒待機して再試行..."
                    )
                    time.sleep(wait_time)
                elif e.code == 404:
                    print(
                        f"[{model_name}] 404 エラー。次のモデルに切り替えます..."
                    )
                    break
                else:
                    time.sleep(3)
            except Exception:
                time.sleep(3)

    return "<p>AI解説の生成中にエラーが発生しました。</p>"


params = {
    "keyword": "IT",
    "acceptance": "1",
    "sort": "created_date",
    "order": "DESC",
}

try:
    index_template = load_template("index_template.html")
    detail_template = load_template("detail_template.html")

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

    toc_items_list = []
    cards_html_list = []

    for item in subsidies:
        subsidy_id = item.get("id", "")
        title = item.get("title", "名称なし")
        inst_name = item.get("institution_name", "")
        target_area = item.get("target_area_search", "全国")
        end_date = item.get("acceptance_end_datetime", "不明")
        target_summary = item.get("target_summary", "")

        # 補助上限額と補助率を取得
        subsidy_max_raw = item.get("subsidy_max", "")
        subsidy_rate_raw = item.get("subsidy_rate", "")

        amount_text, amount_badge, rate_text, rate_badge = format_subsidy_data(
            subsidy_max_raw, subsidy_rate_raw
        )

        if end_date != "不明" and "T" in end_date:
            end_date = end_date.split("T")[0]

        detail_filename = f"subsidy-{subsidy_id}.html"

        print(f"生成中: {title[:20]}...")

        prompt = f"""
補助金「{title}」（概要：{target_summary}）についてのWeb解説記事を作成してください。
以下の構成で、指定のマークアップタグを用いて出力してください。

---
【1. お悩みリスト】
この補助金の対象者（企業・事業者）が抱えていそうな具体的なお悩みを3つ作成し、以下の形式で出力してください。
<PAIN_POINTS>
- 悩み1
- 悩み2
- 悩み3
</PAIN_POINTS>

【2. 解説本文】
以下の3セクション構成で、HTMLタグ（<p>, <h3>, <ul>, <li>）を用いてまとめて出力してください。
・【はじめに】: 読者の関心を引き、どのような補助金かを簡潔に解説（<p>2〜3文）
・【詳細解説】: どのような企業・事業者におすすめか、申請・導入のメリット、活用事例を具体的に解説（<h3>や<ul>を使用）
・【まとめ】: 申請に向けた注意点やアドバイス（<p>2〜3文）
---

出力は上記のタグ・HTML部分のみにしてください。
"""
        raw_response = generate_ai_text(prompt)
        time.sleep(4)

        pain_points_html = "<li>IT導入や事業課題の解決を目指している</li><li>申請に活用できる補助金情報を探している</li><li>費用の負担を軽減してDX化を進めたい</li>"
        ai_article = raw_response

        if "<PAIN_POINTS>" in raw_response and "</PAIN_POINTS>" in raw_response:
            parts = raw_response.split("</PAIN_POINTS>")
            pain_block = parts[0].replace("<PAIN_POINTS>", "").strip()
            ai_article = parts[1].strip()

            items = [
                line.strip("- ").strip()
                for line in pain_block.split("\n")
                if line.strip()
            ]
            if len(items) >= 3:
                pain_points_html = "".join(
                    [f"<li>{item}</li>" for item in items[:3]]
                )

        plain_text = re.sub(r"<[^>]+>", "", ai_article).strip()
        plain_text = re.sub(r"\s+", " ", plain_text)
        short_summary = (
            plain_text[:110] + "..." if len(plain_text) > 110 else plain_text
        )

        clean_summary = (
            target_summary.replace("<", "")
            .replace(">", "")
            .replace("\n", "")
            .strip()
        )
        meta_desc = f"{title}（{amount_text}）の概要・活用メリット・申請手順を解説。{clean_summary[:90]}..."

        inst_html_detail = ""
        inst_html_card = ""
        if inst_name and inst_name.lower() != "none":
            inst_html_detail = (
                f"<p><strong>実施機関・制度名:</strong> {inst_name}</p>"
            )
            inst_html_card = (
                f"<span><strong>制度名:</strong> {inst_name}</span> | "
            )

        detail_html = detail_template.substitute(
            title=title,
            meta_desc=meta_desc,
            inst_html=inst_html_detail,
            target_area=target_area,
            end_date=end_date,
            amount_text=amount_text,
            rate_text=rate_text,
            subsidy_id=subsidy_id,
            pain_points_html=pain_points_html,
            ai_article=ai_article,
            ad_code=ad_code,
        )

        with open(detail_filename, "w", encoding="utf-8") as f:
            f.write(detail_html)

        toc_items_list.append(
            f'<li><a href="{detail_filename}">{title}</a></li>'
        )

        # バッジの組み込み
        badges_html = (
            f"{amount_badge} {rate_badge}".strip() + " | "
            if (amount_badge or rate_badge)
            else ""
        )

        cards_html_list.append(f"""
        <article class="card">
            <h3 class="card-title"><a href="{detail_filename}">{title}</a></h3>
            <div class="short-summary">💡 {short_summary}</div>
            <div class="meta">
                {inst_html_card}
                {badges_html}
                <span>対象地域: <span class="tag">{target_area}</span></span>
                <span>受付終了日: <span class="date-tag">{end_date}</span></span>
            </div>
        </article>""")

    index_html = index_template.substitute(
        ad_code=ad_code,
        toc_items="\n".join(toc_items_list),
        cards_html="\n".join(cards_html_list),
    )

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)

    print("金額・補助率の自動判定ロジックを含む更新処理が正常に完了しました。")

except Exception as e:
    print(f"エラーが発生しました: {e}")
