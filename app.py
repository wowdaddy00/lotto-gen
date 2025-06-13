from flask import Flask, render_template_string, request
import random, json, os

app = Flask(__name__)

# JSON 파일 경로 (1등, 2등, 3등 모두 포함)
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
    </body></html>""")

@app.route("/generate")
def generate():
    exclude_1st = request.args.get("exclude_1st") == "on"
    exclude_2nd = request.args.get("exclude_2nd") == "on"
    exclude_3rd = request.args.get("exclude_3rd") == "on"
    no_2seq = request.args.get("no_2seq") == "on"
    no_3seq = request.args.get("no_3seq") == "on"
    no_4seq = request.args.get("no_4seq") == "on"
    range_limit = request.args.get("range_limit", "all")

    # 고정 번호 입력
    fixed = []
    for i in range(1, 6):
        val = request.args.get(f"fixed{i}")
        if val and val.isdigit():
            fixed.append(int(val))

    count = int(request.args.get("count", 1))
    results = []

    # 회차 제한 필터링
    def filter_by_range(data):
        if range_limit == "all":
            return data
        try:
            limit = int(range_limit)
            return data[-limit:]
        except:
            return data

    # 조합 검증 함수
    def is_valid(numbers):
        numbers = sorted(numbers)
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
    <html><body style='text-align:center; font-family:sans-serif; margin-top:50px;'>
        <h1>🎰 추천 로또 번호</h1>
        {% for row in results %}
            <p style='color:blue;'>{{ row|join(' - ') }}</p>
        {% endfor %}
        <br><a href="/">← 홈으로</a>
    </body></html>""", results=results)

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

            <h3>고정 번호 입력</h3>
            {% for i in range(1, 6) %}
                <input type="number" name="fixed{{i}}" min="1" max="45">
            {% endfor %}

            <h3>추천 개수</h3>
            <select name="count">
                <option value="1">1개</option>
                <option value="5">5개</option>
                <option value="10">10개</option>
            </select><br>

            <h3>제외할 회차 범위</h3>
            <select name="range_limit">
                <option value="all">전체</option>
                <option value="100">최근 100회</option>
                <option value="50">최근 50회</option>
                <option value="10">최근 10회</option>
            </select><br><br>

            <button type="submit">추천 번호 받기</button>
        </form>
        <br><a href="/">← 홈으로</a>
    </body></html>""")
