# 📰 BM25 News Search App

Aplikasi pencarian berita berbasis Flask yang menggunakan algoritma **BM25** untuk menemukan berita paling relevan dari dataset `Summarized_Kompas.csv`.

---

## 🔍 Fitur Utama

- Pencarian berita berbasis kata kunci menggunakan algoritma BM25.
- Tampilan hasil pencarian yang disortir berdasarkan skor relevansi tertinggi.
- Menampilkan informasi berita seperti:
  - Judul
  - Tanggal
  - Ringkasan
  - URL berita asli
  - Status `hoax` (sebagai atribut tambahan dari dataset)

---

## 📁 Struktur Proyek

---

## 🚀 Cara Menjalankan

### 1. Clone Repo & Pindah Direktori

```bash
git clone https://github.com/username/flask_hoax_bm25.git
cd flask_hoax_bm25

python -m venv venv
source venv/bin/activate       # (Linux/macOS)
venv\Scripts\activate          # (Windows)

pip install -r requirements.txt

python run.py

Buka browser dan akses:
http://localhost:5050

📌 Catatan
Aplikasi tidak mendeteksi hoaks secara otomatis, hanya menampilkan kolom hoax dari dataset sebagai informasi tambahan.

Algoritma BM25 digunakan hanya untuk mencocokkan clean_narasi dengan kueri pengguna.

📃 Lisensi
Proyek ini bebas digunakan untuk keperluan pembelajaran, riset, atau modifikasi pribadi. Sertakan atribusi jika digunakan untuk publikasi.
