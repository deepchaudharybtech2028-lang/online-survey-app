
from flask import Flask, request, redirect, render_template_string
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("survey.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                experience TEXT NOT NULL,
                suggestions TEXT
            )
        """)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Online Survey</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #edf3ff;
            margin: 0;
            padding: 30px 15px;
        }
        .container {
            max-width: 600px;
            margin: auto;
            background: white;
            padding: 28px;
            border-radius: 14px;
            box-shadow: 0 4px 18px #0001;
        }
        h1 { color: #2346a0; text-align: center; }
        p { color: #555; text-align: center; }
        label { display: block; margin-top: 18px; font-weight: bold; }
        input, select, textarea {
            box-sizing: border-box;
            width: 100%;
            padding: 11px;
            margin-top: 7px;
            border: 1px solid #ccd2df;
            border-radius: 7px;
            font-size: 15px;
        }
        button {
            width: 100%;
            padding: 13px;
            margin-top: 22px;
            border: 0;
            border-radius: 7px;
            background: #2346a0;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        .success {
            background: #d9f8df;
            padding: 12px;
            border-radius: 7px;
            color: #17652a;
        }
        .link { display: block; text-align: center; margin-top: 18px; }
    </style>
</head>
<body>
<div class="container">
    <h1>Online Survey</h1>
    <p>Share your experience and help us improve.</p>

    {% if success %}
        <div class="success">Thank you! Your response has been saved.</div>
    {% endif %}

    <form method="POST">
        <label>Your Name</label>
        <input type="text" name="name" required maxlength="100"
               placeholder="Enter your name">

        <label>How was your experience?</label>
        <select name="experience" required>
            <option value="">Choose an option</option>
            <option>Excellent</option>
            <option>Good</option>
            <option>Average</option>
            <option>Poor</option>
        </select>

        <label>Suggestions</label>
        <textarea name="suggestions" rows="4" maxlength="2000"
                  placeholder="Share your suggestions"></textarea>

        <button type="submit">Submit Survey</button>
    </form>

    <a class="link" href="/responses">View Survey Responses</a>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        experience = request.form.get("experience", "").strip()
        suggestions = request.form.get("suggestions", "").strip()

        allowed = {"Excellent", "Good", "Average", "Poor"}
        if not name or experience not in allowed:
            return "Please enter your name and select a valid experience.", 400

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "INSERT INTO responses (name, experience, suggestions) VALUES (?, ?, ?)",
                (name, experience, suggestions)
            )
        return redirect("/?success=1")

    return render_template_string(HTML, success=request.args.get("success") == "1")


@app.route("/responses")
def responses():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, name, experience, suggestions FROM responses ORDER BY id DESC"
        ).fetchall()

    items = "".join(
        "<li><b>" + str(row["name"]).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        + "</b> — " + str(row["experience"])
        + "<br>" + str(row["suggestions"] or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        + "</li><br>"
        for row in rows
    )

    return """
    <!DOCTYPE html>
    <html><head><title>Survey Responses</title></head>
    <body style="font-family:Arial;max-width:700px;margin:40px auto;padding:15px">
    <h1>Survey Responses</h1>
    <p>Total responses: """ + str(len(rows)) + """</p>
    <ul>""" + items + """</ul>
    <a href="/">Back to Survey</a>
    </body></html>
    """


init_db()

if __name__ == "__main__":
    app.run(debug=True)
