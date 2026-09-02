import os
import sys
import subprocess
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "citycare-backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    # Locate Python in virtual environment
    venv_python = os.path.join(root_dir, "venv", "Scripts", "python.exe")
    if not os.path.exists(venv_python):
        venv_python = sys.executable

    # npm command on Windows
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"

    print("=" * 60)
    print("🚀 Starting CityCare Full-Stack System (Dev Mode)")
    print("=" * 60)
    print(f"🔹 Backend:  http://127.0.0.1:8000  (Docs: http://127.0.0.1:8000/docs)")
    print(f"🔹 Frontend: http://localhost:5173")
    print("Press Ctrl+C to terminate both servers.")
    print("=" * 60)

    # Prepare backend environment
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"

    backend_proc = None
    frontend_proc = None

    try:
        # Launch Backend
        backend_proc = subprocess.Popen(
            [venv_python, "main.py"],
            cwd=backend_dir,
            env=backend_env
        )

        # Launch Frontend
        frontend_proc = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=frontend_dir
        )

        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("⚠️ Backend server stopped unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("⚠️ Frontend server stopped unexpectedly.")
                break

    except KeyboardInterrupt:
        print("\n🛑 Shutting down both servers...")
    finally:
        if backend_proc and backend_proc.poll() is None:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                backend_proc.kill()

        if frontend_proc and frontend_proc.poll() is None:
            frontend_proc.terminate()
            try:
                frontend_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                frontend_proc.kill()

        print("✅ Both servers stopped cleanly.")

if __name__ == "__main__":
    main()
