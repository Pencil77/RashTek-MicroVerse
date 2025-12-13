from flask import Flask, render_template_string

app = Flask(__name__)

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Termux Retro 3D</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { 
            margin: 0; background: #000; overflow: hidden; 
            font-family: 'Courier New', monospace; touch-action: none; 
        }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* UI OVERLAY */
        #ui { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        
        #debug { position: absolute; top: 10px; left: 10px; color: #0f0; background: rgba(0,0,0,0.5); padding: 5px; }

        /* CONTROLS */
        .control-zone { position: absolute; bottom: 20px; width: 120px; height: 120px; pointer-events: auto; }
        #stick-left { left: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; border: 2px solid rgba(255,255,255,0.3); }
        #stick-right { right: 20px; background: rgba(255, 255, 255, 0.1); border-radius: 50%; border: 2px solid rgba(255,255,255,0.3); }
        
        .knob { 
            width: 50px; height: 50px; background: rgba(255, 255, 255, 0.5); border-radius: 50%; 
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            pointer-events: none;
        }

        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 20px; height: 20px;
            transform: translate(-50%, -50%); pointer-events: none;
        }
        .ch-line { background: #0f0; position: absolute; }
    </style>
</head>
<body>

    <div id="ui">
        <div id="debug">Generating World...</div>
        <div id="crosshair">
            <div class="ch-line" style="width: 2px; height: 20px; left: 9px; top: 0;"></div>
            <div class="ch-line" style="width: 20px; height: 2px; top: 9px; left: 0;"></div>
        </div>
        
        <div id="stick-left" class="control-zone">
            <div class="knob" id="knob-l"></div>
        </div>
        
        <div id="stick-right" class="control-zone">
            <div class="knob" id="knob-r"></div>
        </div>
    </div>

    <canvas id="screen"></canvas>

<script>
    // --- ENGINE CONSTANTS ---
    const canvas = document.getElementById('screen');
    const ctx = canvas.getContext('2d', { alpha: false }); // Optimize
    
    // Resolution (Low res for retro feel & high FPS)
    const SCREEN_W = 320;
    const SCREEN_H = 200;
    canvas.width = SCREEN_W;
    canvas.height = SCREEN_H;

    // --- GAME STATE ---
    const mapWidth = 32;
    const mapHeight = 32;
    let map = []; // 0 = empty, >0 = colored wall

    let player = {
        x: 16.5, y: 16.5,
        dir: 0,        // Direction in radians
        rotSpeed: 0,   // Current rotation speed
        moveSpeed: 0   // Current movement speed
    };

    // FOV settings
    const FOV = Math.PI / 3;
    const BLOCK_SIZE = 64; // For math scaling

    // Generate Random City Map
    function initMap() {
        for (let y = 0; y < mapHeight; y++) {
            let row = [];
            for (let x = 0; x < mapWidth; x++) {
                // Borders are walls
                if (x === 0 || x === mapWidth - 1 || y === 0 || y === mapHeight - 1) {
                    row.push(1);
                } else {
                    // Random blocks (City buildings)
                    if (Math.random() < 0.15) row.push(Math.floor(Math.random() * 4) + 1); // 1-4 color types
                    else row.push(0);
                }
            }
            map.push(row);
        }
        // Clear spawn area
        map[16][16] = 0; map[15][16] = 0; map[17][16] = 0;
        map[16][15] = 0; map[16][17] = 0;
    }

    // --- INPUT HANDLING (Touch Joysticks) ---
    let input = { fwd: 0, strafe: 0, rot: 0 };
    
    function setupJoystick(id, knobId, callback) {
        const zone = document.getElementById(id);
        const knob = document.getElementById(knobId);
        let startX, startY;
        
        zone.addEventListener('touchstart', e => {
            e.preventDefault();
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        }, {passive: false});

        zone.addEventListener('touchmove', e => {
            e.preventDefault();
            const x = e.touches[0].clientX;
            const y = e.touches[0].clientY;
            
            let dx = x - startX;
            let dy = y - startY;
            
            // Limit knob distance
            const max = 40;
            const dist = Math.sqrt(dx*dx + dy*dy);
            if(dist > max) { dx = (dx/dist)*max; dy = (dy/dist)*max; }
            
            knob.style.transform = `translate(-50%, -50%) translate(${dx}px, ${dy}px)`;
            
            // Normalize -1 to 1
            callback(dx / max, dy / max);
        }, {passive: false});

        zone.addEventListener('touchend', e => {
            e.preventDefault();
            knob.style.transform = `translate(-50%, -50%)`;
            callback(0, 0);
        });
    }

    // Left Stick: Forward/Back (Y)
    setupJoystick('stick-left', 'knob-l', (x, y) => {
        input.fwd = -y; // Up is negative Y on screen, but positive movement
    });

    // Right Stick: Rotate (X)
    setupJoystick('stick-right', 'knob-r', (x, y) => {
        input.rot = x;
    });

    // --- RAYCASTING ENGINE ---
    function castRays() {
        // Floor & Ceiling (Simple fill)
        ctx.fillStyle = '#333'; // Ceiling
        ctx.fillRect(0, 0, SCREEN_W, SCREEN_H / 2);
        ctx.fillStyle = '#111'; // Floor
        ctx.fillRect(0, SCREEN_H / 2, SCREEN_W, SCREEN_H / 2);

        for (let x = 0; x < SCREEN_W; x+=2) { // Skip 1 pixel for performance (320x200 is effectively 160 rays)
            // Calculate ray position and direction
            const cameraX = 2 * x / SCREEN_W - 1; // x-coordinate in camera space
            const rayDirX = Math.cos(player.dir) + Math.cos(player.dir + Math.PI/2) * cameraX * 0.66; // 0.66 is FOV scale
            const rayDirY = Math.sin(player.dir) + Math.sin(player.dir + Math.PI/2) * cameraX * 0.66;

            // Which box of the map we're in
            let mapX = Math.floor(player.x);
            let mapY = Math.floor(player.y);

            // Length of ray from current position to next x or y-side
            let sideDistX;
            let sideDistY;

            // Length of ray from one x or y-side to next x or y-side
            const deltaDistX = Math.abs(1 / rayDirX);
            const deltaDistY = Math.abs(1 / rayDirY);
            let perpWallDist;

            // What direction to step in x or y-direction (either +1 or -1)
            let stepX;
            let stepY;

            let hit = 0; // was there a wall hit?
            let side; // was a NS or a EW wall hit?
            let wallType = 1;

            if (rayDirX < 0) {
                stepX = -1;
                sideDistX = (player.x - mapX) * deltaDistX;
            } else {
                stepX = 1;
                sideDistX = (mapX + 1.0 - player.x) * deltaDistX;
            }
            if (rayDirY < 0) {
                stepY = -1;
                sideDistY = (player.y - mapY) * deltaDistY;
            } else {
                stepY = 1;
                sideDistY = (mapY + 1.0 - player.y) * deltaDistY;
            }

            // DDA Algorithm
            let depth = 0;
            while (hit === 0 && depth < 20) { // Max depth 20 blocks
                if (sideDistX < sideDistY) {
                    sideDistX += deltaDistX;
                    mapX += stepX;
                    side = 0;
                } else {
                    sideDistY += deltaDistY;
                    mapY += stepY;
                    side = 1;
                }
                if (map[mapY][mapX] > 0) {
                    hit = 1;
                    wallType = map[mapY][mapX];
                }
                depth++;
            }

            // Calculate distance projected on camera direction (Fish-eye correction)
            if (side === 0) perpWallDist = (mapX - player.x + (1 - stepX) / 2) / rayDirX;
            else            perpWallDist = (mapY - player.y + (1 - stepY) / 2) / rayDirY;

            // Calculate height of line to draw on screen
            const lineHeight = Math.floor(SCREEN_H / perpWallDist);

            // Calculate lowest and highest pixel to fill in current stripe
            let drawStart = -lineHeight / 2 + SCREEN_H / 2;
            if (drawStart < 0) drawStart = 0;
            let drawEnd = lineHeight / 2 + SCREEN_H / 2;
            if (drawEnd >= SCREEN_H) drawEnd = SCREEN_H - 1;

            // Choose wall color
            let color;
            switch(wallType) {
                case 1: color = '#e74c3c'; break; // Red
                case 2: color = '#3498db'; break; // Blue
                case 3: color = '#2ecc71'; break; // Green
                case 4: color = '#f1c40f'; break; // Yellow
                default: color = '#fff';
            }

            // Darken side walls for pseudo-3D effect
            if (side === 1) {
                // Parse hex to darken slightly (lazy way: just reset to grey for side)
                color = '#7f8c8d'; 
            }

            // Draw the vertical strip (2px wide)
            ctx.fillStyle = color;
            ctx.fillRect(x, drawStart, 2, drawEnd - drawStart);
        }
    }

    // --- GAME LOOP ---
    let lastTime = 0;

    function gameLoop(timestamp) {
        const dt = (timestamp - lastTime) / 1000;
        lastTime = timestamp;

        // 1. Update Player
        const moveSpeed = 3.0 * dt; // tiles per second
        const rotSpeed = 2.0 * dt;  // radians per second

        // Rotation
        if (input.rot !== 0) {
            player.dir += input.rot * rotSpeed;
        }

        // Movement
        if (input.fwd !== 0) {
            const moveStep = input.fwd * moveSpeed;
            const newX = player.x + Math.cos(player.dir) * moveStep;
            const newY = player.y + Math.sin(player.dir) * moveStep;

            // Simple collision
            if (map[Math.floor(newY)][Math.floor(newX)] === 0) {
                player.x = newX;
                player.y = newY;
            }
        }

        // 2. Render
        castRays();
        
        // Debug info
        document.getElementById('debug').innerText = 
            `Pos: ${Math.floor(player.x)},${Math.floor(player.y)}`;

        requestAnimationFrame(gameLoop);
    }

    // Initialize
    initMap();
    requestAnimationFrame(gameLoop);

</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(GAME_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

