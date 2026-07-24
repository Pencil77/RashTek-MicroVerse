import os

chess_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>P2P Serverless Chess</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
    <style>
        :root {
            --bg-grad-1: #0f2027;
            --bg-grad-2: #203a43;
            --bg-grad-3: #2c5364;
            --glass-bg: rgba(255, 255, 255, 0.1);
            --glass-border: rgba(255, 255, 255, 0.2);
            --primary: #00f2fe;
            --secondary: #4facfe;
            --accent: #f1c40f;
            --danger: #e74c3c;
            --success: #2ecc71;
            --text-main: #f8f9fa;
        }
        body { 
            background: linear-gradient(135deg, var(--bg-grad-1), var(--bg-grad-2), var(--bg-grad-3));
            color: var(--text-main); 
            font-family: 'Poppins', sans-serif; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            margin: 0; 
            padding: 20px;
            min-height: 100vh;
            overflow-x: hidden;
        }
        h2 { 
            color: var(--primary); 
            margin: 10px 0; 
            font-weight: 800;
            text-shadow: 0 4px 10px rgba(0,0,0,0.3);
            letter-spacing: 1px;
            text-transform: uppercase;
        }
        
        /* Glassmorphism utility */
        .glass {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }

        #game-area { 
            display: none; 
            width: 100%; 
            max-width: 450px; 
            padding: 20px;
            animation: fadeIn 0.5s ease;
        }
        #board { width: 100%; margin-bottom: 15px; border-radius: 8px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        
        #lobby { 
            padding: 30px; 
            text-align: center; 
            max-width: 400px; 
            width: 90%; 
            margin-top: 20px;
            animation: slideUp 0.6s ease;
        }
        
        p { margin: 10px 0; font-weight: 300; }
        
        input { 
            padding: 12px 15px; 
            width: 85%; 
            border-radius: 8px; 
            border: 1px solid var(--glass-border); 
            background: rgba(0,0,0,0.2);
            color: #fff;
            text-align: center; 
            margin-bottom: 15px; 
            font-family: 'Poppins', sans-serif;
            outline: none;
            transition: all 0.3s;
        }
        input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.3);
        }
        
        button { 
            padding: 12px 24px; 
            border-radius: 8px; 
            border: none; 
            font-weight: 600; 
            font-family: 'Poppins', sans-serif;
            cursor: pointer; 
            width: 100%; 
            margin: 5px 0; 
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.3); }
        button:active { transform: translateY(1px); }
        
        .btn-host { background: linear-gradient(45deg, #11998e, #38ef7d); color: white; }
        .btn-join { background: linear-gradient(45deg, var(--secondary), var(--primary)); color: white; }
        .btn-copy { background: rgba(255,255,255,0.1); color: white; font-size: 12px; width: auto; border: 1px solid rgba(255,255,255,0.2); }
        .btn-copy:hover { background: rgba(255,255,255,0.2); }
        .btn-reload { background: linear-gradient(45deg, #cb2d3e, #ef473a); color: white; }
        
        #status { 
            font-weight: 600; 
            color: var(--accent); 
            margin-bottom: 15px; 
            padding: 8px 15px;
            border-radius: 20px;
            background: rgba(0,0,0,0.3);
            display: inline-block;
        }
        .id-box { 
            background: rgba(0,0,0,0.4); 
            padding: 12px; 
            border-radius: 8px;
            border: 1px dashed var(--primary); 
            font-size: 15px; 
            color: var(--primary); 
            margin: 10px auto; 
            user-select: all; 
            word-break: break-all; 
            font-family: monospace;
            width: 85%;
        }
    
        .game-nav {
            position: fixed;
            top: 15px;
            left: 15px;
            z-index: 9999;
            text-decoration: none;
            color: #fff;
            background: rgba(0,0,0,0.45);
            border: 1px solid rgba(255,255,255,0.25);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 600;
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
        }
        .game-nav:hover { background: rgba(0,0,0,0.7); transform: scale(1.05); }

        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            background: rgba(0,0,0,0.2);
            padding: 10px 15px;
            border-radius: 10px;
        }
        .turn-indicator {
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 5px;
            background: rgba(255,255,255,0.1);
        }

        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.02); } 100% { transform: scale(1); } }

        .game-over-overlay {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.8);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 10;
            border-radius: 8px;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.5s ease;
        }
        .game-over-overlay h3 { color: var(--accent); font-size: 24px; margin-bottom: 20px; }
    </style>

    <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
    <script src="https://unpkg.com/peerjs@1.4.7/dist/peerjs.min.js"></script>
</head>
<body>
    <a href="index.html" class="game-nav">← Back to Games</a>

    <h2>⚡ P2P Chess</h2>
    <div id="status">Connecting to Global Network...</div>

    <div id="lobby" class="glass">
        <p>Your ID:</p>
        <div id="my-id" class="id-box">...</div>
        <button class="btn-copy" onclick="copyId()">Copy ID</button>
        
        <hr style="border: 0; height: 1px; background: rgba(255,255,255,0.1); margin: 25px 0;">
        
        <p>Challenge a Friend:</p>
        <input type="text" id="opponent-id" placeholder="Paste Opponent's ID here">
        <button class="btn-join" onclick="joinGame()">CONNECT & PLAY</button>
    </div>

    <div id="game-area" class="glass">
        <div class="game-header">
            <span>You: <b id="my-color" style="color:var(--primary)">?</b></span>
            <span id="turn-display" class="turn-indicator">Turn: White</span>
        </div>
        <div style="position: relative;">
            <div id="board"></div>
            <div id="game-over-screen" class="game-over-overlay">
                <h3 id="game-over-text">Game Over!</h3>
                <button class="btn-reload" onclick="location.reload()" style="width: 80%;">New Game</button>
            </div>
        </div>
        <button class="btn-reload" onclick="location.reload()" style="margin-top: 15px;">Abandon / Reload</button>
    </div>

