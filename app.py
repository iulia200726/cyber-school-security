from flask import Flask, render_template_string, request, redirect
import database as db
import ml_engine
import time
import datetime

app = Flask(__name__)
db.create_tables()

login_attempts = {}
scan_memory = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>School Portal IDS</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #2c3e50; color: white; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0;}
        .container { display: flex; gap: 20px; }
        .box { background: white; color: #333; padding: 40px; border-radius: 10px; width: 350px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }
        h2 { margin-top: 0; color: #2c3e50; }
        input { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 98%; padding: 12px; background-color: #2980b9; color: white; border: none; cursor: pointer; border-radius: 5px; font-weight: bold; }
        button:hover { background-color: #1a5276; }
        .sim-box { background: #34495e; padding: 20px; border-radius: 10px; width: 300px; text-align: center; display: flex; flex-direction: column; gap: 10px; border: 1px solid #4e667e; }
        .sim-btn { background-color: #e67e22; border: none; padding: 10px; color: white; border-radius: 5px; cursor: pointer; font-weight: bold; }
        .ml-btn { background-color: #8e44ad; } 
        .msg { margin-top: 20px; padding: 15px; border-radius: 5px; font-weight: bold; }
        .alert { background-color: #fadbd8; color: #c0392b; border: 1px solid #c0392b; }
        .info { background-color: #d4e6f1; color: #2980b9; border: 1px solid #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <div class="box">
            <h2>🔒 Portal Note Elevi</h2>
            <form action="/" method="POST" enctype="multipart/form-data">
                <input type="text" name="username" placeholder="Utilizator" required>
                <input type="password" name="password" placeholder="Parolă" required>
                <p style="font-size:12px; text-align:left; color:#666; margin-bottom:5px;">Upload Tema (Opțional):</p>
                <input type="file" name="file_upload" style="border:none;">
                <button type="submit">Autentificare</button>
            </form>
            {% if message %}
                <div class="msg {{ msg_class }}">{{ message }}</div>
            {% endif %}
        </div>

        <div class="sim-box">
            <h3>⚡ Panou Simulare</h3>
            <form action="/simulate_exfiltration" method="POST">
                <button type="submit" class="sim-btn ml-btn">📤 Simulare Furt Date (Activare AI)</button>
            </form>
            <p style="font-size: 13px; color: #ccc; margin-top: 10px;">Testare Scanare:</p>
            <a href="/admin"><button class="sim-btn">Accesare /admin</button></a>
        </div>
    </div>
</body>
</html>
"""

def analyze_request(req):
    user_input = req.form.get('username', '').lower()
    pass_input = req.form.get('password', '').lower()
    full_text = user_input + " " + pass_input
    packet_size = len(full_text)
    
    print(f"\n--- ANALIZĂ NOUĂ ---")
    print(f"Text primit: '{full_text}' (Mărime: {packet_size} bytes)")

    # 1. MALWARE
    if 'file_upload' in req.files:
        file = req.files['file_upload']
        if file.filename != '':
            ext = file.filename.split('.')[-1].lower()
            dangerous_ext = ['exe', 'bat', 'sh', 'vbs', 'py', 'php']
            if ext in dangerous_ext:
                print("-> DETECTAT: Malware")
                db.add_incident(5, "Upload Form", f"Malware: {file.filename}", "Blocat", packet_size)
                return True, "Fișier Malițios Detectat!"

    # 2. SQL INJECTION
    sql_signatures = ["' or '1'='1", "' or 1=1", "union select", "drop table", "admin' --", "select * from"]
    for sig in sql_signatures:
        if sig in full_text:
            print(f"-> DETECTAT: SQL Injection ({sig})")
            db.add_incident(1, "Login Form", f"SQL Injection: {sig}", "Critic", packet_size)
            return True, "Tentativă SQL Injection!"

    # 3. WEB ATTACKS
    web_threats = {
        "XSS (Script)": ["<script>", "javascript:"],
        "HTML Injection": ["<iframe", "<embed", "<object", "<form"],
        "Defacement": ["<style", "body{"]
    }
    for threat, patterns in web_threats.items():
        for p in patterns:
            if p in full_text:
                print(f"-> DETECTAT: {threat}")
                t_id = 2
                if "HTML" in threat: t_id = 3
                if "Defacement" in threat: t_id = 4
                db.add_incident(t_id, "Login Form", f"{threat}: {p}", "Ridicat", packet_size)
                return True, f"Alertă: {threat}!"

    # 4. MACHINE LEARNING (AI)
    # Verificăm AI doar dacă pachetul e URIAȘ (>5000)
    print(f"Verificare AI? Mărime {packet_size} vs Limită 5000...")
    
    if packet_size > 5000:
        print("-> Pachet mare. Întreb AI-ul...")
        is_anomaly = ml_engine.check_anomaly(packet_size, 12)
        if is_anomaly:
            print("-> AI zice: ANOMALIE!")
            db.add_incident(8, "Login", "Trafic Masiv", "Monitorizare", packet_size)
            return True, "🤖 ML ALERT: Anomalie comportamentală!"
    else:
        print("-> Pachet mic. AI-ul este IGNORAT.")

    print("-> Curat. Nicio amenințare.")
    return False, None

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    msg_class = "info"
    if request.method == 'POST':
        is_attack, reason = analyze_request(request)
        if is_attack:
            message = f"ALARMĂ: {reason}"
            msg_class = "alert"
        else:
            message = "Utilizator sau parolă incorectă."
    return render_template_string(HTML_PAGE, message=message, msg_class=msg_class)

@app.route('/simulate_exfiltration', methods=['POST'])
def simulate_ml_attack():
    fake_size = 50000000
    print(f"\n--- SIMULARE BUTON ---")
    print(f"Forțez incident de {fake_size} bytes.")
    
    # Scriem direct în DB fără să mai întrebăm funcția de analiză
    db.add_incident(8, "Rețea Internă", "Transfer Date Volum (Anomalie Comportamentală)", "ALERTA AI", fake_size)
    return render_template_string(HTML_PAGE, message="🤖 ML ALERT: Anomalie detectată (Simulare)!", msg_class="alert")

@app.route('/admin')
def scan_trap():
    db.add_incident(7, f"IP: {request.remote_addr}", "Port Scanning", "Monitorizare", 0)
    return "<h1>⛔ ACCES INTERZIS</h1>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)