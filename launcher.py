import os
import subprocess
import sys
import time

if getattr(sys, "frozen", False):
  BASE_DIR = os.path.dirname(sys.executable)
else:
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))

OLLAMA_EXE = os.path.join(BASE_DIR, "ollama_bin", "ollama.exe")
INDRI_EXE = os.path.join(BASE_DIR, "indri.exe")
MODELS_STORE = os.path.join(BASE_DIR, "ollama_store")

if not os.path.exists(OLLAMA_EXE):
  print(f"[ERROR] File tidak ditemukan: {OLLAMA_EXE}")
  input("Tekan Enter untuk keluar...")
  sys.exit(1)

env = os.environ.copy()
env["OLLAMA_MODELS"] = MODELS_STORE
env["OLLAMA_HOST"] = "127.0.0.1:11434"

print("[Launcher] Menyalakan mesin Ollama portable...")
server = subprocess.Popen(
    [OLLAMA_EXE, "serve"],  # <-- Pastikan "serve", bukan "server"
    env=env,
    cwd=BASE_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

time.sleep(3)

MODEL_NAME = "indri-ft"  # Sesuaikan dengan nama model di indri.py
subprocess.run(
    [OLLAMA_EXE, "create", MODEL_NAME, "-f", "Modelfile"],
    env=env,
    cwd=BASE_DIR,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

print("[Launcher] Membuka Indri...\n")
try:
  subprocess.run([INDRI_EXE], cwd=BASE_DIR)
finally:
  print("\n[Launcher] Mematikan mesin Ollama portable...")
  server.terminate()