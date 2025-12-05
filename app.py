from flask import Flask, render_template_string, request
import database as db
import time

app = Flask(__name__)
db.create_tables()

# Memorie pentru Brute Force
login_attempts = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>School Portal Login</title>
    <style>
        body { font-family: sans-serif; background-color: #2c3e50; color: white; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .box { background: white; color: #333; padding: 30px; border-radius: 8px; width: 300px; text-align: center; }
        input { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { width: 96%; padding: 10px; background-color: #e74c3c; color: white; border: none; cursor: pointer; border-radius: 4px; }
        button:hover { background-color: #c0392b; }
        .msg { margin-top: 15px; font-weight: bold; }
        .safe { color: red; }
        .normal { color: #e67e22; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🔒 Portal Note</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="text" name="username" placeholder="Utilizator" required>
            <input type="password" name="password" placeholder="Parolă" required>
            
            <p style="font-size:12px; text-align:left;">Upload Tema (Opțional):</p>
            <input type="file" name="file_upload">
            
            <button type="submit">Autentificare</button>
        </form>
        
        {% if message %}
            <p class="msg {{ msg_class }}">{{ message }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

def analyze_request(req):
    # 1. Luăm datele CURATE (doar textul introdus)
    user_input = req.form.get('username', '').lower()
    pass_input = req.form.get('password', '').lower()
    full_text = user_input + " " + pass_input
    
    # 2. MALWARE CHECK (Verificăm extensia fișierului)
    if 'file_upload' in req.files:
        file = req.files['file_upload']
        if file.filename != '':
            ext = file.filename.split('.')[-1].lower()
            # Lista neagră de extensii
            if ext in ['exe', 'bat', 'sh', 'vbs', 'py', 'php']:
                db.add_incident(4, "Upload Form", f"Malware blocat: {file.filename}", "Blocat")
                return True, "Fișier Malițios Detectat (Malware)!"

    # 3. SQL INJECTION (Doar tipare clare de atac)
    # Căutăm secvențe specifice, nu doar ghilimele simple
    sql_patterns = ["' or '1'='1", "' or 1=1", "union select", "drop table", "admin' --"]
    for pattern in sql_patterns:
        if pattern in full_text:
            db.add_incident(2, "Login Form", f"SQL Injection: {pattern}", "Critic")
            return True, "Tentativă SQL Injection!"

    # 4. XSS (Scripting)
    if "<script>" in full_text or "alert(" in full_text:
        db.add_incident(3, "Login Form", "XSS Script Detectat", "Critic")
        return True, "Atac XSS Detectat!"

    # 5. Phishing / Suspicious User
    if "admin" == user_input and "1234" in pass_input:
        # Doar un exemplu: admin cu parola slaba e considerat risc
        db.add_incident(1, "Login Form", "Tentativă Login Admin (Weak Pass)", "Investigație")
        return True, "Acces Admin Monitorizat."

    return False, None

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    msg_class = "normal"
    
    # Brute Force Check (Simplificat)
    ip = request.remote_addr
    # (Logica de brute force ar veni aici, dar o păstrăm simplă pt debugging acum)

    if request.method == 'POST':
        is_attack, reason = analyze_request(request)
        
        if is_attack:
            print(f"!!! ATAC: {reason}")
            message = f"⛔ ALARMĂ DE SECURITATE: {reason}"
            msg_class = "safe"
        else:
            # Aici ajunge logarea normală greșită
            message = "Utilizator sau parolă incorectă."
            msg_class = "normal"

    return render_template_string(HTML_PAGE, message=message, msg_class=msg_class)

@app.route('/admin')
def scan():
    db.add_incident(6, "URL /admin", "Scanning Vulnerability", "Monitorizare")
    return "<h1>403 Forbidden</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)