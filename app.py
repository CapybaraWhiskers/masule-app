from flask import Flask, request, redirect, url_for, render_template
import sqlite3
from datetime import datetime
import calendar
from flask import jsonify
import os

# -----------------------------
# Flask アプリの設定
# -----------------------------

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), 'train.db')

def get_db_connection():
    """SQLite データベースへ接続し、接続オブジェクトを返す"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 行を辞書のように扱えるよう設定
    return conn

def init_db():
    """必要なテーブルを作成し、既存のDBをアップデートする"""
    conn = get_db_connection()
    cur = conn.cursor()
    # exercises テーブルを作成
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            muscle_group TEXT NOT NULL,
            memo TEXT,
            video_url TEXT,
            default_sets INTEGER,
            default_reps INTEGER,
            default_weight REAL
        )
    ''')
    # 既存DBに必要な列が無ければ追加
    try:
        cur.execute('ALTER TABLE exercises ADD COLUMN memo TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('ALTER TABLE exercises ADD COLUMN video_url TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('ALTER TABLE exercises ADD COLUMN default_sets INTEGER')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('ALTER TABLE exercises ADD COLUMN default_reps INTEGER')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('ALTER TABLE exercises ADD COLUMN default_weight REAL')
    except sqlite3.OperationalError:
        pass
    # workouts テーブル
    cur.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            exercise_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            intensity TEXT,
            note TEXT,
            FOREIGN KEY(exercise_id) REFERENCES exercises(id)
        )
    ''')
    # 既存DBに列が無ければ追加
    try:
        cur.execute('ALTER TABLE workouts ADD COLUMN intensity TEXT')
    except sqlite3.OperationalError:
        pass
    try:
        cur.execute('ALTER TABLE workouts ADD COLUMN note TEXT')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

# アプリ起動時にDB初期化
init_db()

@app.route('/')
def index():
    """トップページ: トレーニング履歴を一覧表示"""
    conn = get_db_connection()
    # muscle_group も取得して行の色分けに使う
    workouts = conn.execute('''
        SELECT w.id, w.date, e.name AS exercise, e.muscle_group, w.sets, w.reps, w.weight, w.intensity
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        ORDER BY w.date DESC
    ''').fetchall()
    exercises = conn.execute('SELECT name FROM exercises ORDER BY name ASC').fetchall()
    conn.close()
    # DBの行オブジェクトを辞書に変換
    workout_list = [dict(w) for w in workouts]
    for w in workout_list:
        # 日付を短い形式に変換（失敗したらそのまま）
        try:
            dt = datetime.strptime(w['date'], '%Y-%m-%d')
            w['date_short'] = dt.strftime('%-m/%-d')
        except Exception:
            w['date_short'] = w['date']
    return render_template('index.html', workouts=workout_list, exercises=exercises)

@app.route('/edit_workout/<int:wid>', methods=['GET', 'POST'])
def edit_workout(wid):
    """指定IDのトレーニングログを編集"""
    conn = get_db_connection()
    if request.method == 'POST':
        exercise_id = int(request.form['exercise_id'])
        date = request.form['date']
        sets = int(request.form['sets'])
        reps = int(request.form['reps'])
        weight = float(request.form['weight'])
        intensity = request.form.get('intensity', '')
        note = request.form.get('note', '').strip()
        conn.execute(
            'UPDATE workouts SET exercise_id=?, date=?, sets=?, reps=?, weight=?, intensity=?, note=? WHERE id=?',
            (exercise_id, date, sets, reps, weight, intensity, note, wid)
        )
        conn.commit()
        conn.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ('', 204)
        return redirect(url_for('index'))

    workout = conn.execute('SELECT * FROM workouts WHERE id = ?', (wid,)).fetchone()
    exercises = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('edit_workout.html', workout=workout, exercises=exercises)

@app.route('/edit_workout_form/<int:wid>')
def edit_workout_form(wid):
    """編集用フォームだけを返す（モーダル表示用）"""
    conn = get_db_connection()
    workout = conn.execute('SELECT * FROM workouts WHERE id = ?', (wid,)).fetchone()
    exercises = conn.execute('SELECT * FROM exercises').fetchall()
    conn.close()
    return render_template('edit_workout_form.html', workout=workout, exercises=exercises)

@app.route('/delete_workout/<int:wid>', methods=['POST'])
def delete_workout(wid):
    """トレーニングログを削除"""
    conn = get_db_connection()
    conn.execute('DELETE FROM workouts WHERE id = ?', (wid,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/edit_exercise/<int:eid>', methods=['GET', 'POST'])
def edit_exercise(eid):
    """エクササイズ情報を編集"""
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name'].strip()
        muscle = request.form['muscle_group']
        memo = request.form.get('memo', '').strip()
        video_url = request.form.get('video_url', '').strip()
        default_sets = request.form.get('default_sets') or None
        default_reps = request.form.get('default_reps') or None
        default_weight = request.form.get('default_weight') or None
        if default_sets is not None and default_sets != '':
            default_sets = int(default_sets)
        else:
            default_sets = None
        if default_reps is not None and default_reps != '':
            default_reps = int(default_reps)
        else:
            default_reps = None
        if default_weight is not None and default_weight != '':
            default_weight = float(default_weight)
        else:
            default_weight = None
        conn.execute(
            'UPDATE exercises SET name=?, muscle_group=?, memo=?, video_url=?, default_sets=?, default_reps=?, default_weight=? WHERE id=?',
            (name, muscle, memo, video_url, default_sets, default_reps, default_weight, eid)
        )
        conn.commit()
        conn.close()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return ('', 204)
        return redirect(url_for('exercises'))

    exercise = conn.execute('SELECT * FROM exercises WHERE id=?', (eid,)).fetchone()
    conn.close()
    return render_template('edit_exercise.html', exercise=exercise)

@app.route('/edit_exercise_form/<int:eid>')
def edit_exercise_form(eid):
    """エクササイズ編集フォームのみを返す"""
    conn = get_db_connection()
    exercise = conn.execute('SELECT * FROM exercises WHERE id=?', (eid,)).fetchone()
    conn.close()
    return render_template('edit_exercise_form.html', exercise=exercise)

@app.route('/exercises', methods=['GET', 'POST'])
def exercises():
    """エクササイズ一覧および追加・削除画面"""
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
        memo = request.form.get('memo', '').strip()
        video_url = request.form.get('video_url', '').strip()
        default_sets = request.form.get('default_sets') or None
        default_reps = request.form.get('default_reps') or None
        default_weight = request.form.get('default_weight') or None
        if default_sets is not None and default_sets != '':
            default_sets = int(default_sets)
        else:
            default_sets = None
        if default_reps is not None and default_reps != '':
            default_reps = int(default_reps)
        else:
            default_reps = None
        if default_weight is not None and default_weight != '':
            default_weight = float(default_weight)
        else:
            default_weight = None
        if name:
            conn.execute(
                'INSERT INTO exercises (name, muscle_group, memo, video_url, default_sets, default_reps, default_weight) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (name, muscle, memo, video_url, default_sets, default_reps, default_weight)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('exercises'))

    # 並び替えや部位フィルター取得
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
    # 番号付け用に全エクササイズを古い順で取得
    all_rows = conn.execute('SELECT id FROM exercises ORDER BY id ASC').fetchall()
    number_map = {r['id']: idx + 1 for idx, r in enumerate(all_rows)}
    conn.close()
    return render_template('exercises.html', exercises=rows, sort=sort, muscle=muscle, numbers=number_map)

@app.route('/log', methods=['POST'])
def log():
    """トレーニングログをDBに保存"""
    conn = get_db_connection()
    # トレーニングログ登録（複数行対応）
    date = request.form['date'] or datetime.now().strftime('%Y-%m-%d')
    exercise_ids = request.form.getlist('exercise_id')
    sets_list = request.form.getlist('sets')
    reps_list = request.form.getlist('reps')
    weight_list = request.form.getlist('weight')
    intensity_list = request.form.getlist('intensity')
    note_list = request.form.getlist('note')
    for ex, st, rp, wt, it, nt in zip(exercise_ids, sets_list, reps_list, weight_list, intensity_list, note_list):
        intensity_value = it if it else '心地よい'
        conn.execute(
            'INSERT INTO workouts (exercise_id, date, sets, reps, weight, intensity, note) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (int(ex), date, int(st), int(rp), float(wt), intensity_value, nt.strip())
        )
    conn.commit()
    conn.close()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return ('', 204)
    return redirect(url_for('index'))

@app.route('/log_form')
def log_form_modal():
    """モーダル表示用のログ登録フォームを返す"""
    conn = get_db_connection()
    exercises = conn.execute(
        'SELECT * FROM exercises ORDER BY muscle_group ASC, name ASC'
    ).fetchall()
    conn.close()
    return render_template('log_form.html', exercises=exercises)

@app.route('/calendar')
def calendar_view():
    """カレンダー表示ページ"""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT w.date, e.muscle_group
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
    ''').fetchall()
    conn.close()
    # 日付ごとに種目部位のセットを作成
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
    cal = calendar.Calendar(firstweekday=6)
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


@app.route('/day_data/<date>')
def day_data(date):
    """指定日のトレーニングデータをJSONで返す"""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT w.date, e.name, e.muscle_group, w.sets, w.reps, w.weight
        FROM workouts w
        JOIN exercises e ON w.exercise_id = e.id
        WHERE w.date = ?
        ORDER BY w.id ASC
    ''', (date,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/day/<date>')
def day_detail(date):
    """1日の詳細ページ"""
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
    # デバッグモードでアプリを起動
    app.run(debug=True)
