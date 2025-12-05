from flask import Flask, render_template_string, request
import database as db

app = Flask(__name__)

# Ne asigurăm că baza de date există la pornire
db.create_tables()

# HTML-ul site-ului vulnerabil
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>School Portal - Login</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f2f6; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 300px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { width: 100%; padding: 10px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background-color: #45a049; }
        h2 { text-align: center; color: #333; }
        .alert { color: red; text-align: center; font-weight: bold; }
        .info { font-size: 12px; color: #666; text-align: center; margin-top: 20px;}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>Portal Note Elevi</h2>
        <p style="text-align:center">Loghează-te pentru a vedea notele.</p>
        <form method="POST">
            <input type="text" name="username" placeholder="Utilizator / Email" required>
            <input type="password" name="password" placeholder="Parolă" required>
            <button type="submit">Autentificare</button>
        </form>
        {% if message %}
            <p class="alert">{{ message }}</p>
        {% endif %}
        <div class="info">Sistem protejat de CyberGuardian v1.0</div>
    </div>
</body>
</html>
"""

# Funcție simplă de detectare a atacurilor (Semnături)
def detect_attack(input_text, source="Login Page"):
    input_text = input_text.lower()
    
    # 1. Detectare SQL Injection
    if "'" in input_text or "or 1=1" in input_text or "--" in input_text:
        db.add_incident(3, source, f"Tentativă SQL Injection detectată: {input_text}", "Investigație")
        return True, "SQL Injection"
    
    # 2. Detectare XSS (Cross Site Scripting)
    if "<script>" in input_text or "alert(" in input_text:
        db.add_incident(4, source, f"Tentativă XSS (Script malițios): {input_text}", "Investigație")
        return True, "XSS"
    
    # 3. Detectare Cuvinte suspecte (Phishing/Command Injection)
    if "admin" in input_text or "root" in input_text or "cmd" in input_text:
        db.add_incident(1, source, f"Utilizare cont privilegiat suspect: {input_text}", "Investigație")
        return True, "Suspicious User"
        
    return False, None

@app.route('/', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Analizăm ce a scris utilizatorul
        is_attack, attack_type = detect_attack(username)
        
        if is_attack:
            print(f"!!! ATAC DETECTAT: {attack_type} !!!") # Apare în terminal
            message = "⚠️ Eroare sistem: Activitate suspectă înregistrată și blocată!"
        else:
            message = "Utilizator sau parolă incorectă." # Simulăm un login eșuat normal

    return render_template_string(HTML_PAGE, message=message)

if __name__ == '__main__':
    # Pornim site-ul pe portul 5000
    app.run(debug=True, port=5000)