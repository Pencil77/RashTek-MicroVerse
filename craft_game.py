from flask import Flask, render_template_string

app = Flask(__name__)

GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Termux-Craft</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Courier New', monospace; touch-action: none; user-select: none; }
        canvas { display: block; }
        
        /* UI Overlay */
        #ui-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
        
        #inventory-bar {
            position: absolute; top: 10px; left: 10px;
            display: flex; gap: 5px; pointer-events: auto;
        }
        .slot {
            width: 40px; height: 40px; background: rgba(0,0,0,0.5); border: 2px solid #555;
            color: white; display: flex; justify-content: center; align-items: center;
            font-size: 10px; font-weight: bold; position: relative; cursor: pointer;
        }
        .slot.active { border-color: yellow; }
        .slot span { position: absolute; bottom: 2px; right: 2px; }
        
        #controls {
            position: absolute; bottom: 20px; left: 20px;
            display: grid; grid-template-columns: 60px 60px 60px; grid-template-rows: 60px 60px;
            gap: 10px; pointer-events: auto;
        }
        .btn {
            width: 60px; height: 60px; background: rgba(255, 255, 255, 0.2);
            border-radius: 50%; border: 2px solid rgba(255,255,255,0.5);
            display: flex; justify-content: center; align-items: center;
            color: white; font-size: 20px; touch-action: manipulation;
        }
        .btn:active { background: rgba(255, 255, 255, 0.5); }
        
        #action-buttons {
            position: absolute; bottom: 20px; right: 20px;
            display: flex; gap: 15px; pointer-events: auto;
        }
        .action-btn {
            width: 70px; height: 70px; background: #e74c3c;
            border-radius: 50%; border: 2px solid #c0392b;
            color: white; font-weight: bold; display: flex; justify-content: center; align-items: center;
        }
        
        #debug { position: absolute; top: 5px; right: 5px; color: lime; font-size: 10px; }
    </style>