<script>
    var board = null;
    var game = new Chess();
    var peer = null;
    var conn = null;
    var myId = null;
    var myColor = 'white'; 

    var peerConfig = {
        config: {
            'iceServers': [
                { url: 'stun:stun.l.google.com:19302' },
                { url: 'stun:stun1.l.google.com:19302' }
            ]
        }
    };

    peer = new Peer(null, peerConfig);

    peer.on('open', function(id) {
        myId = id;
        document.getElementById('my-id').innerText = id;
        let statusEl = document.getElementById('status');
        statusEl.innerText = "Online & Ready";
        statusEl.style.color = "var(--success)";
        statusEl.style.textShadow = "0 0 10px rgba(46, 204, 113, 0.5)";
    });

    peer.on('error', function(err) {
        document.getElementById('status').innerText = "Connection Error";
        document.getElementById('status').style.color = "var(--danger)";
    });

    peer.on('connection', function(c) {
        if(conn) { c.close(); return; }
        conn = c;
        myColor = 'white'; 
        setupConnection();
    });

    function joinGame() {
        var otherId = document.getElementById('opponent-id').value.trim();
        if(!otherId) { alert("Please enter a valid ID to connect!"); return; }

        let statusEl = document.getElementById('status');
        statusEl.innerText = "Connecting...";
        statusEl.style.color = "var(--primary)";
        
        conn = peer.connect(otherId);
        myColor = 'black'; 
        
        conn.on('open', function() {
            setupConnection();
        });
        
        setTimeout(function(){
            if(!conn.open) {
                statusEl.innerText = "Connection timeout... Check ID.";
                statusEl.style.color = "var(--danger)";
            }
        }, 5000);
    }

    function setupConnection() {
        let statusEl = document.getElementById('status');
        statusEl.innerText = "Connected! Match Started.";
        statusEl.style.color = "var(--success)";
        startGame();

        conn.on('data', function(data) {
            if(data.type === 'move') {
                game.move(data.move);
                board.position(game.fen());
                updateStatus();
            }
        });
        
        conn.on('close', function() {
            alert("Opponent disconnected!");
            location.reload();
        });
    }

    function startGame() {
        document.getElementById('lobby').style.display = 'none';
        document.getElementById('game-area').style.display = 'block';
        document.getElementById('my-color').innerText = myColor.toUpperCase();
        
        var config = {
            draggable: true,
            position: 'start',
            orientation: myColor,
            onDragStart: onDragStart,
            onDrop: onDrop,
            onSnapEnd: onSnapEnd,
            pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
        }
        board = Chessboard('board', config);
        updateStatus();
    }

    function onDragStart (source, piece) {
        if (game.game_over()) return false;
        var turn = game.turn() === 'w' ? 'white' : 'black';
        if (turn !== myColor) return false; 
    }

    function onDrop (source, target) {
        var move = game.move({ from: source, to: target, promotion: 'q' });
        if (move === null) return 'snapback';

        if(conn) {
            conn.send({ type: 'move', move: move });
        }
        updateStatus();
    }

    function onSnapEnd () { board.position(game.fen()); }

    function updateStatus() {
        var turn = game.turn() === 'w' ? 'White' : 'Black';
        var statusText = "Turn: " + turn;
        var turnDisp = document.getElementById('turn-display');
        
        if (game.in_checkmate()) {
            statusText = "Checkmate!";
            showGameOver(turn + " lost by checkmate.");
        } else if (game.in_draw()) {
            statusText = "Draw!";
            showGameOver("Game ended in a draw.");
        } else if (game.in_check()) {
            statusText += " (CHECK)";
            turnDisp.style.color = "var(--danger)";
        } else {
            turnDisp.style.color = "var(--text-main)";
        }
        
        turnDisp.innerText = statusText;
    }
    
    function showGameOver(msg) {
        document.getElementById('game-over-screen').style.display = 'flex';
        document.getElementById('game-over-text').innerText = msg;
    }

    function copyId() {
        navigator.clipboard.writeText(myId);
        let btn = document.querySelector('.btn-copy');
        btn.innerText = "Copied!";
        btn.style.background = "var(--success)";
        setTimeout(() => { btn.innerText = "Copy ID"; btn.style.background = "rgba(255,255,255,0.1)"; }, 2000);
    }
