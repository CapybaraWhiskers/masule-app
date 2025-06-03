from flask import Flask, request, redirect, url_for, render_template
import sqlite3
from datetime import datetime
import random
import os
app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'train.db')
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            muscle_group TEXT NOT NULL
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            exercise_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            FOREIGN KEY(exercise_id) REFERENCES exercises(id)
        )
    ''')
    conn.commit()
    conn.close()
# アプリ起動時にDB初期化
init_db()
@app.route('/')
def index():
    conn = get_db_connection()
    workouts = conn.execute('''
        SELECT w.date, e.name AS exercise, w.sets, w.reps, w.weight
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        ORDER BY w.date DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', workouts=workouts)
@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name'].strip()
        muscle = request.form['muscle_group']
        if name:
            conn.execute(
                'INSERT INTO exercises (name, muscle_group) VALUES (?, ?)',
                (name, muscle)
            )
            conn.commit()
        return redirect(url_for('exercises'))
    rows = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('exercises.html', exercises=rows)
@app.route('/log', methods=['GET', 'POST'])
def log():
    conn = get_db_connection()
    if request.method == 'POST':
        exercise_id = int(request.form['exercise_id'])
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')
        sets = int(request.form['sets'])
        reps = int(request.form['reps'])
        weight = float(request.form['weight'])
        conn.execute(
            'INSERT INTO workouts (exercise_id, date, sets, reps, weight) VALUES (?, ?, ?, ?, ?)',
            (exercise_id, date, sets, reps, weight)
        )
        conn.commit()
        return redirect(url_for('index'))
    exercises = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('log.html', exercises=exercises)
@app.route('/random')
def random_workout():
    conn = get_db_connection()
    exs = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    if not exs:
        return render_template('random.html', workout=None)
# 5種目までランダムにチョイス、各種目にセット数・回数をランダム設定
    sample = random.sample(exs, min(5, len(exs)))
    workout = [
        {
            'name': e['name'],
            'muscle_group': e['muscle_group'],
            'sets': random.randint(3, 5),
            'reps': random.choice([8, 10, 12, 15])
        }
        for e in sample
    ]
    return render_template('random.html', workout=workout)
if __name__ == '__main__':
    app.run(debug=True)
