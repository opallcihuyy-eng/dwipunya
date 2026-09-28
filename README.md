# ⚡ Petualangan Energi (Streamlit)

Media pembelajaran interaktif **IPAS Fase B (Kelas IV SD)** dengan topik **Mengubah Bentuk Energi**. Dibuat dengan Python dan [Streamlit](https://streamlit.io), berdasarkan storyboard "Petualangan Energi Bersama Si Volta" untuk siswa usia 9-10 tahun dengan gaya belajar visual dan kinestetik. Alokasi waktu yang dirancang: 2 × 35 menit.

## Fitur Utama

| Layar | Isi |
|---|---|
| 🏠 Cover dan 📖 Petunjuk | Siswa mengisi nama dan mengenal tiga lencana yang akan dikumpulkan |
| 🎬 Apersepsi | Animasi senter dan pertanyaan pemantik: *"Dari mana energi cahaya pada senter berasal?"* |
| 🗺️ Menu Utama | Peta petualangan, bilah kemajuan baterai, dan kunci menu Evaluasi |
| 🏝️ Eksplorasi Materi | Lampu, Setrika, Kipas Angin, Radio, dan Senter, lengkap dengan animasi SVG, tombol ON, dan rantai energi berwarna |
| 🧪 Simulasi Penyelidikan | Lab virtual Sebelum – Tombol – Sesudah dan tabel Catatan Penyelidik (adaptasi LKM) |
| 🎯 Evaluasi Formatif | Drag-and-drop peta konsep 3 level, petunjuk, skor, dan bintang |
| 🪞 Refleksi dan 🏁 Penutup | Emoji, slider, perbandingan dugaan dulu dan sekarang, sertifikat, dan rekap CSV untuk guru |

## Tampilan dan Interaksi

- **Tema cerah:** latar gradien pastel, kartu berbayang, tombol 3D, emoji melayang, dan font Baloo 2 + Nunito.
- **Si Volta bicara:** gelembung ucapan robot pemandu di setiap halaman.
- **Pengatur interaktif:** kecerahan lampu, suhu setrika, kecepatan kipas, dan volume radio mengubah animasi secara langsung.
- **Tebak Cepat:** permainan singkat di Pulau Jelajah dengan skor dan rangkaian jawaban benar beruntun.
- **Pelacak langkah lab:** empat langkah penyelidikan tercentang otomatis saat siswa mengisi dan menghidupkan alat.
- **Balon dan toast** saat lencana diraih, serta sertifikat yang tampil langsung di halaman Penutup.

Menu **Evaluasi terkunci** sampai lencana Eksplorasi (🥇) dan Simulasi (🥈) didapat. Batas ketuntasan: **70 dari 100 poin**.

## Prasyarat

- Python 3.9 atau lebih baru
- Library pada `requirements.txt` (`streamlit` dan `streamlit-sortables`)

## Menjalankan di Komputer

```bash
git clone https://github.com/<username>/petualangan-energi-streamlit.git
cd petualangan-energi-streamlit
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Browser akan terbuka di `http://localhost:8501`. Jika `streamlit-sortables` tidak terpasang, evaluasi otomatis memakai pilihan dropdown sebagai cadangan.

## Mengunggah ke GitHub

```bash
git init
git add .
git commit -m "Versi pertama Petualangan Energi"
git branch -M main
git remote add origin https://github.com/<username>/petualangan-energi-streamlit.git
git push -u origin main
```

## Deploy ke Streamlit Community Cloud

1. Buka [share.streamlit.io](https://share.streamlit.io) dan masuk dengan akun GitHub.
2. Pilih **Create app**, lalu pilih repositori ini, cabang `main`, dan berkas `streamlit_app.py`.
3. Tekan **Deploy**. Setelah selesai, bagikan tautan aplikasi kepada siswa.

## Struktur Repositori

```
petualangan-energi-streamlit/
├── streamlit_app.py        # program utama
├── requirements.txt        # daftar library
├── .streamlit/config.toml  # tema warna ramah anak
├── media/                  # (opsional) apersepsi.mp4
├── README.md
├── LICENSE
└── .gitignore
```

## Cara Memodifikasi

Semua isi materi berada di bagian **DATA** pada `streamlit_app.py`:

- **Menambah alat:** tambahkan entri pada `ALAT`, satu gambar SVG pada `SVG`, dan (jika perlu) satu entri `LAB`.
- **Mengubah soal evaluasi:** edit `LEVEL`. Kunci `slot` berisi pasangan *kotak → kartu yang benar*, `pengecoh` berisi kartu jebakan, dan `poin` adalah poin per kotak.
- **Mengubah batas ketuntasan:** ubah `KKM`.
- **Memakai video apersepsi sendiri:** simpan sebagai `media/apersepsi.mp4`. Aplikasi otomatis memakainya.
- **Mengubah warna tema:** edit `.streamlit/config.toml`.

## Catatan Pedagogis

Aplikasi ini melengkapi, bukan menggantikan, kegiatan langsung. Disarankan menambahkan senter asli saat apersepsi, kipas kertas, dan gerak "Patung Energi" di kelas. Simulasi setrika hanya untuk pengamatan. Ingatkan siswa bahwa alat listrik asli tidak boleh disentuh tanpa pendamping dewasa.

## Lisensi

MIT. Lihat berkas `LICENSE`.
