import sqlite3
import os
from flask import Flask, render_template_string, request, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_termux_key'
DB_NAME = 'chess_v3.db'  # Changed to v3 to ensure clean start

# --- DATABASE SETUP ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      username TEXT UNIQUE, 
                      password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS games 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      white_id INTEGER, 
                      black_id INTEGER, 
                      fen TEXT, 
                      turn TEXT, 
                      status TEXT)''')
        conn.commit()

init_db()

# --- HTML TEMPLATES ---

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chess Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #222; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .box { background: #333; padding: 20px; border-radius: 10px; width: 300px; text-align: center; }
        input { width: 90%; padding: 10px; margin: 10px 0; border-radius: 5px; border: none; }
        button { width: 100%; padding: 10px; margin-top: 5px; border: none; color: white; cursor: pointer; border-radius: 5px; font-weight: bold; }
        .login-btn { background: #e67e22; }
        .reg-btn { background: #27ae60; }
        .error { color: #e74c3c; margin-bottom: 10px; }
        .success { color: #2ecc71; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="box">
        <h2>Termux Chess V3</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        {% if msg %}<div class="success">{{ msg }}</div>{% endif %}
        
        <form method="POST">
            <input type="text" name="username" placeholder="Username" required autocomplete="off">
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" name="action" value="login" class="login-btn">Login</button>
            <button type="submit" name="action" value="register" class="reg-btn">Register</button>
        </form>
    </div>
</body>
</html>
"""

LOBBY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chess Lobby</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #222; color: #fff; padding: 20px; }
        .header { display: flex; justify-content: space-between; border-bottom: 1px solid #444; padding-bottom: 10px; }
        .btn { padding: 10px; border-radius: 5px; text-decoration: none; color: white; }
        .create { background: #27ae60; width: 100%; text-align: center; margin-top: 20px; display:block; border:none; font-size:16px; cursor:pointer;}
        .logout { background: #c0392b; font-size: 12px; }
        .game-card { background: #333; padding: 15px; margin-top: 10px; border-radius: 5px; display: flex; justify-content: space-between; align-items: center; }
        .join-btn { background: #3498db; padding: 5px 10px; border-radius: 3px; text-decoration: none; color: white; }
    </style>
</head>
<body>
    <div class="header">
        <div>User: <strong>{{ username }}</strong></div>
        <a href="/logout" class="btn logout">Logout</a>
    </div>

    <form method="POST" action="/create_game">
        <button type="submit" class="create">+ Create New Game</button>
    </form>

    <h3>Available Games</h3>
    {% if not games %} <p style="color:#777">No active games.</p> {% endif %}
    
    {% for game in games %}
    <div class="game-card">
        <div>
            <strong>Game #{{ game['id'] }}</strong> <br>
            <span style="font-size: 12px; color: #aaa;">{{ game['status'] }}</span>
        </div>
        
        {% if game['status'] == 'waiting' and game['white_id'] != user_id %}
            <a href="/join/{{ game['id'] }}" class="join-btn">JOIN</a>
        {% elif game['white_id'] == user_id or game['black_id'] == user_id %}
            <a href="/game/{{ game['id'] }}" class="join-btn" style="background:#e67e22">PLAY</a>
        {% else %}
            <span style="color:#555">Locked</span>
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
"""

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Chess Game</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <style>
        body { background: #111; color: #ccc; display: flex; flex-direction: column; align-items: center; font-family: sans-serif; margin: 0; padding-top: 20px; }
        #board { width: 340px; margin: 20px 0; }
        .status-box { background: #333; padding: 10px; border-radius: 5px; text-align: center; width: 320px; }
        .back-btn { margin-top: 20px; color: #777; text-decoration: none; }
    </style>
    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
</head>
<body>
    <div class="status-box">
        <div>You are: <strong style="color: {{ 'white' if is_white else 'orange' }}">{{ 'WHITE' if is_white else 'BLACK' }}</strong></div>
        <div id="status">Connecting...</div>
    </div>

    <div id="board"></div>
    <a href="/lobby" class="back-btn">← Back to Lobby</a>

<script>
    var board = null;
    var game = new Chess();
    var gameId = {{ game_id }};
    var myColor = "{{ 'white' if is_white else 'black' }}";
    var isMyTurn = false;

    function onDragStart (source, piece) {
        if (game.game_over()) return false;
        if (!isMyTurn) return false;
        if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
            (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
            return false;
        }
    }

    function onDrop (source, target) {
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';

        $.ajax({
            url: '/api/move/' + gameId,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ fen: game.fen() }),
            success: function() { isMyTurn = false; updateStatus(); }
        });
    }

    function updateStatus () {
        var status = '';
        var moveColor = (game.turn() === 'b') ? 'Black' : 'White';

        if (game.in_checkmate()) { status = 'Game over, ' + moveColor + ' is in checkmate.'; }
        else if (game.in_draw()) { status = 'Game drawn'; }
        else {
            status = moveColor + "'s turn";
            if (game.in_check()) status += ' (CHECK)';
        }
        $('#status').text(status);
    }

    // --- THIS IS THE FIX ---
    // We added pieceTheme to tell it where to find images
    var config = {
        draggable: true,
        position: 'start',
        orientation: myColor,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: function() { board.position(game.fen()); }
    }
    board = Chessboard('board', config);

    setInterval(function() {
        $.get('/api/state/' + gameId, function(data) {
            if (data.fen !== game.fen()) {
                game.load(data.fen);
                board.position(data.fen);
            }
            var serverTurn = (game.turn() === 'w') ? 'white' : 'black';
            isMyTurn = (serverTurn === myColor && data.status === 'active');
            
            if(data.status === 'waiting') $('#status').text("Waiting for opponent...");
            else updateStatus();
        });
    }, 1000);
</script>
</body>
</html>
"""

# --- ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = None
    error = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        c = conn.cursor()

        if action == 'register':
            try:
                hashed_pw = generate_password_hash(password)
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
                msg = "Registration successful! Please login."
            except sqlite3.IntegrityError:
                error = "Username already exists!"
        
        elif action == 'login':
            user = c.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                session.permanent = True
                conn.close()
                return redirect(url_for('lobby'))
            else:
                error = "Invalid username or password"
        
        conn.close()

    return render_template_string(LOGIN_TEMPLATE, error=error, msg=msg)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/lobby')
def lobby():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    games = conn.execute("SELECT * FROM games WHERE status != 'finished'").fetchall()
    conn.close()
    
    return render_template_string(LOBBY_TEMPLATE, games=games, username=session['username'], user_id=session['user_id'])

@app.route('/create_game', methods=['POST'])
def create_game():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
    conn = get_db_connection()
    conn.execute("INSERT INTO games (white_id, fen, turn, status) VALUES (?, ?, 'w', 'waiting')", 
                 (session['user_id'], start_fen))
    conn.commit()
    conn.close()
    return redirect(url_for('lobby'))

@app.route('/join/<int:game_id>')
def join_game(game_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    
    if game and game['status'] == 'waiting' and game['white_id'] != session['user_id']:
        conn.execute("UPDATE games SET black_id = ?, status = 'active' WHERE id = ?", 
                     (session['user_id'], game_id))
        conn.commit()
    
    conn.close()
    return redirect(url_for('play_game', game_id=game_id))

@app.route('/game/<int:game_id>')
def play_game(game_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    conn.close()

    if not game: return "Game not found"
    
    is_white = (game['white_id'] == session['user_id'])
    return render_template_string(GAME_TEMPLATE, game_id=game_id, is_white=is_white)

# --- API ---
@app.route('/api/state/<int:game_id>')
def get_state(game_id):
    conn = get_db_connection()
    game = conn.execute("SELECT fen, status, turn FROM games WHERE id = ?", (game_id,)).fetchone()
    conn.close()
    if game:
        return jsonify({'fen': game['fen'], 'status': game['status'], 'turn': game['turn']})
    return jsonify({})

@app.route('/api/move/<int:game_id>', methods=['POST'])
def make_move(game_id):
    if 'user_id' not in session: return jsonify({'error': 'auth'}), 403
    
    data = request.json
    conn = get_db_connection()
    conn.execute("UPDATE games SET fen = ? WHERE id = ?", (data['fen'], game_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

