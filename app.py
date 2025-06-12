from flask import Flask, render_template_string, request, redirect, url_for
import random

app = Flask(__name__)

@app.route("/")
def home():
    return render_template_string("""
    <html>
    <head>
        <title>LottoGen 홈</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 100px; }
            h1 { font-size: 30px; }
            a.button {
                display: inline-block;
                margin: 20px;
                padding: 15px 30px;
                font-size: 18px;
                text-decoration: none;
                background-color: #4CAF50;
                color: white;
                border-radius: 10px;
            }
        </style>
    </head>
    <body>
        <h1>🎲 LottoGen에 오신 걸 환영합니다 🎲</h1>
        <a href='/generate' class='button'>무료 로또 번호 생성</a>
        <a href='/filter' class='button'>제외 조합 설정하기</a>
    </body>
    </html>
    """)

@app.route("/generate")
def generate():
    numbers = sorted(random.sample(range(1, 46), 6))
    return render_template_string(f"""
    <html>
    <head>
        <title>로또 번호 생성</title>
        <style>
            body {{ font-family: sans-serif; text-align: center; margin-top: 100px; }}
            h1 {{ font-size: 30px; }}
            h2 {{ font-size: 26px; color: blue; }}
            a {{ text-decoration: none; color: gray; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>🎯 오늘의 로또 번호</h1>
        <h2>{' - '.join(map(str, numbers))}</h2>
        <br>
        <a href="/">← 홈으로 돌아가기</a>
    </body>
    </html>
    """)

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
