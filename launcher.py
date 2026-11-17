import os
import shutil
import subprocess
import sys
import time
import urllib.request

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. Deteksi mode Ollama: pakai folder portable jika ada, atau fallback ke Ollama sistem laptop
PORTABLE_OLLAMA = os.path.join(BASE_DIR, "ollama_bin", "ollama.exe")
MODELS_STORE = os.path.join(BASE_DIR, "ollama_store")
env = os.environ.copy()
env["OLLAMA_HOST"] = "127.0.0.1:11434"

if os.path.exists(PORTABLE_OLLAMA):
    OLLAMA_CMD = PORTABLE_OLLAMA
    env["OLLAMA_MODELS"] = MODELS_STORE
    is_portable_ollama = True
else:
    OLLAMA_CMD = shutil.which("ollama")
    is_portable_ollama = False
    if not OLLAMA_CMD:
        print("[ERROR] Ollama tidak ditemukan di folder portable maupun di sistem laptop!")
        print("Silakan install Ollama terlebih dahulu di https://ollama.com")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)

# 2. Cek apakah server Ollama sudah berjalan di port 11434
server = None
try:
    urllib.request.urlopen("http://127.0.0.1:11434", timeout=1)
    print("[Launcher] Mesin Ollama sudah aktif.")
except Exception:
    mode_str = "portable" if is_portable_ollama else "sistem"
    print(f"[Launcher] Menyalakan mesin Ollama ({mode_str})...")
    server = subprocess.Popen(
        [OLLAMA_CMD, "serve"],
        env=env,
        cwd=BASE_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)

# 3. Pastikan model custom 'indri-coder_v2' sudah terdaftar dari Modelfile
MODEL_NAME = "indri-coder_v2"
print(f"[Launcher] Memeriksa model {MODEL_NAME}...")
hasil_list = subprocess.run(
    [OLLAMA_CMD, "list"], env=env, capture_output=True, text=True
)

if MODEL_NAME not in hasil_list.stdout:
    print(f"[Launcher] Merakit model {MODEL_NAME} dari Modelfile (tunggu sebentar)...")
    res_create = subprocess.run(
        [OLLAMA_CMD, "create", MODEL_NAME, "-f", "Modelfile"],
        env=env,
        cwd=BASE_DIR,
    )
    if res_create.returncode != 0:
        print("\n[ERROR] Gagal membuat model! Pastikan file .gguf sudah ada di folder 'models/'.")
        input("Tekan Enter untuk keluar...")
        sys.exit(1)

INDRI_PY = os.path.join(BASE_DIR, "indri.py")
INDRI_EXE = os.path.join(BASE_DIR, "indri.exe")

print("[Launcher] Membuka Indri...\n")
try:
    if os.path.exists(INDRI_PY):
        subprocess.run([sys.executable, INDRI_PY], env=env, cwd=BASE_DIR)
    elif os.path.exists(INDRI_EXE):
        subprocess.run([INDRI_EXE], env=env, cwd=BASE_DIR)
    else:
        print("[ERROR] File indri.py maupun indri.exe tidak ditemukan!")
finally:
    if server is not None:
        print("\n[Launcher] Mematikan mesin Ollama yang dinyalakan launcher...")
        server.terminate()