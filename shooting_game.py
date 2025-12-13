from flask import Flask, render_template_string

app = Flask(__name__)

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Neon Space Defender</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            background-color: #050505;
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace;
            touch-action: none;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        canvas {
            border-bottom: 2px solid #333;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.1);
        }
        #ui-layer {
            position: absolute;
            top: 10px;
            left: 10px;
            color: #0ff;
            font-size: 18px;
            font-weight: bold;
            text-shadow: 0 0 5px #0ff;
            pointer-events: none;
        }
        #controls {
            width: 100%;
            height: 30vh; /* Bottom 30% for controls */
            background: #111;
            display: grid;
            grid-template-columns: 1fr 1fr 1.5fr;
            gap: 10px;
            padding: 10px;
            box-sizing: border-box;
        }
        .btn {
            background: #222;
            border: 2px solid #444;
            border-radius: 10px;
            color: white;
            font-size: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            user-select: none;
        }
        .btn:active { background: #444; }
        .btn-shoot {
            background: #c0392b;
            border-color: #e74c3c;
            color: #fff;
            font-weight: bold;
        }
        .btn-shoot:active { background: #e74c3c; }
    </style>
</head>
<body>

    <div id="ui-layer">
        SCORE: <span id="score">0</span> <br>
        HP: <span id="hp">100</span>%
    </div>

    <canvas id="gameCanvas"></canvas>

    <div id="controls">
        <div class="btn" id="btn-left">◄</div>
        <div class="btn" id="btn-right">►</div>
        <div class="btn btn-shoot" id="btn-shoot">FIRE</div>
    </div>

<script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // Dynamic Sizing
    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight * 0.7; // Top 70%
    }
    window.addEventListener('resize', resize);
    resize();

    // Game State
    let score = 0;
    let gameOver = false;
    let frame = 0;
    let difficulty = 1;

    // Inputs
    let keys = { left: false, right: false, shoot: false };

    // --- ENTITIES ---
    
    // Player
    const player = {
        x: canvas.width / 2,
        y: canvas.height - 50,
        width: 30,
        height: 30,
        speed: 7,
        hp: 100,
        color: '#0ff'
    };

    let bullets = [];
    let enemies = [];
    let particles = [];
    let stars = [];

    // Initialize Stars (Background)
    for(let i=0; i<50; i++) {
        stars.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            size: Math.random() * 2,
            speed: Math.random() * 3 + 1
        });
    }

    // --- GAME LOGIC ---

    function spawnEnemy() {
        const size = 30;
        const x = Math.random() * (canvas.width - size);
        enemies.push({
            x: x,
            y: -size,
            width: size,
            height: size,
            speed: 3 + Math.random() * 2 * difficulty,
            hp: 1
        });
    }

    function createExplosion(x, y, color) {
        for(let i=0; i<10; i++) {
            particles.push({
                x: x, y: y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10,
                life: 20,
                color: color
            });
        }
    }

    function update() {
        if (gameOver) return;
        frame++;

        // Difficulty ramp up
        if (frame % 500 === 0) difficulty += 0.2;

        // Move Player
        if (keys.left && player.x > 0) player.x -= player.speed;
        if (keys.right && player.x < canvas.width - player.width) player.x += player.speed;

        // Shoot (Auto-repeat limiter)
        if (keys.shoot && frame % 10 === 0) {
            bullets.push({ x: player.x + player.width/2 - 2, y: player.y, width: 4, height: 10, speed: 10 });
        }

        // Update Bullets
        for (let i = bullets.length - 1; i >= 0; i--) {
            let b = bullets[i];
            b.y -= b.speed;
            if (b.y < 0) bullets.splice(i, 1);
        }

        // Update Enemies
        if (frame % Math.floor(40 / difficulty) === 0) spawnEnemy();

        for (let i = enemies.length - 1; i >= 0; i--) {
            let e = enemies[i];
            e.y += e.speed;

            // Player Collision
            if (rectIntersect(player, e)) {
                player.hp -= 25;
                createExplosion(player.x, player.y, '#f00');
                enemies.splice(i, 1);
                if (player.hp <= 0) endGame();
                continue;
            }

            // Bullet Collision
            for (let j = bullets.length - 1; j >= 0; j--) {
                let b = bullets[j];
                if (rectIntersect(b, e)) {
                    createExplosion(e.x + e.width/2, e.y + e.height/2, '#ff0');
                    score += 100;
                    enemies.splice(i, 1);
                    bullets.splice(j, 1);
                    break;
                }
            }

            // Remove if off screen
            if (e.y > canvas.height) enemies.splice(i, 1);
        }

        // Update Particles
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.life--;
            if(p.life <= 0) particles.splice(i, 1);
        }

        // Update Stars
        stars.forEach(s => {
            s.y += s.speed;
            if (s.y > canvas.height) { s.y = 0; s.x = Math.random() * canvas.width; }
        });

        // Update UI
        document.getElementById('score').innerText = score;
        document.getElementById('hp').innerText = player.hp;
    }

    function rectIntersect(r1, r2) {
        return !(r2.x > r1.x + r1.width || 
                 r2.x + r2.width < r1.x || 
                 r2.y > r1.y + r1.height || 
                 r2.y + r2.height < r1.y);
    }

    function endGame() {
        gameOver = true;
        alert("GAME OVER! Final Score: " + score);
        location.reload();
    }

    // --- RENDER ---
    function draw() {
        // Clear
        ctx.fillStyle = '#050505';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw Stars
        ctx.fillStyle = '#fff';
        stars.forEach(s => {
            ctx.fillRect(s.x, s.y, s.size, s.size);
        });

        // Draw Player
        ctx.shadowBlur = 15;
        ctx.shadowColor = player.color;
        ctx.fillStyle = player.color;
        
        // Draw Triangle Ship
        ctx.beginPath();
        ctx.moveTo(player.x + player.width/2, player.y);
        ctx.lineTo(player.x + player.width, player.y + player.height);
        ctx.lineTo(player.x, player.y + player.height);
        ctx.fill();

        // Draw Bullets
        ctx.shadowColor = '#ff0';
        ctx.fillStyle = '#ff0';
        bullets.forEach(b => ctx.fillRect(b.x, b.y, b.width, b.height));

        // Draw Enemies
        ctx.shadowColor = '#f00';
        ctx.fillStyle = '#f00';
        enemies.forEach(e => {
            ctx.fillRect(e.x, e.y, e.width, e.height);
            // Enemy Eyes
            ctx.fillStyle = '#000';
            ctx.fillRect(e.x + 5, e.y + 10, 5, 5);
            ctx.fillRect(e.x + e.width - 10, e.y + 10, 5, 5);
            ctx.fillStyle = '#f00';
        });

        // Draw Particles
        particles.forEach(p => {
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.life / 20;
            ctx.fillRect(p.x, p.y, 3, 3);
            ctx.globalAlpha = 1.0;
        });
        
        ctx.shadowBlur = 0; // Reset
    }

    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }

    // --- INPUT HANDLING ---
    function setupBtn(id, key) {
        const el = document.getElementById(id);
        el.addEventListener('touchstart', (e) => { e.preventDefault(); keys[key] = true; });
        el.addEventListener('touchend', (e) => { e.preventDefault(); keys[key] = false; });
        el.addEventListener('mousedown', () => { keys[key] = true; });
        el.addEventListener('mouseup', () => { keys[key] = false; });
    }

    setupBtn('btn-left', 'left');
    setupBtn('btn-right', 'right');
    setupBtn('btn-shoot', 'shoot');

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