</head>
<body>

    <canvas id="gameCanvas"></canvas>

    <div id="ui-layer">
        <div id="debug">FPS: 60 | Time: Day</div>
        
        <div id="inventory-bar">
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
    /** * ENGINE CONSTANTS & SETUP
     */
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    
    // Disable smoothing for pixel art look
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

    // Game Constants
    const TILE_SIZE = 32;
    const WORLD_W = 100; // Tiles wide
    const WORLD_H = 60;  // Tiles high
    const GRAVITY = 0.5;
    const TERMINAL_VELOCITY = 12;
    const SPEED = 4;
    const JUMP_POWER = 10;

    // Block IDs
    const BLOCKS = {
        AIR: 0, DIRT: 1, GRASS: 2, STONE: 3, COAL: 4, WOOD: 5, LEAVES: 6, BEDROCK: 7
    };
    
    // Block Colors
    const COLORS = {
        0: null, 
        1: '#5d4037', // Dirt
        2: '#388e3c', // Grass
        3: '#757575', // Stone
        4: '#212121', // Coal
        5: '#795548', // Wood
        6: '#4caf50', // Leaves
        7: '#000000'  // Bedrock
    };

    /**
     * STATE MANAGEMENT
     */
    let world = [];
    let particles = [];
    
    let camera = { x: 0, y: 0 };
    
    let player = {
        x: 50 * TILE_SIZE,
        y: 0,
        w: 20,
        h: 28,
        vx: 0,
        vy: 0,
        grounded: false,
        facingRight: true
    };

    let keys = { left: false, right: false, up: false, action: false };
    
    // Inventory: { blockId: count }
    let inventory = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    let selectedBlock = 0; // 0 means pickaxe mode (mining), >0 means placing

    // Day Cycle
    let time = 0;
    const DAY_LENGTH = 2000;
    
    /**
     * WORLD GENERATION (Procedural)
     */
    function initWorld() {
        world = new Array(WORLD_W * WORLD_H).fill(BLOCKS.AIR);

        // Simple terrain height generation using Math.sin
        let heights = [];
        for (let x = 0; x < WORLD_W; x++) {
            // Combine two sine waves for "hills"
            let h = Math.floor(WORLD_H / 3 + Math.sin(x / 10) * 5 + Math.sin(x / 4) * 2);
            heights[x] = h;
            
            for (let y = 0; y < WORLD_H; y++) {
                let idx = y * WORLD_W + x;
                
                if (y == WORLD_H - 1) {
                    world[idx] = BLOCKS.BEDROCK;
                } else if (y > h) {
                    // Underground
                    if (y > h + 5 && Math.random() > 0.95) world[idx] = BLOCKS.COAL;
                    else if (y > h + 8) world[idx] = BLOCKS.STONE;
                    else world[idx] = BLOCKS.DIRT;
                } else if (y == h) {
                    world[idx] = BLOCKS.GRASS;
                    
                    // Generate Trees randomly
                    if (x > 5 && x < WORLD_W - 5 && Math.random() < 0.05) {
                        createTree(x, y);
                    }
                }
            }
        }
        // Spawn player above highest point in middle
        player.y = (heights[50] - 5) * TILE_SIZE;
        updateInventoryUI();
    }

    function createTree(x, y) {
        let height = 3 + Math.floor(Math.random() * 3);
        // Trunk
        for (let i = 1; i <= height; i++) {
            setBlock(x, y - i, BLOCKS.WOOD);
        }
        // Leaves
        for (let lx = x - 2; lx <= x + 2; lx++) {
            for (let ly = y - height - 2; ly <= y - height; ly++) {
                if (Math.abs(lx - x) + Math.abs(ly - (y - height)) < 3) {
                    if (getBlock(lx, ly) == BLOCKS.AIR) setBlock(lx, ly, BLOCKS.LEAVES);
                }
            }
        }
    }

    // Helper to access 1D array as 2D
    function getBlock(x, y) {
        if (x < 0 || x >= WORLD_W || y < 0 || y >= WORLD_H) return BLOCKS.BEDROCK;
        return world[y * WORLD_W + x];
    }

    function setBlock(x, y, id) {
        if (x < 0 || x >= WORLD_W || y < 0 || y >= WORLD_H) return;
        world[y * WORLD_W + x] = id;
    }

    /**
     * PHYSICS & UPDATE
     */
    function update() {
        // --- Player Physics ---
        if (keys.left) player.vx = -SPEED;
        else if (keys.right) player.vx = SPEED;
        else player.vx *= 0.8; // Friction

        player.vy += GRAVITY;
        if (player.vy > TERMINAL_VELOCITY) player.vy = TERMINAL_VELOCITY;

        // X Collision
        player.x += player.vx;
        handleCollisions(true);

        // Y Collision
        player.y += player.vy;
        player.grounded = false;
        handleCollisions(false);

        // Jump
        if (keys.up && player.grounded) {
            player.vy = -JUMP_POWER;
        }

        // Camera Follow
        camera.x = player.x - width / 2;
        camera.y = player.y - height / 2;
        
        // Clamp Camera
        if(camera.x < 0) camera.x = 0;
        if(camera.x > WORLD_W * TILE_SIZE - width) camera.x = WORLD_W * TILE_SIZE - width;
        if(camera.y < 0) camera.y = 0;
        if(camera.y > WORLD_H * TILE_SIZE - height) camera.y = WORLD_H * TILE_SIZE - height;

        // Day/Night Cycle
        time++;
        if (time > DAY_LENGTH) time = 0;

        // Interaction (Mining/Placing)
        if (keys.action) {
            performAction();
            keys.action = false; // Trigger once per tap
        }

        // Particles
        for (let i = particles.length - 1; i >= 0; i--) {
            let p = particles[i];
            p.x += p.vx;
            p.y += p.vy;
            p.life--;
            if (p.life <= 0) particles.splice(i, 1);
        }
    }

    function handleCollisions(isX) {
        // Check corners of player
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

            if (block != BLOCKS.AIR) {
                if (isX) {
                    if (player.vx > 0) player.x = tx * TILE_SIZE - player.w - 0.1;
                    else if (player.vx < 0) player.x = (tx + 1) * TILE_SIZE + 0.1;
                    player.vx = 0;
                } else {
                    if (player.vy > 0) {
                        player.y = ty * TILE_SIZE - player.h - 0.1;
                        player.grounded = true;
                    } else if (player.vy < 0) {
                        player.y = (ty + 1) * TILE_SIZE + 0.1;
                    }
                    player.vy = 0;
                }
                return; // Collision handled
            }
        }
    }

    function performAction() {
        // Find block in front of player
        let cx = player.x + player.w / 2;
        let cy = player.y + player.h / 2;
        
        // Direction modifier
        let dir = player.vx >= 0 ? 1 : -1;
        if (Math.abs(player.vx) < 0.1) dir = keys.lastDir || 1; 

        // Target coords (1 block away)
        let tx = Math.floor((cx + dir * TILE_SIZE) / TILE_SIZE);
        let ty = Math.floor(cy / TILE_SIZE);

        let currentBlock = getBlock(tx, ty);

        if (selectedBlock === 0) { 
            // MINING MODE
            if (currentBlock != BLOCKS.AIR && currentBlock != BLOCKS.BEDROCK) {
                // Add to inventory
                if (!inventory[currentBlock]) inventory[currentBlock] = 0;
                inventory[currentBlock]++;
                
                // Spawn particles
                spawnParticles(tx * TILE_SIZE + TILE_SIZE/2, ty * TILE_SIZE + TILE_SIZE/2, COLORS[currentBlock]);
                
                // Remove block
                setBlock(tx, ty, BLOCKS.AIR);
                updateInventoryUI();
            }
        } else {
            // PLACING MODE
            if (currentBlock == BLOCKS.AIR && inventory[selectedBlock] > 0) {
                // Don't place inside player
                if (!(tx * TILE_SIZE < player.x + player.w && (tx+1)*TILE_SIZE > player.x &&
                      ty * TILE_SIZE < player.y + player.h && (ty+1)*TILE_SIZE > player.y)) {
                    
                    setBlock(tx, ty, selectedBlock);
                    inventory[selectedBlock]--;
                    updateInventoryUI();
                }
            }
        }
    }

    function spawnParticles(x, y, color) {
        for (let i = 0; i < 5; i++) {
            particles.push({
                x: x, y: y,
                vx: (Math.random() - 0.5) * 4,
                vy: (Math.random() - 0.5) * 4,
                life: 20,
                color: color
            });
        }
    }

    /**
     * RENDERING
     */
    function draw() {
        // 1. Sky & Background
        let brightness = 1.0;
        if (time > DAY_LENGTH * 0.6) brightness = 0.3; // Night
        
        ctx.fillStyle = `rgb(${135 * brightness}, ${206 * brightness}, ${235 * brightness})`;
        ctx.fillRect(0, 0, width, height);

        ctx.save();
        ctx.translate(-Math.floor(camera.x), -Math.floor(camera.y));

        // 2. Draw Visible Blocks (Culling for performance)
        let startCol = Math.floor(camera.x / TILE_SIZE);
        let endCol = startCol + (width / TILE_SIZE) + 1;
        let startRow = Math.floor(camera.y / TILE_SIZE);
        let endRow = startRow + (height / TILE_SIZE) + 1;

        for (let y = startRow; y <= endRow; y++) {
            for (let x = startCol; x <= endCol; x++) {
                let block = getBlock(x, y);
                if (block !== BLOCKS.AIR) {
                    ctx.fillStyle = COLORS[block];
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                    
                    // Simple lighting shade based on depth/surroundings
                    ctx.fillStyle = "rgba(0,0,0,0.1)";
                    ctx.fillRect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE);
                }
            }
        }

        // 3. Draw Player
        ctx.fillStyle = 'red';
        ctx.fillRect(player.x, player.y, player.w, player.h);
        // Eyes
        ctx.fillStyle = 'white';
        if (player.vx >= 0) ctx.fillRect(player.x + 12, player.y + 4, 4, 4);
        else ctx.fillRect(player.x + 4, player.y + 4, 4, 4);

        // 4. Draw Particles
        for (let p of particles) {
            ctx.fillStyle = p.color;
            ctx.fillRect(p.x, p.y, 4, 4);
        }

        // 5. Selection Highlight
        let cx = player.x + player.w / 2;
        let dir = player.vx >= 0 ? 1 : -1;
        if (Math.abs(player.vx) < 0.1) dir = keys.lastDir || 1;
        let tx = Math.floor((cx + dir * TILE_SIZE) / TILE_SIZE);
        let ty = Math.floor((player.y + player.h / 2) / TILE_SIZE);
        
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.strokeRect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE);

        ctx.restore();

        // 6. Day/Night Overlay UI
        document.getElementById('debug').innerText = `Time: ${Math.floor(time)}`;
    }

    /**
     * UI & CONTROLS
     */
    function updateInventoryUI() {
        const bar = document.getElementById('inventory-bar');
        bar.innerHTML = '';
        
        // Pickaxe Slot
        let pickDiv = document.createElement('div');
        pickDiv.className = selectedBlock === 0 ? 'slot active' : 'slot';
        pickDiv.innerText = '⛏️';
        pickDiv.onclick = () => { selectedBlock = 0; updateInventoryUI(); };
        bar.appendChild(pickDiv);

        // Block Slots
        for (let id in inventory) {
            if (inventory[id] > 0) {
                let div = document.createElement('div');
                div.className = selectedBlock == id ? 'slot active' : 'slot';
                div.style.backgroundColor = COLORS[id];
                div.innerHTML = `<span>${inventory[id]}</span>`;
                div.onclick = () => { selectedBlock = id; updateInventoryUI(); };
                bar.appendChild(div);
            }
        }
    }

    function setupBtn(id, key) {
        const el = document.getElementById(id);
        el.addEventListener('touchstart', (e) => { e.preventDefault(); keys[key] = true; if(key=='left') keys.lastDir=-1; if(key=='right') keys.lastDir=1; });
        el.addEventListener('touchend', (e) => { e.preventDefault(); keys[key] = false; });
        // Mouse for PC testing
        el.addEventListener('mousedown', () => { keys[key] = true; if(key=='left') keys.lastDir=-1; if(key=='right') keys.lastDir=1; });
        el.addEventListener('mouseup', () => { keys[key] = false; });
    }

    setupBtn('btn-left', 'left');
    setupBtn('btn-right', 'right');
    setupBtn('btn-up', 'up');
    setupBtn('btn-interact', 'action');

    // Change action button text based on mode
    setInterval(() => {
        let btn = document.getElementById('btn-interact');
        if (selectedBlock === 0) {
            btn.style.backgroundColor = '#e74c3c';
            btn.innerText = "MINE";
        } else {
            btn.style.backgroundColor = '#27ae60';
            btn.innerText = "PLACE";
        }
    }, 100);

    /**
     * GAME LOOP
     */
    initWorld();
    
    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }
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
