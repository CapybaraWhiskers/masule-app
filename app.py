from flask import Flask, request, redirect, url_for, render_template
import sqlite3
from datetime import datetime
import calendar
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
    # exercises テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            muscle_group TEXT NOT NULL
        )
    ''')
    # workouts テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            exercise_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight INTEGER NOT NULL,
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
    # muscle_group も取得して行の色分けに使う
    workouts = conn.execute('''
        SELECT w.id, w.date, e.name AS exercise, e.muscle_group, w.sets, w.reps, w.weight
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        ORDER BY w.date DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', workouts=workouts)

@app.route('/edit_workout/<int:wid>', methods=['GET', 'POST'])
def edit_workout(wid):
    conn = get_db_connection()
    if request.method == 'POST':
        exercise_id = int(request.form['exercise_id'])
        date = request.form['date']
        sets = int(request.form['sets'])
        reps = int(request.form['reps'])
        weight = int(request.form['weight'])
        conn.execute(
            'UPDATE workouts SET exercise_id=?, date=?, sets=?, reps=?, weight=? WHERE id=?',
            (exercise_id, date, sets, reps, weight, wid)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    workout = conn.execute('SELECT * FROM workouts WHERE id = ?', (wid,)).fetchone()
    exercises = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('edit_workout.html', workout=workout, exercises=exercises)

@app.route('/delete_workout/<int:wid>', methods=['POST'])
def delete_workout(wid):
    conn = get_db_connection()
    conn.execute('DELETE FROM workouts WHERE id = ?', (wid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    conn = get_db_connection()
    if request.method == 'POST':
        # 新規登録 or 削除判定
        if 'delete_id' in request.form:
            delete_id = int(request.form['delete_id'])
            conn.execute('DELETE FROM exercises WHERE id = ?', (delete_id,))
            conn.commit()
            conn.close()
            return redirect(url_for('exercises'))

        # 新規エクササイズ追加
        name = request.form['name'].strip()
        muscle = request.form['muscle_group']
        if name:
            conn.execute(
                'INSERT INTO exercises (name, muscle_group) VALUES (?, ?)',
                (name, muscle)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('exercises'))

    sort = request.args.get('sort', 'new')
    muscle = request.args.get('muscle', '')
    query = 'SELECT * FROM exercises'
    params = []
    if muscle:
        query += ' WHERE muscle_group = ?'
        params.append(muscle)
    if sort == 'old':
        query += ' ORDER BY id ASC'
    else:
        query += ' ORDER BY id DESC'

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('exercises.html', exercises=rows, sort=sort, muscle=muscle)

@app.route('/log', methods=['GET', 'POST'])
def log():
    conn = get_db_connection()
    if request.method == 'POST':
        # トレーニングログ登録（複数行対応）
        date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')
        exercise_ids = request.form.getlist('exercise_id')
        sets_list = request.form.getlist('sets')
        reps_list = request.form.getlist('reps')
        weight_list = request.form.getlist('weight')
        for ex, st, rp, wt in zip(exercise_ids, sets_list, reps_list, weight_list):
            conn.execute(
                'INSERT INTO workouts (exercise_id, date, sets, reps, weight) VALUES (?, ?, ?, ?, ?)',
                (int(ex), date, int(st), int(rp), int(wt))
            )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET時：エクササイズ一覧をプルダウン表示
    exercises = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('log.html', exercises=exercises)

@app.route('/calendar')
def calendar_view():
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT w.date, e.muscle_group
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
    ''').fetchall()
    conn.close()
    events = {}
    for r in rows:
        day_events = events.setdefault(r['date'], set())
        day_events.add(r['muscle_group'])

    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    if not year or not month:
        now = datetime.now()
        year = now.year
        month = now.month
    cal = calendar.Calendar()
    month_days = cal.monthdatescalendar(year, month)
    today = datetime.now().date()

    # previous and next month calculations
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    return render_template('calendar.html', events=events, days=month_days,
                           year=year, month=month, today=today,
                           prev_year=prev_year, prev_month=prev_month,
                           next_year=next_year, next_month=next_month)


@app.route('/day/<date>')
def day_detail(date):
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT w.date, e.name, e.muscle_group, w.sets, w.reps, w.weight
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        WHERE w.date = ?
        ORDER BY w.id ASC
    ''', (date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', workouts=rows, date=date)

if __name__ == '__main__':
    app.run(debug=True)
