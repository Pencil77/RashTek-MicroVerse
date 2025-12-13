from flask import Flask, render_template_string

app = Flask(__name__)

# Single-file Mario Clone (HTML + CSS + JS)
GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Termux Super Mario</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            background-color: #5c94fc; /* Sky Blue */
            overflow: hidden;
            font-family: sans-serif;
            touch-action: none; /* Disable browser zooming */
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        #game-container {
            position: relative;
            width: 100%;
            height: 60vh; /* Game takes top 60% of screen */
            background: #5c94fc;
            overflow: hidden;
            border-bottom: 5px solid #000;
        }
        canvas {
            display: block;
        }
        #controls {
            height: 40vh; /* Controls take bottom 40% */
            width: 100%;
            background-color: #222;
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            padding: 20px;
            box-sizing: border-box;
        }
        .btn {
            background-color: #444;
            border: 2px solid #666;
            border-radius: 15px;
            color: white;
            font-size: 24px;
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            user-select: none;
        }
        .btn:active { background-color: #666; }
        .dpad { display: flex; gap: 10px; grid-column: span 2; }
        .action-btn { background-color: #e74c3c; grid-column: 3; }
        .arrow { flex: 1; height: 100%; }
        
        #score-board {
            position: absolute;
            top: 10px;
            left: 10px;
            color: white;
            font-size: 20px;
            font-weight: bold;
            text-shadow: 2px 2px 0 #000;
            z-index: 10;
        }
    </style>
</head>
<body>

    <div id="score-board">Coins: <span id="coin-count">0</span></div>

    <div id="game-container">
        <canvas id="gameCanvas"></canvas>
    </div>

    <div id="controls">
        <div class="dpad">
            <div class="btn arrow" id="btn-left">←</div>
            <div class="btn arrow" id="btn-right">→</div>
        </div>
        <div class="btn action-btn" id="btn-jump">JUMP</div>
    </div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // Game Config
    let viewWidth, viewHeight;
    function resize() {
        viewWidth = document.getElementById('game-container').clientWidth;
        viewHeight = document.getElementById('game-container').clientHeight;
        canvas.width = viewWidth;
        canvas.height = viewHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    // Physics Constants
    const GRAVITY = 0.6;
    const FRICTION = 0.8;
    const SPEED = 5;
    const JUMP_FORCE = 12;

    // Inputs
    let keys = { right: false, left: false, up: false };

    // --- ENTITIES ---

    // The "Mario"
    let player = {
        x: 50,
        y: 100,
        width: 30,
        height: 30,
        velX: 0,
        velY: 0,
        grounded: false,
        color: 'red'
    };

    // Camera
    let camera = { x: 0 };

    // Level Data (1 = Ground, 2 = Platform, 3 = Coin, 4 = Enemy, 5 = Flag)
    // A simple scrolling level map
    const tileSize = 40;
    const mapString = 
        "                                                                    5   " +
        "                                                                    1   " +
        "                 333                                                1   " +
        "                22222                                               1   " +
        "                                222                                 1   " +
        "       3                      33   3                                1   " +
        "      222                    2222222                  4             1   " +
        "             4      33                        222    222            1   " +
        "111111111111111111111111  1111111111111111   111111111111111111111111111";
    
    // Parse Map
    let platforms = [];
    let coins = [];
    let enemies = [];
    let flag = null;

    const rows = 9; // Based on mapString length
    const cols = mapString.length / rows;

    function initLevel() {
        platforms = [];
        coins = [];
        enemies = [];
        
        let mapRows = [];
        for (let i = 0; i < rows; i++) {
            mapRows.push(mapString.slice(i * cols, (i + 1) * cols));
        }

        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                let type = mapRows[r][c];
                let x = c * tileSize;
                let y = viewHeight - ((rows - r) * tileSize); // Align to bottom

                if (type === '1' || type === '2') {
                    platforms.push({ x: x, y: y, width: tileSize, height: tileSize, type: type });
                } else if (type === '3') {
                    coins.push({ x: x + 10, y: y + 10, width: 20, height: 20, active: true });
                } else if (type === '4') {
                    enemies.push({ x: x, y: y, width: tileSize, height: tileSize, velX: 2 });
                } else if (type === '5') {
                    flag = { x: x, y: y, width: 10, height: tileSize * 8 }; // Tall pole
                }
            }
        }
    }

    // --- GAME LOGIC ---

    function update() {
        // Apply Gravity
        player.velY += GRAVITY;
        player.grounded = false;

        // Input Movement
        if (keys.right) {
            if (player.velX < SPEED) player.velX++;
        }
        if (keys.left) {
            if (player.velX > -SPEED) player.velX--;
        }

        // Apply Friction
        player.velX *= FRICTION;

        // Move Player X
        player.x += player.velX;
        
        // Resolve X Collisions
        platforms.forEach(p => {
            if (colCheck(player, p)) {
                if (player.velX > 0) player.x = p.x - player.width;
                else if (player.velX < 0) player.x = p.x + p.width;
                player.velX = 0;
            }
        });

        // Move Player Y
        player.y += player.velY;

        // Resolve Y Collisions (Ground)
        platforms.forEach(p => {
            if (colCheck(player, p)) {
                if (player.velY > 0) { // Falling down
                    player.grounded = true;
                    player.y = p.y - player.height;
                    player.velY = 0;
                } else if (player.velY < 0) { // Jumping up
                    player.y = p.y + p.height;
                    player.velY = 0;
                }
            }
        });

        // Jump
        if (keys.up && player.grounded) {
            player.velY = -JUMP_FORCE;
            player.grounded = false;
        }

        // Camera Follow
        // Keep player in middle of screen horizontally
        camera.x = player.x - viewWidth / 2 + player.width / 2;
        if (camera.x < 0) camera.x = 0; // Don't scroll past start

        // Coin Collection
        coins.forEach(c => {
            if (c.active && colCheck(player, c)) {
                c.active = false;
                document.getElementById('coin-count').innerText = parseInt(document.getElementById('coin-count').innerText) + 1;
            }
        });

        // Enemy Logic
        enemies.forEach(e => {
            e.x += e.velX;
            // Simple patrol logic (turn around at edges would require more code, just bouncing for now)
            platforms.forEach(p => {
                if (colCheck(e, p)) {
                    e.velX *= -1; // Reverse direction on wall hit
                }
            });

            // Player Death
            if (colCheck(player, e)) {
                // Mario Mechanic: Kill enemy if falling on top, else die
                if (player.velY > 0 && player.y < e.y + 10) {
                    e.y = 10000; // Remove enemy
                    player.velY = -5; // Bounce
                } else {
                    resetGame();
                }
            }
        });

        // Win Condition
        if (flag && colCheck(player, flag)) {
            alert("Level Complete!");
            resetGame();
        }

        // Fall off world
        if (player.y > viewHeight + 100) {
            resetGame();
        }
    }

    function colCheck(shapeA, shapeB) {
        return (shapeA.x < shapeB.x + shapeB.width &&
                shapeA.x + shapeA.width > shapeB.x &&
                shapeA.y < shapeB.y + shapeB.height &&
                shapeA.y + shapeA.height > shapeB.y);
    }

    function resetGame() {
        player.x = 50;
        player.y = 100;
        player.velX = 0;
        player.velY = 0;
        camera.x = 0;
        document.getElementById('coin-count').innerText = "0";
        initLevel();
    }

    // --- RENDER ---
    function draw() {
        // Clear Screen
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.save();
        ctx.translate(-camera.x, 0); // Apply Camera Scroll

        // Draw Platforms
        platforms.forEach(p => {
            ctx.fillStyle = (p.type === '1') ? '#654321' : '#e67e22'; // Brown ground, Orange blocks
            ctx.fillRect(p.x, p.y, p.width, p.height);
            // Draw grass top
            if (p.type === '1') {
                ctx.fillStyle = '#2ecc71';
                ctx.fillRect(p.x, p.y, p.width, 5);
            }
        });

        // Draw Flag
        if (flag) {
            ctx.fillStyle = '#fff';
            ctx.fillRect(flag.x, flag.y, flag.width, flag.height);
            ctx.fillStyle = 'red';
            ctx.fillRect(flag.x + 10, flag.y, 40, 30);
        }

        // Draw Coins
        ctx.fillStyle = 'gold';
        coins.forEach(c => {
            if (c.active) {
                ctx.beginPath();
                ctx.arc(c.x + 10, c.y + 10, 8, 0, Math.PI * 2);
                ctx.fill();
            }
        });

        // Draw Enemies
        ctx.fillStyle = '#8e44ad'; // Purple Goombas
        enemies.forEach(e => {
            ctx.fillRect(e.x, e.y, e.width, e.height);
        });

        // Draw Player
        ctx.fillStyle = player.color;
        ctx.fillRect(player.x, player.y, player.width, player.height);

        ctx.restore();
        requestAnimationFrame(loop);
    }

    function loop() {
        update();
        draw();
    }

    // --- CONTROLS HANDLER ---
    function setupControls(id, key) {
        const el = document.getElementById(id);
        el.addEventListener('touchstart', (e) => { e.preventDefault(); keys[key] = true; });
        el.addEventListener('touchend', (e) => { e.preventDefault(); keys[key] = false; });
        el.addEventListener('mousedown', () => { keys[key] = true; });
        el.addEventListener('mouseup', () => { keys[key] = false; });
    }

    setupControls('btn-left', 'left');
    setupControls('btn-right', 'right');
    setupControls('btn-jump', 'up');

    // Init
    initLevel();
    loop();

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(GAME_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

