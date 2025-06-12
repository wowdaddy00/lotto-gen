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
            body { font-family: sans-serif; text-align: center; margin-top: 100px; }
            h1 { font-size: 28px; }
            p { color: gray; }
            a { text-decoration: none; color: gray; font-size: 14px; }
        </style>
    </head>
    <body>
        <h1>🚧 제외 조건 설정 기능은 준비 중입니다</h1>
        <p>다음 단계에서 필터 기능을 붙일 예정이에요!</p>
        <br>
        <a href="/">← 홈으로 돌아가기</a>
    </body>
    </html>
    """)
