from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import random
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/news')
def news():
    return render_template('news.html')

if __name__ == '__main__':
    app.run(debug=True)
app = Flask(__name__)
app.config['SECRET_KEY'] = '030-18-007'
socketio = SocketIO(app)

# SQLiteデータベースの初期設定
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# テーブル作成
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, email TEXT, balance REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS companies
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, stock_price REAL)''')
c.execute('''CREATE TABLE IF NOT EXISTS events
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, effect REAL)''')

# 初期データ挿入（例として5社の株と初期イベントを追加）
c.execute("INSERT INTO companies (name, stock_price) VALUES ('Company A', 100.0)")
c.execute("INSERT INTO companies (name, stock_price) VALUES ('Company B', 200.0)")
c.execute("INSERT INTO companies (name, stock_price) VALUES ('Company C', 150.0)")
c.execute("INSERT INTO companies (name, stock_price) VALUES ('Company D', 180.0)")
c.execute("INSERT INTO companies (name, stock_price) VALUES ('Company E', 220.0)")

# ランダムなイベントの生成
def generate_random_event():
    event_name = f"Event_{random.randint(1, 100)}"
    effect = random.uniform(-20.0, 20.0)
    c.execute("INSERT INTO events (name, effect) VALUES (?, ?)", (event_name, effect))
    conn.commit()
    return event_name, effect

# ランダムな株価変動のシミュレーション
def simulate_stock_prices():
    while True:
        company_ids = [row[0] for row in c.execute("SELECT id FROM companies")]
        for company_id in company_ids:
            # ランダムに株価を変動させる
            random_change = random.uniform(-10.0, 10.0)
            c.execute("UPDATE companies SET stock_price = stock_price + ? WHERE id = ?", (random_change, company_id))
            conn.commit()
            # フロントエンドに新しい株価を送信
            socketio.emit('update_stock_price', {'company_id': company_id, 'new_price': c.execute("SELECT stock_price FROM companies WHERE id = ?", (company_id,)).fetchone()[0]})
        
        # ランダムなイベントを発生させる（2週間に1回程度の頻度）
        if random.random() < 0.5:  # 約2週間に1回の割合でイベントを生成
            event_name, effect = generate_random_event()
            socketio.emit('update_event', {'event_name': event_name, 'effect': effect})
        
        # 10秒ごとに株価変動を発生させる
        socketio.sleep(10)

# モデレータ権限を持つユーザの検証
def is_moderator(user_id):
    # ここでは仮にユーザIDが1の場合がモデレータとして扱う例
    return user_id == 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('trade'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        c.execute("INSERT INTO users (username, password, email, balance) VALUES (?, ?, ?, 10000.0)", (username, password, email))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/trade')
def trade():
    if 'user_id' in session:
        companies = c.execute("SELECT * FROM companies").fetchall()
        return render_template('trade.html', companies=companies)
    return redirect(url_for('login'))

@app.route('/moderator')
def moderator():
    if 'user_id' in session and is_moderator(session['user_id']):
        events = c.execute("SELECT * FROM events").fetchall()
        return render_template('moderator.html', events=events)
    return redirect(url_for('login'))

@app.route('/ban_user/<int:user_id>')
def ban_user(user_id):
    if is_moderator(session.get('user_id')):
        # ユーザをBanするロジックをここに実装
        return jsonify({'message': f'User with ID {user_id} has been banned.'})
    return jsonify({'message': 'You do not have permission to perform this action.'}), 403

@app.route('/suspend_trading/<int:user_id>')
def suspend_trading(user_id):
    if is_moderator(session.get('user_id')):
        # 取引を一時停止するロジックをここに実装
        return jsonify({'message': f'Trading for user with ID {user_id} has been suspended.'})
    return jsonify({'message': 'You do not have permission to perform this action.'}), 403

@socketio.on('connect')
def handle_connect():
    emit('update_stock_prices', [{'company_id': row[0], 'stock_price': row[2]} for row in c.execute("SELECT * FROM companies").fetchall()])
    emit('update_events', [{'event_name': row[1], 'effect': row[2]} for row in c.execute("SELECT * FROM events").fetchall()])

if __name__ == '__main__':
    socketio.start_background_task(target=simulate_stock_prices)
    socketio.run(app, debug=True)
# aああああ