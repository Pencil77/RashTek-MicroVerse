from flask import Flask, render_template_string

app = Flask(__name__)

GAME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Musical Chairs / Random Pause</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a1a;
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }

        h1 { color: #f1c40f; margin-bottom: 20px; }

        .container {
            background: #2c3e50;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            width: 90%;
            max-width: 500px;
            text-align: center;
        }

        .input-group { margin-bottom: 15px; text-align: left; }
        label { display: block; margin-bottom: 5px; font-size: 14px; color: #bdc3c7; }
        
        input {
            width: 100%;
            padding: 12px;
            background: #34495e;
            border: 1px solid #7f8c8d;
            border-radius: 5px;
            color: white;
            font-size: 16px;
            box-sizing: border-box; 
        }

        .row { display: flex; gap: 10px; }
        .col { flex: 1; }

        button {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 15px;
            width: 100%;
            font-size: 18px;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            margin-top: 10px;
            transition: transform 0.1s;
        }
        button:active { transform: scale(0.98); }
        button:disabled { background: #7f8c8d; cursor: not-allowed; }

        #status {
            margin-top: 20px;
            font-size: 18px;
            font-weight: bold;
            color: #2ecc71;
            min-height: 24px;
        }
        
        .stop-info { color: #e74c3c !important; font-size: 22px !important; }

        /* Responsive Video Container */
        .video-wrapper {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 */
            height: 0;
            margin-top: 20px;
            border-radius: 10px;
            overflow: hidden;
            border: 2px solid #555;
            display: none; /* Hidden until loaded */
        }
        
        .video-wrapper iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>

    <h1>🎵 Musical Chairs Bot</h1>

    <div class="container">
        <div class="input-group">
            <label>YouTube Link:</label>
            <input type="text" id="yt-link" placeholder="Paste link here..." value="https://www.youtube.com/watch?v=5qap5aO4i9A">
        </div>

        <div class="row">
            <div class="col input-group">
                <label>Min Duration (Sec):</label>
                <input type="number" id="min-time" value="10">
            </div>
            <div class="col input-group">
                <label>Max Duration (Sec):</label>
                <input type="number" id="max-time" value="30">
            </div>
        </div>

        <button id="play-btn" onclick="startRandomPlay()">▶ LOAD & PLAY</button>

        <div id="status">Ready (Starts at 5s)</div>

        <div class="video-wrapper" id="video-box">
            <div id="player"></div>
        </div>
    </div>

    <script>
        var tag = document.createElement('script');
        tag.src = "https://www.youtube.com/iframe_api";
        var firstScriptTag = document.getElementsByTagName('script')[0];
        firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

        var player;
        var stopTime = 0;
        var timerInterval = null;
        var isApiReady = false;

        function onYouTubeIframeAPIReady() {
            isApiReady = true;
        }

        function extractVideoID(url) {
            var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
            var match = url.match(regExp);
            return (match && match[7].length == 11) ? match[7] : false;
        }

        function startRandomPlay() {
            if (!isApiReady) {
                alert("YouTube API not loaded yet. Check internet.");
                return;
            }

            var url = document.getElementById('yt-link').value;
            var min = parseInt(document.getElementById('min-time').value);
            var max = parseInt(document.getElementById('max-time').value);
            var videoId = extractVideoID(url);

            if (!videoId) {
                alert("Invalid YouTube URL!");
                return;
            }

            if (min >= max) {
                alert("Min time must be less than Max time!");
                return;
            }

            // Calculate Random Stop Time (Duration)
            var randomDuration = Math.floor(Math.random() * (max - min + 1)) + min;
            stopTime = randomDuration; // We will add current time to this later

            document.getElementById('status').innerText = "Loading Video at 5s...";
            document.getElementById('status').className = "";
            document.getElementById('play-btn').disabled = true;
            document.getElementById('video-box').style.display = 'block';

            // UPDATED: Start at 5 seconds
            var playerConfig = {
                'videoId': videoId,
                'startSeconds': 5 
            };

            if (player && typeof player.loadVideoById === 'function') {
                player.loadVideoById(playerConfig);
                startTracking();
            } else {
                player = new YT.Player('player', {
                    height: '360',
                    width: '640',
                    videoId: videoId,
                    playerVars: { 'start': 5 }, // Start new player at 5s
                    events: {
                        'onReady': onPlayerReady,
                        'onStateChange': onPlayerStateChange
                    }
                });
            }
        }

        function onPlayerReady(event) {
            event.target.playVideo();
            startTracking();
        }

        function onPlayerStateChange(event) {
            if (event.data === YT.PlayerState.ENDED) {
                clearInterval(timerInterval);
                document.getElementById('status').innerText = "Video Ended naturally.";
                document.getElementById('play-btn').disabled = false;
            }
        }

        function startTracking() {
            if (timerInterval) clearInterval(timerInterval);

            var startTime = 0; 
            var hasStarted = false;
            var targetTimestamp = 0;

            document.getElementById('status').innerText = "Buffering...";

            timerInterval = setInterval(function() {
                if (!player || !player.getCurrentTime) return;

                var currentTime = player.getCurrentTime();
                var playerState = player.getPlayerState();

                // Check if actually playing (State 1)
                if (playerState === 1) {
                    if (!hasStarted) {
                        startTime = currentTime;
                        hasStarted = true;
                        
                        // UPDATED LOGIC: 
                        // Target Timestamp = Current Time + Random Duration selected earlier
                        targetTimestamp = startTime + stopTime;
                        
                        console.log("Started at: " + startTime + " | Will stop at: " + targetTimestamp);
                    }

                    document.getElementById('status').innerText = "Playing... 🎵";
                    document.getElementById('status').style.color = "#2ecc71";

                    // CHECK STOP CONDITION
                    if (currentTime >= targetTimestamp) {
                        player.pauseVideo();
                        clearInterval(timerInterval);
                        
                        // UPDATED: Show exactly where it stopped
                        var finalTime = currentTime.toFixed(1);
                        document.getElementById('status').innerText = "🛑 STOPPED at " + finalTime + "s";
                        document.getElementById('status').className = "stop-info";
                        document.getElementById('play-btn').disabled = false;
                    }
                }
            }, 100);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(GAME_TEMPLATE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

