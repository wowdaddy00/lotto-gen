from flask import Flask
import random

app = Flask(__name__)

@app.route("/")
def home():
    numbers = sorted(random.sample(range(1, 46), 6))
    numbers_str = " - ".join(map(str, numbers))
    return f"""
    <html>
      <head><title>로또 번호 추천기</title></head>
      <body style='text-align:center;font-family:sans-serif;margin-top:50px;'>
        <h1>🎲 오늘의 로또 번호 🎲</h1>
        <h2 style='color:blue;'>{numbers_str}</h2>
      </body>
    </html>
    """