</script>
</body>
</html>"""

craft_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Termux-Craft</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Poppins:wght@600&display=swap" rel="stylesheet">
    <style>
        :root {
            --glass-bg: rgba(20, 20, 20, 0.6);
            --glass-border: rgba(255, 255, 255, 0.15);
            --accent: #2ecc71;
            --danger: #e74c3c;
        }
        body { 
            margin: 0; 
            overflow: hidden; 
            background: #000; 
            font-family: 'Roboto Mono', monospace; 
            touch-action: none; 
            user-select: none;
            -webkit-user-select: none;
        }
        canvas { display: block; }
        
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        
        /* Glassmorphism utility */
        .glass {
            background: var(--glass-bg);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }

        #inventory-bar {
            position: absolute; top: 15px; left: 50%; transform: translateX(-50%);
            display: flex; gap: 8px; pointer-events: auto;
            padding: 8px;
        }
        .slot {
            width: 45px; height: 45px; 
            background: rgba(0,0,0,0.5); 
            border: 2px solid #555;
            border-radius: 8px;
            color: white; display: flex; justify-content: center; align-items: center;
            font-size: 14px; font-weight: bold; position: relative; cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        .slot:hover { transform: translateY(-2px); }
        .slot.active { 
            border-color: #f1c40f; 
            box-shadow: 0 0 10px rgba(241, 196, 15, 0.5), inset 0 0 10px rgba(0,0,0,0.5); 
            transform: scale(1.1);
        }
        .slot span { 
            position: absolute; bottom: 2px; right: 4px; 
            font-size: 11px; text-shadow: 1px 1px 0 #000;
        }
        
        #controls {
            position: absolute; bottom: 25px; left: 25px;
            display: grid; grid-template-columns: 65px 65px 65px; grid-template-rows: 65px 65px;
            gap: 12px; pointer-events: auto;
        }
        .btn {
            width: 65px; height: 65px; 
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(5px);
            border-radius: 50%; 
            border: 2px solid rgba(255,255,255,0.3);
            display: flex; justify-content: center; align-items: center;
            color: white; font-size: 24px; touch-action: manipulation;
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            transition: all 0.1s;
        }
        .btn:active { background: rgba(255, 255, 255, 0.4); transform: scale(0.95); }
        
        #action-buttons {
            position: absolute; bottom: 35px; right: 35px;
            display: flex; gap: 15px; pointer-events: auto;
        }
        .action-btn {
            width: 80px; height: 80px; 
            background: var(--danger);
            border-radius: 50%; 
            border: 3px solid rgba(255,255,255,0.3);
            color: white; font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 16px;
            display: flex; justify-content: center; align-items: center;
            box-shadow: 0 5px 15px rgba(231, 76, 60, 0.5);
            transition: all 0.2s;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }
        .action-btn:active { transform: scale(0.9); box-shadow: 0 2px 5px rgba(231, 76, 60, 0.5); }
        
        #debug { 
            position: absolute; top: 15px; right: 15px; 
            color: #00f2fe; font-size: 12px; font-weight: bold;
            text-shadow: 1px 1px 2px #000;
            background: rgba(0,0,0,0.4);
            padding: 5px 10px;
            border-radius: 5px;
        }
    
        .game-nav {
            position: fixed;
            top: 15px;
            left: 15px;
            z-index: 9999;
            text-decoration: none;
            color: #fff;
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.2);
            padding: 8px 14px;
            border-radius: 30px;
            font-size: 13px;
            font-family: 'Poppins', sans-serif;
            backdrop-filter: blur(5px);
            transition: background 0.3s;
            pointer-events: auto;
        }
        .game-nav:hover { background: rgba(0,0,0,0.8); }

        #crosshair {
            position: absolute; top: 50%; left: 50%;
            width: 20px; height: 20px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            opacity: 0.5;
        }
        #crosshair::before, #crosshair::after {
            content: ''; position: absolute; background: white;
        }
        #crosshair::before { top: 9px; left: 0; width: 20px; height: 2px; }
        #crosshair::after { left: 9px; top: 0; width: 2px; height: 20px; }
    </style>
</head>
<body>
    <a href="index.html" class="game-nav">← Exit</a>

    <canvas id="gameCanvas"></canvas>

    <div id="ui-layer">
        <div id="crosshair"></div>
        <div id="debug">FPS: 60 | Time: Day</div>
        
        <div id="inventory-bar" class="glass">
        </div>

        <div id="controls">
            <div class="btn" style="grid-column: 2; grid-row: 1;" id="btn-up">▲</div>
            <div class="btn" style="grid-column: 1; grid-row: 2;" id="btn-left">◀</div>
            <div class="btn" style="grid-column: 3; grid-row: 2;" id="btn-right">▶</div>
        </div>

        <div id="action-buttons">
            <div class="action-btn" id="btn-interact">MINE</div>
        </div>
    </div>

<script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d', { alpha: false });
    
    ctx.imageSmoothingEnabled = false;

    let width, height;
    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }
    window.addEventListener('resize', resize);
    resize();

    const TILE_SIZE = 40;
    const WORLD_W = 120; 
    const WORLD_H = 80;  
    const GRAVITY = 0.6;
    const TERMINAL_VELOCITY = 15;
    const SPEED = 5;
    const JUMP_POWER = 11;

    const BLOCKS = { AIR: 0, DIRT: 1, GRASS: 2, STONE: 3, COAL: 4, WOOD: 5, LEAVES: 6, BEDROCK: 7 };
    
    const COLORS = {
        0: null, 
        1: '#795548', // Dirt
        2: '#4CAF50', // Grass
        3: '#9E9E9E', // Stone
        4: '#424242', // Coal
        5: '#5D4037', // Wood
        6: '#81C784', // Leaves
        7: '#212121'  // Bedrock
    };

    let world = [];
    let particles = [];
    let camera = { x: 0, y: 0 };
    
    let player = {
        x: 60 * TILE_SIZE, y: 0, w: 24, h: 36,
        vx: 0, vy: 0, grounded: false, facingRight: true
    };

    let keys = { left: false, right: false, up: false, action: false };
    
    let inventory = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0 };
    let selectedBlock = 0; 
    let time = 0;
    const DAY_LENGTH = 3000;
    
    let lastTime = performance.now();
    let fps = 0;

    function initWorld() {
        world = new Array(WORLD_W * WORLD_H).fill(BLOCKS.AIR);

        let heights = [];
        for (let x = 0; x < WORLD_W; x++) {
            let h = Math.floor(WORLD_H / 2.5 + Math.sin(x / 8) * 6 + Math.sin(x / 3) * 2 + Math.cos(x/15)*4);
            heights[x] = h;
            
            for (let y = 0; y < WORLD_H; y++) {
                let idx = y * WORLD_W + x;
                
                if (y == WORLD_H - 1) {
                    world[idx] = BLOCKS.BEDROCK;
                } else if (y > h) {
                    if (y > h + 8 && Math.random() > 0.92) world[idx] = BLOCKS.COAL;
                    else if (y > h + 5) world[idx] = BLOCKS.STONE;
                    else world[idx] = BLOCKS.DIRT;
                } else if (y == h) {
                    world[idx] = BLOCKS.GRASS;
                    if (x > 5 && x < WORLD_W - 5 && Math.random() < 0.08) createTree(x, y);
                }
            }
        }
        player.y = (heights[60] - 5) * TILE_SIZE;
        updateInventoryUI();
    }

    function createTree(x, y) {
        let height = 4 + Math.floor(Math.random() * 3);
        for (let i = 1; i <= height; i++) setBlock(x, y - i, BLOCKS.WOOD);
        for (let lx = x - 2; lx <= x + 2; lx++) {
            for (let ly = y - height - 2; ly <= y - height + 1; ly++) {
                if (Math.abs(lx - x) + Math.abs(ly - (y - height)) < 3) {
                    if (getBlock(lx, ly) == BLOCKS.AIR) setBlock(lx, ly, BLOCKS.LEAVES);
                }
            }
        }
    }

    function getBlock(x, y) {
        if (x < 0 || x >= WORLD_W || y < 0 || y >= WORLD_H) return BLOCKS.BEDROCK;
        return world[y * WORLD_W + x];
    }

    function setBlock(x, y, id) {
        if (x < 0 || x >= WORLD_W || y < 0 || y >= WORLD_H) return;
        world[y * WORLD_W + x] = id;
    }

    function update() {
        if (keys.left) { player.vx = -SPEED; player.facingRight = false; }
        else if (keys.right) { player.vx = SPEED; player.facingRight = true; }
        else player.vx *= 0.7; 

        player.vy += GRAVITY;
        if (player.vy > TERMINAL_VELOCITY) player.vy = TERMINAL_VELOCITY;

        player.x += player.vx;
        handleCollisions(true);

        player.y += player.vy;
        player.grounded = false;
        handleCollisions(false);

        if (keys.up && player.grounded) {
            player.vy = -JUMP_POWER;
            spawnParticles(player.x + player.w/2, player.y + player.h, '#fff', 3);
        }

        // Smooth camera
        let targetCamX = player.x - width / 2;
        let targetCamY = player.y - height / 2;
        camera.x += (targetCamX - camera.x) * 0.1;
        camera.y += (targetCamY - camera.y) * 0.1;
        
        if(camera.x < 0) camera.x = 0;
        if(camera.x > WORLD_W * TILE_SIZE - width) camera.x = WORLD_W * TILE_SIZE - width;
        if(camera.y < 0) camera.y = 0;
        if(camera.y > WORLD_H * TILE_SIZE - height) camera.y = WORLD_H * TILE_SIZE - height;

        time = (time + 1) % DAY_LENGTH;

        if (keys.action) {
            performAction();
            keys.action = false; 
        }

        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.2; // Gravity for particles
            p.life--;
            if (p.life <= 0) particles.splice(i, 1);
        }
    }

    function handleCollisions(isX) {
        let corners = [
            { x: player.x, y: player.y },
            { x: player.x + player.w, y: player.y },
            { x: player.x, y: player.y + player.h },
            { x: player.x + player.w, y: player.y + player.h }
        ];

        for (let p of corners) {
            let tx = Math.floor(p.x / TILE_SIZE);
            let ty = Math.floor(p.y / TILE_SIZE);
            let block = getBlock(tx, ty);

            if (block != BLOCKS.AIR && block != BLOCKS.LEAVES) {
                if (isX) {
                    if (player.vx > 0) player.x = tx * TILE_SIZE - player.w - 0.01;
                    else if (player.vx < 0) player.x = (tx + 1) * TILE_SIZE + 0.01;
                    player.vx = 0;
                } else {
                    if (player.vy > 0) {
                        player.y = ty * TILE_SIZE - player.h - 0.01;
                        player.grounded = true;
                    } else if (player.vy < 0) {
                        player.y = (ty + 1) * TILE_SIZE + 0.01;
                    }
                    player.vy = 0;
                }
                return; 
            }
        }
    }

    function getTargetTile() {
        let cx = player.x + player.w / 2;
        let dir = player.facingRight ? 1 : -1;
        let tx = Math.floor((cx + dir * TILE_SIZE * 1.2) / TILE_SIZE);
        let ty = Math.floor((player.y + player.h / 2) / TILE_SIZE);
        return {tx, ty};
    }

    function performAction() {
        let {tx, ty} = getTargetTile();
        let currentBlock = getBlock(tx, ty);

        if (selectedBlock === 0) { 
            if (currentBlock != BLOCKS.AIR && currentBlock != BLOCKS.BEDROCK) {
                if (!inventory[currentBlock]) inventory[currentBlock] = 0;
                inventory[currentBlock]++;
                spawnParticles(tx * TILE_SIZE + TILE_SIZE/2, ty * TILE_SIZE + TILE_SIZE/2, COLORS[currentBlock], 8);
                setBlock(tx, ty, BLOCKS.AIR);
                updateInventoryUI();
            }
        } else {
            if ((currentBlock == BLOCKS.AIR || currentBlock == BLOCKS.LEAVES) && inventory[selectedBlock] > 0) {
                if (!(tx * TILE_SIZE < player.x + player.w && (tx+1)*TILE_SIZE > player.x &&
                      ty * TILE_SIZE < player.y + player.h && (ty+1)*TILE_SIZE > player.y)) {
                    setBlock(tx, ty, selectedBlock);
                    inventory[selectedBlock]--;
                    spawnParticles(tx * TILE_SIZE + TILE_SIZE/2, ty * TILE_SIZE + TILE_SIZE/2, '#fff', 4);
                    updateInventoryUI();
                }
            }
        }
    }

    function spawnParticles(x, y, color, count=5) {
        for (let i = 0; i < count; i++) {
            particles.push({
                x: x, y: y,
                vx: (Math.random() - 0.5) * 6,
                vy: (Math.random() - 1) * 5,
                life: 15 + Math.random() * 15,
                color: color,
                size: 3 + Math.random() * 3
            });
        }
    }

    function draw() {
        // Sky
        let brightness = 1.0;
        let timeRatio = time / DAY_LENGTH;
        if (timeRatio > 0.45 && timeRatio < 0.55) brightness = 1 - (timeRatio-0.45)*10; // Sunset
        else if (timeRatio >= 0.55 && timeRatio <= 0.9) brightness = 0.1; // Night
        else if (timeRatio > 0.9 && timeRatio < 1.0) brightness = 0.1 + (timeRatio-0.9)*9; // Sunrise
        
        let r = Math.floor(135 * brightness);
        let g = Math.floor(206 * brightness);
        let b = Math.floor(235 * brightness);
        
        // Stars at night
        ctx.fillStyle = brightness < 0.3 ? '#0a0a2a' : `rgb(${r}, ${g}, ${b})`;
        ctx.fillRect(0, 0, width, height);
        
        if (brightness < 0.3) {
            ctx.fillStyle = '#fff';
            for(let i=0; i<50; i++) {
                // Pseudo random stars based on camera pos
                let sx = (i * 123 + camera.x * 0.1) % width;
                let sy = (i * 321 + camera.y * 0.1) % (height/2);
                ctx.fillRect(sx, sy, 2, 2);
            }
        }

        ctx.save();
        ctx.translate(-Math.floor(camera.x), -Math.floor(camera.y));

        let startCol = Math.max(0, Math.floor(camera.x / TILE_SIZE));
        let endCol = Math.min(WORLD_W - 1, startCol + Math.ceil(width / TILE_SIZE));
        let startRow = Math.max(0, Math.floor(camera.y / TILE_SIZE));
        let endRow = Math.min(WORLD_H - 1, startRow + Math.ceil(height / TILE_SIZE));

        for (let y = startRow; y <= endRow; y++) {
            for (let x = startCol; x <= endCol; x++) {
                let block = getBlock(x, y);
                if (block !== BLOCKS.AIR) {
                    ctx.fillStyle = COLORS[block];
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                    
                    // Highlight top edge
                    ctx.fillStyle = "rgba(255,255,255,0.15)";
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, 3);
                    // Shadow bottom/right edge
                    ctx.fillStyle = "rgba(0,0,0,0.2)";
                    ctx.fillRect(x * TILE_SIZE + TILE_SIZE - 3, y * TILE_SIZE, 3, TILE_SIZE);
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE + TILE_SIZE - 3, TILE_SIZE, 3);
                }
            }
        }

        // Draw Player (Modernized slightly)
        ctx.fillStyle = '#e74c3c';
        ctx.beginPath();
        ctx.roundRect(player.x, player.y, player.w, player.h, 4);
        ctx.fill();
        
        // Eyes/Visor
        ctx.fillStyle = '#fff';
        let eyeX = player.facingRight ? player.x + 12 : player.x + 4;
        ctx.fillRect(eyeX, player.y + 6, 8, 4);
        ctx.fillStyle = '#3498db'; // pupil
        ctx.fillRect(player.facingRight ? eyeX + 4 : eyeX, player.y + 6, 4, 4);

        // Particles
        for (let p of particles) {
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life / 30;
            ctx.fillRect(p.x, p.y, p.size, p.size);
            ctx.globalAlpha = 1.0;
        }

        // Selection Highlight
        let {tx, ty} = getTargetTile();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.lineWidth = 2;
        ctx.strokeRect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE);

        ctx.restore();

        // UI Updates
        let now = performance.now();
        fps = Math.round(1000 / (now - lastTime));
        lastTime = now;
        
        let timeOfDay = brightness > 0.5 ? "Day" : (brightness > 0.3 ? "Dusk/Dawn" : "Night");
        document.getElementById('debug').innerText = `FPS: ${fps} | ${timeOfDay}`;
    }

    function updateInventoryUI() {
        const bar = document.getElementById('inventory-bar');
        bar.innerHTML = '';
        
        let pickDiv = document.createElement('div');
        pickDiv.className = selectedBlock === 0 ? 'slot active' : 'slot';
        pickDiv.innerText = '⛏️';
        pickDiv.onclick = () => { selectedBlock = 0; updateInventoryUI(); updateActionBtn(); };
        bar.appendChild(pickDiv);

        for (let id in inventory) {
            if (inventory[id] > 0) {
                let div = document.createElement('div');
                div.className = selectedBlock == id ? 'slot active' : 'slot';
                div.style.backgroundColor = COLORS[id];
                div.innerHTML = `<span>${inventory[id]}</span>`;
                div.onclick = () => { selectedBlock = id; updateInventoryUI(); updateActionBtn(); };
                bar.appendChild(div);
            }
        }
    }
    
    function updateActionBtn() {
        let btn = document.getElementById('btn-interact');
        if (selectedBlock === 0) {
            btn.style.background = 'var(--danger)';
            btn.innerText = "MINE";
            btn.style.boxShadow = '0 5px 15px rgba(231, 76, 60, 0.5)';
        } else {
            btn.style.background = 'var(--accent)';
            btn.innerText = "PLACE";
            btn.style.boxShadow = '0 5px 15px rgba(46, 204, 113, 0.5)';
        }
    }

    function setupBtn(id, key) {
        const el = document.getElementById(id);
        const press = (e) => { e.preventDefault(); keys[key] = true; };
        const release = (e) => { e.preventDefault(); keys[key] = false; };
        el.addEventListener('touchstart', press);
        el.addEventListener('touchend', release);
        el.addEventListener('mousedown', press);
        el.addEventListener('mouseup', release);
        el.addEventListener('mouseleave', release);
    }

    setupBtn('btn-left', 'left');
    setupBtn('btn-right', 'right');
    setupBtn('btn-up', 'up');
    setupBtn('btn-interact', 'action');

    initWorld();
    
    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }
    requestAnimationFrame(loop);

</script>
</body>
</html>"""


