import subprocess
import sys
import os
import time

def run_services():
    print("🚀 Starting Election Assistant Services...")
    
    # 1. Start Backend (FastAPI)
    print("📡 Launching Backend (FastAPI)...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # 2. Start Frontend (Streamlit)
    print("🎨 Launching Frontend (Streamlit)...")
    frontend_proc = subprocess.Popen(
        ["streamlit", "run", "frontend/streamlit_app.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    try:
        while True:
            # Print outputs to console
            b_line = backend_proc.stdout.readline()
            if b_line:
                print(f"[Backend] {b_line.strip()}")
            
            f_line = frontend_proc.stdout.readline()
            if f_line:
                print(f"[Frontend] {f_line.strip()}")
                
            if backend_proc.poll() is not None and frontend_proc.poll() is not None:
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("✅ Done.")

if __name__ == "__main__":
    run_services()
