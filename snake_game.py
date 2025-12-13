from flask import Flask, render_template_string

app = Flask(__name__)

# This contains the HTML, CSS, and JavaScript for the game
GAME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Termux Snake</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        body {
            background-color: #2c3e50;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            font-family: 'Courier New', Courier, monospace;
            touch-action: none; /* Prevents zooming/scrolling on tap */
        }
        h2 { margin: 10px 0; }
        canvas {
            background-color: #000;
            border: 2px solid #ecf0f1;
            box-shadow: 0px 0px 15px rgba(0,0,0,0.5);
        }
        .controls {
            margin-top: 20px;
            display: grid;
            grid-template-columns: repeat(3, 60px);
            gap: 10px;
        }
        button {
            width: 60px;
            height: 60px;
            background-color: #e74c3c;
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 24px;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 4px #c0392b;
        }
        button:active {
            box-shadow: 0 2px #c0392b;
            transform: translateY(2px);
        }
        /* Grid layout for D-Pad */
        .up { grid-column: 2; }
        .left { grid-column: 1; grid-row: 2; }
        .down { grid-column: 2; grid-row: 2; }
        .right { grid-column: 3; grid-row: 2; }
    </style>
</head>
<body>

    <h2>Score: <span id="score">0</span></h2>
    <canvas id="gameCanvas" width="300" height="300"></canvas>

    <div class="controls">
        <button class="up" ontouchstart="setDir('UP')" onclick="setDir('UP')">W</button>
        <button class="left" ontouchstart="setDir('LEFT')" onclick="setDir('LEFT')">A</button>
        <button class="down" ontouchstart="setDir('DOWN')" onclick="setDir('DOWN')">S</button>
        <button class="right" ontouchstart="setDir('RIGHT')" onclick="setDir('RIGHT')">D</button>
    </div>

    <script>
        const canvas = document.getElementById("gameCanvas");
        const ctx = canvas.getContext("2d");
        const box = 15; // Size of one square
        
        let snake = [];
        snake[0] = { x: 10 * box, y: 10 * box }; // Starting position

        let food = {
            x: Math.floor(Math.random() * (canvas.width / box)) * box,
            y: Math.floor(Math.random() * (canvas.height / box)) * box
        };

        let score = 0;
        let d; // Direction

        // Listen for Keyboard (for testing on PC)
        document.addEventListener("keydown", direction);

        function direction(event) {
            let key = event.keyCode;
            if (key == 37 && d != "RIGHT") d = "LEFT";
            else if (key == 38 && d != "DOWN") d = "UP";
            else if (key == 39 && d != "LEFT") d = "RIGHT";
            else if (key == 40 && d != "UP") d = "DOWN";
        }

        // Handle Touch Controls
        function setDir(dir) {
            if (dir == "LEFT" && d != "RIGHT") d = "LEFT";
            else if (dir == "UP" && d != "DOWN") d = "UP";
            else if (dir == "RIGHT" && d != "LEFT") d = "RIGHT";
            else if (dir == "DOWN" && d != "UP") d = "DOWN";
        }

        function collision(head, array) {
            for (let i = 0; i < array.length; i++) {
                if (head.x == array[i].x && head.y == array[i].y) {
                    return true;
                }
            }
            return false;
        }

        function draw() {
            // Draw Background
            ctx.fillStyle = "#34495e";
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Draw Snake
            for (let i = 0; i < snake.length; i++) {
                ctx.fillStyle = (i == 0) ? "#2ecc71" : "#27ae60"; // Head is brighter
                ctx.fillRect(snake[i].x, snake[i].y, box, box);
                ctx.strokeStyle = "#34495e";
                ctx.strokeRect(snake[i].x, snake[i].y, box, box);
            }

            // Draw Food
            ctx.fillStyle = "#e74c3c";
            ctx.fillRect(food.x, food.y, box, box);

            // Old Head position
            let snakeX = snake[0].x;
            let snakeY = snake[0].y;

            // Move Direction
            if (d == "LEFT") snakeX -= box;
            if (d == "UP") snakeY -= box;
            if (d == "RIGHT") snakeX += box;
            if (d == "DOWN") snakeY += box;

            // If Snake eats the food
            if (snakeX == food.x && snakeY == food.y) {
                score++;
                document.getElementById("score").innerText = score;
                food = {
                    x: Math.floor(Math.random() * (canvas.width / box)) * box,
                    y: Math.floor(Math.random() * (canvas.height / box)) * box
                };
            } else {
                // Remove tail
                snake.pop();
            }

            let newHead = { x: snakeX, y: snakeY };

            // Game Over Rules
            if (snakeX < 0 || snakeX >= canvas.width || 
                snakeY < 0 || snakeY >= canvas.height || 
                collision(newHead, snake)) {
                
                clearInterval(game);
                alert("Game Over! Score: " + score);
                location.reload(); // Restart game
            }

            snake.unshift(newHead);
        }

        // Run the game every 100ms
        let game = setInterval(draw, 100);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(GAME_TEMPLATE)

if __name__ == '__main__':
    # 0.0.0.0 binds to all network interfaces so you can access it
    app.run(host='0.0.0.0', port=5000)