mario_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Termux Super Run</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&family=Poppins:wght@600;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --sky-top: #1CB5E0;
            --sky-bottom: #000046;
            --primary: #FF416C;
            --secondary: #FF4B2B;
            --ground: #38ef7d;
            --dirt: #11998e;
        }
        body {
            margin: 0;
            background: linear-gradient(to bottom, var(--sky-top), var(--sky-bottom));
            overflow: hidden;
            font-family: 'Poppins', sans-serif;
            touch-action: none; 
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }
        #game-container {
            position: relative;
            width: 100%;
            height: 65vh; 
            overflow: hidden;
            border-bottom: 6px solid #222;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }
        canvas { display: block; }
        
        #controls {
            height: 35vh; 
            width: 100%;
            background: rgba(10, 10, 20, 0.9);
            backdrop-filter: blur(10px);
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            padding: 20px 30px;
            box-sizing: border-box;
            align-items: center;
        }
        .btn {
            background: rgba(255,255,255,0.1);
            border: 2px solid rgba(255,255,255,0.2);
            border-radius: 20px;
            color: white;
            font-size: 30px;
            font-weight: 800;
            display: flex;
            justify-content: center;
            align-items: center;
            user-select: none;
            height: 100%;
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
            transition: all 0.1s;
        }
        .btn:active { 
            background: rgba(255,255,255,0.25); 
            transform: scale(0.95);
            box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .dpad { display: flex; gap: 15px; grid-column: span 2; height: 80px;}
        .action-btn { 
            background: linear-gradient(45deg, var(--primary), var(--secondary)); 
            grid-column: 3; 
            border: none;
            height: 80px;
            font-family: 'Press Start 2P', cursive;
            font-size: 16px;
            text-shadow: 2px 2px 0px rgba(0,0,0,0.5);
            box-shadow: 0 8px 20px rgba(255, 75, 43, 0.4);
        }
        .action-btn:active { background: linear-gradient(45deg, var(--secondary), var(--primary)); }
        .arrow { flex: 1; height: 100%; }
        
        #score-board {
            position: absolute;
            top: 20px;
            left: 20px;
            color: #fff;
            font-family: 'Press Start 2P', cursive;
            font-size: 14px;
            text-shadow: 2px 2px 0 #000;
            z-index: 10;
            background: rgba(0,0,0,0.4);
            padding: 10px 15px;
            border-radius: 10px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        #score-board span { color: #f1c40f; }
        
        .overlay {
            position: absolute; top:0; left:0; width:100%; height:100%;
            background: rgba(0,0,0,0.8);
            display: none; flex-direction: column; justify-content: center; align-items: center;
            z-index: 100;
            color: white; font-family: 'Press Start 2P', cursive;
        }
        .overlay h1 { font-size: 24px; margin-bottom: 20px; text-shadow: 3px 3px 0 var(--primary); text-align: center; line-height: 1.5; }
        .overlay button {
            padding: 15px 30px; font-family: 'Press Start 2P', cursive;
            font-size: 14px; cursor: pointer; border: none;
            background: var(--ground); color: #000; border-radius: 8px;
            box-shadow: 0 5px 0 var(--dirt);
        }
        .overlay button:active { transform: translateY(5px); box-shadow: none; }
    
        .game-nav {
            position: fixed; top: 15px; right: 15px; z-index: 9999;
            text-decoration: none; color: #fff; background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.25); padding: 8px 12px;
            border-radius: 20px; font-size: 12px; font-family: 'Poppins', sans-serif;
            backdrop-filter: blur(5px);
        }
    </style>
</head>
<body>
    <a href="index.html" class="game-nav">Exit</a>

    <div id="game-container">
        <div id="score-board">SCORE: <span id="coin-count">0</span></div>
        <canvas id="gameCanvas"></canvas>
        
        <div id="game-over" class="overlay">
            <h1 id="go-msg">GAME OVER</h1>
            <button onclick="resetGame()">RESTART</button>
        </div>
    </div>

    <div id="controls">
        <div class="dpad">
            <div class="btn arrow" id="btn-left">◀</div>
            <div class="btn arrow" id="btn-right">▶</div>
        </div>
        <div class="btn action-btn" id="btn-jump">JUMP</div>
    </div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d", { alpha: false });

    let viewWidth, viewHeight;
    function resize() {
        let container = document.getElementById('game-container');
        viewWidth = container.clientWidth;
        viewHeight = container.clientHeight;
        canvas.width = viewWidth;
        canvas.height = viewHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    const GRAVITY = 0.55;
    const FRICTION = 0.82;
    const SPEED = 6;
    const JUMP_FORCE = 12.5;

    let keys = { right: false, left: false, up: false };

    let player = { x: 50, y: 100, width: 32, height: 32, velX: 0, velY: 0, grounded: false, squish: 1.0 };
    let camera = { x: 0 };
    let score = 0;
    let isGameOver = false;
    let particles = [];

    const tileSize = 40;
    const mapString = 
        "                                                                         5      " +
        "                                                                         1      " +
        "                 333                                                33   1      " +
        "                22222                                              2222  1      " +
        "                                222                  333                 1      " +
        "       3                      33   3                22222                1      " +
        "      222                    2222222                  4             4    1      " +
        "             4      33                        222    222           222   1      " +
        "111111111111111111111111  1111111111111111   11111111111111111111111111111111111";
    
    let platforms = [], coins = [], enemies = [], flag = null;
    const rows = 9, cols = mapString.length / rows;

    function initLevel() {
        platforms = []; coins = []; enemies = []; particles = [];
        score = 0; isGameOver = false;
        document.getElementById('coin-count').innerText = score;
        document.getElementById('game-over').style.display = 'none';
        
        let mapRows = [];
        for (let i = 0; i < rows; i++) mapRows.push(mapString.slice(i * cols, (i + 1) * cols));

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                let type = mapRows[r][c];
                let x = c * tileSize;
                let y = viewHeight - ((rows - r) * tileSize); 

                if (type === '1' || type === '2') platforms.push({ x: x, y: y, width: tileSize, height: tileSize, type: type });
                else if (type === '3') coins.push({ x: x + 10, y: y + 10, width: 20, height: 20, active: true, float: Math.random()*Math.PI*2 });
                else if (type === '4') enemies.push({ x: x, y: y+8, width: 32, height: 32, velX: 1.5, startX: x });
                else if (type === '5') flag = { x: x, y: y, width: 10, height: tileSize * 8 }; 
            }
        }
    }

    function spawnParticles(x, y, color, count=10) {
        for(let i=0; i<count; i++) {
            particles.push({
                x: x, y: y,
                vx: (Math.random()-0.5)*8, vy: (Math.random()-1)*8,
                life: 20 + Math.random()*20, color: color, size: 2+Math.random()*4
            });
        }
    }

    function update() {
        if (isGameOver) return;

        player.velY += GRAVITY;
        player.grounded = false;

        if (keys.right && player.velX < SPEED) player.velX += 1;
        if (keys.left && player.velX > -SPEED) player.velX -= 1;
        player.velX *= FRICTION;
        player.x += player.velX;
        
        platforms.forEach(p => {
            if (colCheck(player, p)) {
                if (player.velX > 0) player.x = p.x - player.width;
                else if (player.velX < 0) player.x = p.x + p.width;
                player.velX = 0;
            }
        });

        player.y += player.velY;
        platforms.forEach(p => {
            if (colCheck(player, p)) {
                if (player.velY > 0) { 
                    player.grounded = true; player.y = p.y - player.height; player.velY = 0;
                    if(player.squish === 1.0) player.squish = 0.7; // Landing squash
                } else if (player.velY < 0) { 
                    player.y = p.y + p.height; player.velY = 0; 
                }
            }
        });

        // Recover squish
        player.squish += (1.0 - player.squish) * 0.2;

        if (keys.up && player.grounded) {
            player.velY = -JUMP_FORCE;
            player.grounded = false;
            player.squish = 1.3; // Jump stretch
            spawnParticles(player.x + 16, player.y + 32, '#fff', 5);
        }

        // Camera interpolation for smooth follow
        let targetCamX = player.x - viewWidth / 2 + player.width / 2;
        if (targetCamX < 0) targetCamX = 0;
        camera.x += (targetCamX - camera.x) * 0.1;

        coins.forEach(c => {
            c.float += 0.1;
            c.y += Math.sin(c.float) * 0.5;
            if (c.active && colCheck(player, c)) {
                c.active = false;
                score += 100;
                document.getElementById('coin-count').innerText = score;
                spawnParticles(c.x + 10, c.y + 10, '#f1c40f', 15);
            }
        });

        enemies.forEach(e => {
            e.x += e.velX;
            let hitWall = false;
            platforms.forEach(p => { if (colCheck(e, p)) hitWall = true; });
            if(hitWall || Math.abs(e.x - e.startX) > 150) e.velX *= -1;

            if (colCheck(player, e)) {
                if (player.velY > 0 && player.y < e.y + 16) {
                    e.y = 10000; 
                    player.velY = -8; 
                    score += 200;
                    document.getElementById('coin-count').innerText = score;
                    spawnParticles(e.x + 16, e.y, '#9b59b6', 20);
                } else {
                    die("YOU DIED");
                }
            }
        });

        if (flag && colCheck(player, flag)) {
            die("LEVEL COMPLETE!<br>SCORE: " + score);
        }

        if (player.y > viewHeight + 50) die("YOU FELL");

        // Particles
        for(let i=particles.length-1; i>=0; i--) {
            let p = particles[i];
            p.x += p.vx; p.y += p.vy; p.vy += 0.3; p.life--;
            if(p.life <= 0) particles.splice(i,1);
        }
    }

    function die(msg) {
        isGameOver = true;
        document.getElementById('go-msg').innerHTML = msg;
        document.getElementById('game-over').style.display = 'flex';
    }

    function colCheck(shapeA, shapeB) {
        return (shapeA.x < shapeB.x + shapeB.width && shapeA.x + shapeA.width > shapeB.x &&
                shapeA.y < shapeB.y + shapeB.height && shapeA.y + shapeA.height > shapeB.y);
    }

    function resetGame() {
        player.x = 50; player.y = 100; player.velX = 0; player.velY = 0;
        camera.x = 0;
        initLevel();
    }

    function draw() {
        // Sky Gradient (static background drawn on clear)
        let grad = ctx.createLinearGradient(0, 0, 0, viewHeight);
        grad.addColorStop(0, '#1CB5E0');
        grad.addColorStop(1, '#000046');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Clouds (parallax)
        ctx.fillStyle = 'rgba(255,255,255,0.4)';
        for(let i=0; i<5; i++) {
            ctx.beginPath();
            ctx.arc(((i*300 - camera.x*0.2) % (viewWidth+200)) - 100, 100 + (i%3)*40, 40, 0, Math.PI*2);
            ctx.arc(((i*300 - camera.x*0.2) % (viewWidth+200)) - 60, 100 + (i%3)*40, 50, 0, Math.PI*2);
            ctx.arc(((i*300 - camera.x*0.2) % (viewWidth+200)) - 20, 100 + (i%3)*40, 40, 0, Math.PI*2);
            ctx.fill();
        }

        ctx.save();
        ctx.translate(-Math.floor(camera.x), 0); 

        // Platforms
        platforms.forEach(p => {
            if(p.type === '1') {
                ctx.fillStyle = '#8e44ad'; // Ground dirt
                ctx.fillRect(p.x, p.y, p.width, p.height);
                ctx.fillStyle = '#2ecc71'; // Grass top
                ctx.fillRect(p.x, p.y, p.width, 8);
            } else {
                ctx.fillStyle = '#e67e22'; // Floating blocks
                ctx.beginPath();
                ctx.roundRect(p.x, p.y, p.width, p.height, 4);
                ctx.fill();
                ctx.strokeStyle = '#d35400';
                ctx.lineWidth = 2;
                ctx.strokeRect(p.x+2, p.y+2, p.width-4, p.height-4);
            }
        });

        if (flag) {
            ctx.fillStyle = '#bdc3c7';
            ctx.fillRect(flag.x, flag.y, flag.width, flag.height);
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath();
            ctx.moveTo(flag.x + 10, flag.y);
            ctx.lineTo(flag.x + 50, flag.y + 15);
            ctx.lineTo(flag.x + 10, flag.y + 30);
            ctx.fill();
        }

        ctx.fillStyle = '#f1c40f';
        ctx.shadowColor = '#f39c12'; ctx.shadowBlur = 10;
        coins.forEach(c => {
            if (c.active) {
                ctx.beginPath();
                ctx.ellipse(c.x + 10, c.y + 10, 8, 12, 0, 0, Math.PI * 2);
                ctx.fill();
            }
        });
        ctx.shadowBlur = 0; 

        // Enemies
        enemies.forEach(e => {
            ctx.fillStyle = '#c0392b';
            ctx.beginPath();
            ctx.roundRect(e.x, e.y, e.width, e.height, 8);
            ctx.fill();
            // Eyes
            ctx.fillStyle = 'white';
            ctx.fillRect(e.x + (e.velX > 0 ? 18 : 6), e.y + 8, 8, 8);
            ctx.fillStyle = 'black';
            ctx.fillRect(e.x + (e.velX > 0 ? 22 : 6), e.y + 10, 4, 4);
        });

        // Player
        ctx.save();
        ctx.translate(player.x + player.width/2, player.y + player.height); // Bottom center
        ctx.scale(1/player.squish, player.squish); 
        
        // Draw character body
        ctx.fillStyle = '#FF416C';
        ctx.beginPath();
        ctx.roundRect(-player.width/2, -player.height, player.width, player.height, 8);
        ctx.fill();
        
        // Face/Eyes
        ctx.fillStyle = 'white';
        let faceDir = player.velX > 0 ? 1 : (player.velX < 0 ? -1 : 0);
        let eyeOffset = faceDir * 4;
        ctx.fillRect(-8 + eyeOffset, -24, 6, 8);
        ctx.fillRect(2 + eyeOffset, -24, 6, 8);
        ctx.fillStyle = '#000';
        ctx.fillRect(-6 + eyeOffset, -22, 4, 4);
        ctx.fillRect(4 + eyeOffset, -22, 4, 4);

        ctx.restore();

        // Particles
        particles.forEach(p => {
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life / 40;
            ctx.fillRect(p.x, p.y, p.size, p.size);
        });
        ctx.globalAlpha = 1.0;

        ctx.restore();
        requestAnimationFrame(loop);
    }

    function loop() {
        update();
        draw();
    }

    function setupControls(id, key) {
        const el = document.getElementById(id);
        const press = (e) => { e.preventDefault(); keys[key] = true; };
        const release = (e) => { e.preventDefault(); keys[key] = false; };
        el.addEventListener('touchstart', press);
        el.addEventListener('touchend', release);
        el.addEventListener('mousedown', press);
        el.addEventListener('mouseup', release);
        el.addEventListener('mouseleave', release);
    }

    setupControls('btn-left', 'left');
    setupControls('btn-right', 'right');
    setupControls('btn-jump', 'up');

    // Keyboard support for testing
    window.addEventListener('keydown', e => {
        if(e.code === 'ArrowLeft') keys.left = true;
        if(e.code === 'ArrowRight') keys.right = true;
        if(e.code === 'ArrowUp' || e.code === 'Space') keys.up = true;
    });
    window.addEventListener('keyup', e => {
        if(e.code === 'ArrowLeft') keys.left = false;
        if(e.code === 'ArrowRight') keys.right = false;
        if(e.code === 'ArrowUp' || e.code === 'Space') keys.up = false;
    });

    initLevel();
    requestAnimationFrame(loop);

</script>
</body>
</html>"""

with open('/home/mrzoromit3/projects/RashTek-MicroVerse/Micro_Games/chess_p2p.html', 'w') as f:
    f.write(chess_code)

with open('/home/mrzoromit3/projects/RashTek-MicroVerse/Micro_Games/craft_game.html', 'w') as f:
    f.write(craft_code)

with open('/home/mrzoromit3/projects/RashTek-MicroVerse/Micro_Games/mario_game.html', 'w') as f:
    f.write(mario_code)
