from flask import Flask, render_template_string, request
import random, json, os

app = Flask(__name__)

# JSON 파일 불러오기
WINNING_PATH = os.path.join(os.path.dirname(__file__), 'static', 'winning_numbers_full.json')
try:
    with open(WINNING_PATH, encoding='utf-8') as f:
        WINNING = json.load(f)
except:
    WINNING = {"rank1": [], "rank2": [], "rank3": []}

@app.route("/")
def home():
    return render_template_string("""
    <html><body style='text-align:center; font-family:sans-serif; margin-top:50px;'>
        <h1>🎲 LottoGen에 오신 걸 환영합니다 🎲</h1>
        <a href="/generate">무료 로또 번호 생성</a><br><br>
        <a href="/filter">제외 조합 설정하기</a>
        <a href="/stats">출현 통계 보기</a><br><br>
    </body></html>""")

@app.route("/generate")
def generate():
    exclude_1st = request.args.get("exclude_1st") == "on"
    exclude_2nd = request.args.get("exclude_2nd") == "on"
    exclude_3rd = request.args.get("exclude_3rd") == "on"
    no_2seq = request.args.get("no_2seq") == "on"
    no_3seq = request.args.get("no_3seq") == "on"
    no_4seq = request.args.get("no_4seq") == "on"
    range_option = request.args.get("range_option", "all")

    fixed = []
    for i in range(1, 6):
        val = request.args.get(f"fixed{i}")
        if val and val.isdigit():
            fixed.append(int(val))

    exclude_nums = []
    for i in range(1, 7):
        val = request.args.get(f"exclude{i}")
        if val and val.isdigit():
            exclude_nums.append(int(val))

    count = int(request.args.get("count", 1))
    results = []

    # 회차 필터용 함수
    def filter_by_range(rank_list):
        if range_option == "recent10":
            return rank_list[-10:]
        elif range_option == "recent50":
            return rank_list[-50:]
        elif range_option == "recent100":
            return rank_list[-100:]
        else:
            return rank_list

    def is_valid(numbers):
        numbers = sorted(numbers)

        # 연속번호 필터
        seq, max_seq = 1, 1
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i - 1] + 1:
                seq += 1
                max_seq = max(max_seq, seq)
            else:
                seq = 1
        if no_2seq and max_seq >= 2: return False
        if no_3seq and max_seq >= 3: return False
        if no_4seq and max_seq >= 4: return False

        # 사용자 직접 제외번호 포함 시 제외
        if any(n in numbers for n in exclude_nums): return False

        # 1~3등 당첨 조합 필터
        if exclude_1st and numbers in filter_by_range(WINNING["rank1"]): return False
        if exclude_2nd and numbers in filter_by_range(WINNING["rank2"]): return False
        if exclude_3rd and numbers in filter_by_range(WINNING["rank3"]): return False

        return True

    attempts = 0
    while len(results) < count and attempts < 10000:
        attempts += 1
        nums = set(fixed)
        while len(nums) < 6:
            nums.add(random.randint(1, 45))
        nums = sorted(nums)
        if is_valid(nums) and nums not in results:
            results.append(nums)

    return render_template_string("""
    <html>
    <head>
        <style>
            body { text-align:center; font-family:sans-serif; margin-top:50px; }
            .lotto { font-size: 20px; color: blue; }
            .copy-btn { margin-left: 10px; padding: 5px 10px; font-size: 14px; }
        </style>
        <script>
            function copyToClipboard(text) {
                navigator.clipboard.writeText(text).then(function() {
                    alert("복사되었습니다: " + text);
                });
            }
        </script>
    </head>
    <body>
        <h1>🎰 추천 로또 번호</h1>
        {% for row in results %}
            <p class='lotto'>
                {{ row|join(' - ') }}
                <button class='copy-btn' onclick="copyToClipboard('{{ row|join(' - ') }}')">복사</button>
            </p>
        {% endfor %}
        <br><a href="/">← 홈으로</a>
    </body>
    </html>
    """, results=results)

@app.route("/filter")
def filter():
    return render_template_string("""
    <html><body style='text-align:center;font-family:sans-serif;margin-top:30px;'>
        <h1>🎯 로또 번호 제외 조건 설정</h1>
        <form action="/generate" method="get">
            <h3>당첨번호 제외</h3>
            <input type="checkbox" name="exclude_1st" checked> 1등 제외<br>
            <input type="checkbox" name="exclude_2nd"> 2등 제외<br>
            <input type="checkbox" name="exclude_3rd"> 3등 제외<br>

            <h3>연속번호 제외</h3>
            <input type="checkbox" name="no_2seq"> 2연속 제외<br>
            <input type="checkbox" name="no_3seq" checked> 3연속 제외<br>
            <input type="checkbox" name="no_4seq"> 4연속 이상 제외<br>

            <h3>제외할 번호 직접 입력</h3>
            {% for i in range(1, 7) %}
                <input type="number" name="exclude{{i}}" min="1" max="45">
            {% endfor %}

            <h3>고정 번호 입력</h3>
            {% for i in range(1, 6) %}
                <input type="number" name="fixed{{i}}" min="1" max="45">
            {% endfor %}

            <h3>회차 범위 설정</h3>
            <select name="range_option">
                <option value="all">전체</option>
                <option value="recent100">최근 100회</option>
                <option value="recent50">최근 50회</option>
                <option value="recent10">최근 10회</option>
            </select><br>

            <h3>추천 개수</h3>
            <select name="count">
                <option value="1">1개</option>
                <option value="5">5개</option>
                <option value="10">10개</option>
            </select><br><br>

            <button type="submit">추천 번호 받기</button>
        </form>
        <br><a href="/">← 홈으로</a>
    </body></html>""")

@app.route("/stats")
def stats():
    try:
        WINNING_PATH = os.path.join(os.path.dirname(__file__), 'static', 'winning_numbers_full.json')
        with open(WINNING_PATH, encoding='utf-8') as f:
            data = json.load(f)
    except:
        return "통계 데이터를 불러오지 못했습니다."

    all_numbers = data["rank1"] + data["rank2"] + data["rank3"]
    flattened = [num for sublist in all_numbers for num in sublist]
    counts = {i: flattened.count(i) for i in range(1, 46)}

    table_html = "<table border='1' style='margin:auto; text-align:center;'>"
    table_html += "<tr><th>번호</th><th>출현 횟수</th></tr>"
    for number, count in sorted(counts.items()):
        table_html += f"<tr><td>{number}</td><td>{count}</td></tr>"
    table_html += "</table>"

    return render_template_string(f"""
    <html><body style='font-family:sans-serif; text-align:center; margin-top:40px;'>
        <h1>📊 로또 번호 출현 통계</h1>
        {table_html}
        <br><a href="/">← 홈으로</a>
    </body></html>""")
