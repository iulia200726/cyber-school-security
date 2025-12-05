from flask import Flask, render_template_string, request
import database as db
import time

app = Flask(__name__)
db.create_tables()

# --- MEMORIE PENTRU BRUTE FORCE ---
# Dicționar global: { 'IP_ADRESA': [timp1, timp2, timp3...] }
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
        .msg { margin-top: 15px; font-weight: bold; padding: 10px; border-radius: 5px;}
        .alert { background-color: #ffcccc; color: #cc0000; border: 1px solid #cc0000; }
        .info { background-color: #e6f7ff; color: #0066cc; border: 1px solid #0066cc; }
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
            <div class="msg {{ msg_class }}">{{ message }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

def check_brute_force(ip_address):
    current_time = time.time()
    
    # 1. Dacă e prima dată când vedem acest IP, facem o listă goală
    if ip_address not in login_attempts:
        login_attempts[ip_address] = []
        
    # 2. Curățăm lista: Păstrăm doar încercările din ultimele 10 secunde
    # (Ștergem tot ce e mai vechi de 10 secunde)
    login_attempts[ip_address] = [t for t in login_attempts[ip_address] if current_time - t < 10]
    
    # 3. Adăugăm tentativa curentă
    login_attempts[ip_address].append(current_time)
    
    # 4. Verificăm limita: Mai mult de 5 încercări în 10 secunde?
    if len(login_attempts[ip_address]) > 5:
        return True # ESTE BRUTE FORCE
    
    return False # E curat

def analyze_request(req):
    user_input = req.form.get('username', '').lower()
    pass_input = req.form.get('password', '').lower()
    full_text = user_input + " " + pass_input
    
    # MALWARE
    if 'file_upload' in req.files:
        file = req.files['file_upload']
        if file.filename != '':
            ext = file.filename.split('.')[-1].lower()
            if ext in ['exe', 'bat', 'sh', 'vbs', 'py']:
                db.add_incident(4, "Upload Form", f"Malware blocat: {file.filename}", "Blocat")
                return True, "Fișier Malițios Detectat!"

    # SQL INJECTION
    sql_patterns = ["' or '1'='1", "' or 1=1", "union select", "drop table", "admin' --"]
    for pattern in sql_patterns:
        if pattern in full_text:
            db.add_incident(2, "Login Form", f"SQL Injection: {pattern}", "Critic")
            return True, "Tentativă SQL Injection!"

    # XSS
    if "<script>" in full_text:
        db.add_incident(3, "Login Form", "XSS Script Detectat", "Critic")
        return True, "Atac XSS Detectat!"

    return False, None

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    msg_class = "info"
    
    # Preluăm IP-ul utilizatorului
    ip = request.remote_addr

    if request.method == 'POST':
        # PASUL 1: Verificăm Brute Force ÎNAINTE de orice altceva
        if check_brute_force(ip):
            print(f"!!! BRUTE FORCE DETECTAT DE PE {ip} !!!")
            # Scriem în baza de date cu ID-ul 5 (Brute Force)
            db.add_incident(5, f"IP: {ip}", "Viteză logare suspectă (Brute Force)", "Blocat Automat")
            return render_template_string(HTML_PAGE, message="⛔ PREA MULTE ÎNCERCĂRI! IP BLOCAT TEMPORAR.", msg_class="alert")

        # PASUL 2: Analizăm conținutul (SQL, Malware etc)
        is_attack, reason = analyze_request(request)
        
        if is_attack:
            message = f"ALARMĂ: {reason}"
            msg_class = "alert"
        else:
            message = "Utilizator sau parolă incorectă."
            msg_class = "info"

    return render_template_string(HTML_PAGE, message=message, msg_class=msg_class)

if __name__ == '__main__':
    app.run(debug=True, port=5000)