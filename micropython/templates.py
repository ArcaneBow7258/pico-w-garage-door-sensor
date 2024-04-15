home = """<!DOCTYPE html>
    <html>
        <head> <title>Garage Door Status</title>
            <style>
            p {font-size: 30px}
            b {font-size: 30px}
            </style>
        </head>
        <script>
        var timer = setTimeout(function() {
            window.location.reload()
        }, $timer);
        </script>
        <body> <h1>Garage Door Status</h1>
            <p>Garage Door is currently $status. </p>
            <input></input>
            <a href=\"toggle\"><button class="button">Open/Close</button></a>
        </body>
    </html>
    """