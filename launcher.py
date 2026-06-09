import subprocess
import sys
import os

# Запускаємо app.py через Python
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app.py")
    
    # Запускаємо app.py
    subprocess.run([sys.executable, app_path])
