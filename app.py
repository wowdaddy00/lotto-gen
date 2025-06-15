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

def make_tuple_list(rank_list):
    # 각 조합을 정렬하여 tuple로 변환 (순서 무관 비교용)
    return [tuple(sorted(row)) for row in rank_list]

@app.route("/")
def home():
    return render_template_string("""
    <html><body style='text-align:center; font-family:sans-serif; margin-top:50px;'>
        <h1>🎲 LottoGen에 오신 걸 환영합니다 🎲</h1>
        <a href="/generate">무료 로또 번호 생성</a><br><br>
        <a href="/generate-hot10">최근 10주 인기번호 추천</a><br><br>
        <a href="/filter">제외 조합 설정하기</a><br><br>
        <a href="/stats">출현 통계 보기</a>
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

    # 회차 필터용 함수 (슬라이스)
    def filter_by_range(rank_list):
        if range_option == "recent10":
            return rank_list[-10:]
        elif range_option == "recent50":
            return rank_list[-50:]
        elif range_option == "recent100":
            return rank_list[-100:]
        else:
            return rank_list

    # ★ 핵심: 회차 옵션별 당첨조합 추출 & tuple로 변환
    rank1 = make_tuple_list(filter_by_range(WINNING["rank1"]))
    rank2 = make_tuple_list(filter_by_range(WINNING["rank2"]))
    rank3 = make_tuple_list(filter_by_range(WINNING["rank3"]))

    def is_valid(numbers):
        numbers = sorted(numbers)
        # 연속번호 필터
        seq, max_seq = 1, 1
        for i in range(1, len(numbers)):
            if numbers[i] == numbers[i-1] + 1:
                seq += 1
                max_seq = max(max_seq, seq)
            else:
                seq = 1
        if no_2seq and max_seq >= 2: return False
        if no_3seq and max_seq >= 3: return False
        if no_4seq and max_seq >= 4: return False

        # 직접 제외번호
        if any(n in numbers for n in exclude_nums): return False

        # ★ 핵심: 조합 제외 (tuple 비교, 순서 무관)
        t_numbers = tuple(numbers)
        if exclude_1st and t_numbers in rank1: return False
        if exclude_2nd and t_numbers in rank2: return False
        if exclude_3rd and t_numbers in rank3: return False
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

    # 결과 부족 안내
    message = ""
    if len(results) < count:
        message = f"⚠️ 필터 조건이 너무 많거나 추천 개수({count}개)를 만족하지 못했습니다. {len(results)}개만 추천됩니다."

    return render_template_string("""
    <head>
        <style>
            body { text-align:center; font-family:sans-serif; margin-top:50px; }
            .lotto { font-size: 20px; color: blue; }
            .copy-btn { margin-left: 10px; padding: 5px 10px; font-size: 14px; }
            .msg { color: red; margin-top: 20px; font-weight: bold; }
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
        {% if message %}
            <div class='msg'>{{ message }}</div>
        {% endif %}
        <br><a href="/">← 홈으로</a>
    </body>
    </html>
    """, results=results, message=message)

@app.route("/filter")
def filter():
    return render_template_string("""
   <html>
    <head>
        <title>제외 조건 설정</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin: 50px; }
            h1 { font-size: 26px; margin-bottom: 30px; }
            form { display: inline-block; text-align: left; }
            label { font-weight: bold; display: block; margin-top: 20px; }
            input[type='number'] { width: 60px; margin: 5px; }
            input[type='checkbox'] { margin-right: 5px; }
            select { padding: 5px; margin-top: 10px; }
            button { margin-top: 30px; padding: 10px 20px; font-size: 16px; }
        </style>
    </head>
    <body>
        <h1>🎯 로또 번호 제외 조건 설정</h1>
        <form action="/generate" method="GET">
            <label>✅ 제외할 당첨조합</label>
            <input type="checkbox" name="exclude_1st" checked> 1등 조합 제외<br>
            <input type="checkbox" name="exclude_2nd"> 2등 조합 제외<br>
            <input type="checkbox" name="exclude_3rd"> 3등 조합 제외<br>

            <label>⚠️ 연속번호 제외</label>
            <input type="checkbox" name="no_2seq"> 2연속 제외<br>
            <input type="checkbox" name="no_3seq" checked> 3연속 제외<br>
            <input type="checkbox" name="no_4seq"> 4연속 이상 제외<br>

            <label>🔒 고정하고 싶은 번호 (1~45)</label>
            <input type="number" name="fixed1" min="1" max="45">
            <input type="number" name="fixed2" min="1" max="45">
            <input type="number" name="fixed3" min="1" max="45">
            <input type="number" name="fixed4" min="1" max="45">
            <input type="number" name="fixed5" min="1" max="45">

            <h3>제외할 번호 직접 입력</h3>
            {% for i in range(1, 7) %}
                <input type="number" name="exclude{{i}}" min="1" max="45">
            {% endfor %}

            <h3>회차 범위 설정</h3>
            <select name="range_option">
                <option value="all">전체</option>
                <option value="recent100">최근 100회</option>
                <option value="recent50">최근 50회</option>
                <option value="recent10">최근 10회</option>
            </select><br>

            <label>🔢 추천 조합 개수</label>
            <select name="count">
                <option value="1">1개</option>
                <option value="5">5개</option>
                <option value="10">10개</option>
                <option value="20">20개</option>
            </select>

            <br>
            <button type="submit">🎰 번호 추천받기</button>
        </form>
        <br><br>
        <a href="/">← 홈으로 돌아가기</a>
    </body>
    </html>
    """)

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

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/generate-hot10")
def generate_hot10():
    try:
        with open(WINNING_PATH, encoding='utf-8') as f:
            data = json.load(f)
    except:
        return "데이터를 불러오지 못했습니다."

    # 최근 10회차의 1등 번호만 추출
    recent_10 = data["rank1"][-10:]
    flat = [num for sublist in recent_10 for num in sublist]

    # 출현 빈도 계산
    from collections import Counter
    counts = Counter(flat)
    top_numbers = [num for num, _ in counts.most_common(12)]

    # 5개 조합 생성
    results = []
    attempts = 0
    while len(results) < 5 and attempts < 1000:
        combo = sorted(random.sample(top_numbers, 6))
        if combo not in results:
            results.append(combo)
        attempts += 1

    return render_template_string("""
    <html><body style='text-align:center; font-family:sans-serif; margin-top:50px;'>
        <h1>🔥 최근 10주 인기번호 기반 추천</h1>
        {% for row in results %}
            <p style='color:red;'>{{ row|join(' - ') }}</p>
        {% endfor %}
        <br><a href="/">← 홈으로</a>
    </body></html>""", results=results)
