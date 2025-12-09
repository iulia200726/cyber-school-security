from sklearn.ensemble import IsolationForest
import random
import numpy as np

# --- ANTRENAMENT ---
print("🧠 ML Engine: Se calibrează...")
X_train = []
# Îl învățăm cu date mici (normale)
for _ in range(3000):
    X_train.append([random.randint(1, 5000), random.randint(7, 22)])
# Îl învățăm cu date extreme (anomalii)
for _ in range(50):
    X_train.append([50000000, 3]) 

model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
model.fit(X_train)
print("🧠 ML Engine: Gata.")

def check_anomaly(packet_size, hour):
    # DEBUG: Vedem ce primește AI-ul
    print(f"[ML_ENGINE] Verific pachet de mărime: {packet_size} bytes...")

    # --- FILTRUL SUPREM ---
    # Dacă e sub 10KB, returnăm False automat.
    if packet_size < 10000:
        print("[ML_ENGINE] Pachet prea mic. IGNORAT de AI.")
        return False

    # Altfel, judecăm
    prediction = model.predict([[packet_size, hour]])
    if prediction[0] == -1:
        print("[ML_ENGINE] ANOMALIE DETECTATĂ!")
        return True 
    
    print("[ML_ENGINE] Trafic mare, dar pare normal.")
    return False