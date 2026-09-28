"""
Petualangan Energi (versi Streamlit)
Media pembelajaran interaktif IPAS Fase B (Kelas IV SD): Mengubah Bentuk Energi.

Susunan file ini:
  1. DATA       -> materi alat, kondisi lab, level evaluasi (edit di sini untuk mengubah isi)
  2. ANIMASI    -> SVG + CSS animasi untuk tiap alat
  3. TAMPILAN   -> tema cerah, hero, gelembung Si Volta, kartu
  4. HALAMAN    -> satu fungsi per layar storyboard
  5. UTAMA      -> sidebar, navigasi, dan pemanggil halaman
"""
import os
import html
import random

import streamlit as st
import streamlit.components.v1 as components

try:  # drag-and-drop asli; jika belum terpasang, dipakai dropdown sebagai cadangan
    from streamlit_sortables import sort_items
    ADA_DRAG = True
except ImportError:
    ADA_DRAG = False

st.set_page_config(page_title="Petualangan Energi", page_icon="⚡", layout="wide")

# =====================================================================
# 1. DATA
# =====================================================================
# Warna energi: (latar, warna teks). Dipakai konsisten di seluruh media.
WARNA = {
    "kimia": ("#2E7D32", "#FFFFFF"), "listrik": ("#0277BD", "#FFFFFF"),
    "cahaya": ("#FFC107", "#1B2A4A"), "panas": ("#C62828", "#FFFFFF"),
    "gerak": ("#3949AB", "#FFFFFF"), "bunyi": ("#7B1FA2", "#FFFFFF"),
}
IKON = {"kimia": "🟢", "listrik": "⚡", "cahaya": "🟡", "panas": "🔴", "gerak": "🔵", "bunyi": "🟣"}

# Lima alat pada menu Eksplorasi. Tambah alat baru dengan menambah entri di sini
# (dan satu gambar SVG di dictionary SVG pada bagian ANIMASI).
ALAT = {
    "Lampu": {"ikon": "💡", "rantai": ["listrik", "cahaya"],
              "kalimat": "Lampu mengubah energi listrik menjadi energi cahaya.",
              "fakta": "Lampu yang menyala lama juga terasa hangat."},
    "Setrika": {"ikon": "♨️", "rantai": ["listrik", "panas"],
                "kalimat": "Setrika mengubah energi listrik menjadi energi panas.",
                "fakta": "Panas setrika membuat kain kusut menjadi rata."},
    "Kipas Angin": {"ikon": "🌀", "rantai": ["listrik", "gerak"],
                    "kalimat": "Kipas angin mengubah energi listrik menjadi energi gerak.",
                    "fakta": "Baling-baling yang berputar mendorong udara sehingga terasa angin."},
    "Radio": {"ikon": "📻", "rantai": ["listrik", "bunyi"],
              "kalimat": "Radio mengubah energi listrik menjadi energi bunyi.",
              "fakta": "Makin besar volume, makin kuat bunyi yang keluar dari speaker."},
    "Senter": {"ikon": "🔦", "rantai": ["kimia", "listrik", "cahaya"],
               "kalimat": "Baterai pada senter mengubah energi kimia -> energi listrik -> energi cahaya.",
               "fakta": "Ini perubahan berantai: dua tahap perubahan energi."},
}

# Lab virtual: (kondisi awal, kondisi akhir, energi awal, energi akhir, tantangan Si Volta)
LAB = {
    "Senter": ("Gelap", "Terang", "Energi Kimia", "Energi Cahaya",
               "Apa yang terjadi jika baterai dilepas? Coba hilangkan centang baterai!"),
    "Kipas Angin": ("Diam", "Berputar", "Energi Listrik", "Energi Gerak",
                    "Apakah kipas juga terasa hangat? Coba rasakan kipas di rumah!"),
    "Setrika": ("Dingin", "Panas", "Energi Listrik", "Energi Panas",
                "Ingat: di dunia nyata, setrika hanya boleh disentuh orang dewasa!"),
}
OPSI_KONDISI = ["Gelap", "Terang", "Diam", "Berputar", "Dingin", "Panas"]
OPSI_ENERGI = ["Energi Kimia", "Energi Listrik", "Energi Cahaya", "Energi Panas", "Energi Gerak", "Energi Bunyi"]

# Evaluasi drag-and-drop. "slot" = kotak peta konsep -> kartu yang benar.
# "poin" = poin per kotak. Total: 4x10 + 3x10 + 5x6 = 100.
LEVEL = {
    "Level 1 · Cocokkan alat": {"poin": 10, "pengecoh": [], "slot": {
        "💡 Lampu": "Energi Cahaya", "♨️ Setrika": "Energi Panas",
        "🌀 Kipas Angin": "Energi Gerak", "📻 Radio": "Energi Bunyi"}},
    "Level 2 · Rantai senter": {"poin": 10, "pengecoh": [], "slot": {
        "1️⃣ Baterai menyimpan": "Energi Kimia", "2️⃣ Lalu mengalir sebagai": "Energi Listrik",
        "3️⃣ Lampu senter menghasilkan": "Energi Cahaya"}},
    "Level 3 · Peta lengkap": {"poin": 6, "pengecoh": ["Energi Angin", "Energi Air"], "slot": {
        "🔋 Baterai (awal)": "Energi Kimia", "💡 Lampu": "Energi Cahaya", "♨️ Setrika": "Energi Panas",
        "🌀 Kipas Angin": "Energi Gerak", "📻 Radio": "Energi Bunyi"}},
}
KKM = 70  # batas ketuntasan (poin)

LENCANA = {"1": "🥇", "2": "🥈", "3": "🥉"}
H = ["🏠 Cover", "📖 Petunjuk", "🎬 Apersepsi", "🗺️ Menu Utama", "🏝️ Eksplorasi Materi",
     "🧪 Simulasi Penyelidikan", "🎯 Evaluasi", "🪞 Refleksi", "🏁 Penutup"]

# =====================================================================
# 2. ANIMASI (SVG + CSS). Kelas "on" pada pembungkus = alat menyala.
# =====================================================================
CSS = """
body{margin:0;font-family:sans-serif}
.on,.off{background:linear-gradient(180deg,#DFF3FF,#FFFFFF);border-radius:20px}
.sinar,.angin,.uap,.gel,.titik{opacity:0}
.on .sinar{animation:muncul .6s forwards}
@keyframes muncul{to{opacity:@@O@@}}
.baling{transform-origin:150px 85px}
.on .baling{animation:putar @@D@@ linear infinite}
@keyframes putar{to{transform:rotate(360deg)}}
.on .angin{animation:angin .8s linear infinite}
@keyframes angin{0%{opacity:0;transform:translateX(0)}50%{opacity:1}100%{opacity:0;transform:translateX(30px)}}
.gel{transform-box:fill-box;transform-origin:center}
.on .gel{animation:gel @@G@@ ease-out infinite}
.g2{animation-delay:.6s!important}.g3{animation-delay:1.2s!important}
@keyframes gel{0%{opacity:.9;transform:scale(1)}100%{opacity:0;transform:scale(@@S@@)}}
.on .uap{animation:uap 1.6s linear infinite}
.u2{animation-delay:.5s!important}.u3{animation-delay:1s!important}
@keyframes uap{0%{opacity:.9;transform:translateY(0)}100%{opacity:0;transform:translateY(-45px)}}
.alas{fill:#9E9E9E}.on .alas{animation:panas @@P@@ forwards}
@keyframes panas{to{fill:#F44336}}
.suhu{transform-box:fill-box;transform-origin:bottom;transform:scaleY(.15)}
.on .suhu{animation:naik @@P@@ forwards}
@keyframes naik{to{transform:scaleY(1)}}
.on .titik{animation:jalan 1s linear infinite}
.t2{animation-delay:.33s!important}.t3{animation-delay:.66s!important}
@keyframes jalan{0%{opacity:0;transform:translateX(0)}20%{opacity:1}100%{opacity:0;transform:translateX(60px)}}
.kaca{fill:#CFD8DC}.on .kaca{fill:#FFEB3B}
.bat{fill:#C8E6C9}.on .bat{fill:#66BB6A}
"""

SVG = {
    "Lampu": '''<g class="sinar" stroke="#F9A825" stroke-width="5"><line x1="160" y1="25" x2="160" y2="8"/>
<line x1="121" y1="41" x2="109" y2="29"/><line x1="199" y1="41" x2="211" y2="29"/>
<line x1="105" y1="80" x2="88" y2="80"/><line x1="215" y1="80" x2="232" y2="80"/></g>
<circle class="kaca" cx="160" cy="80" r="40" stroke="#90A4AE" stroke-width="3"/>
<path d="M148 95 q6 -20 12 0 q6 -20 12 0" stroke="#F57F17" stroke-width="3" fill="none"/>
<rect x="140" y="118" width="40" height="32" rx="4" fill="#78909C"/>
<rect x="146" y="150" width="28" height="12" rx="3" fill="#546E7A"/>''',
    "Senter": '''<polygon class="sinar" points="240,75 310,25 310,165 240,125" fill="#FFF59D"/>
<rect x="40" y="80" width="160" height="40" fill="#90A4AE" stroke="#546E7A" stroke-width="3"/>
<rect class="bat" x="60" y="87" width="65" height="26" stroke="#2E7D32" stroke-width="2"/>
<text x="92" y="105" font-size="11" text-anchor="middle" fill="#0B2A0F" font-weight="bold">Baterai</text>
<polygon points="200,75 240,65 240,135 200,125" fill="#546E7A"/>
<circle class="kaca" cx="206" cy="100" r="16" stroke="#F9A825" stroke-width="2"/>
<circle class="titik" cx="130" cy="100" r="4" fill="#29B6F6"/>
<circle class="titik t2" cx="130" cy="100" r="4" fill="#29B6F6"/>
<circle class="titik t3" cx="130" cy="100" r="4" fill="#29B6F6"/>''',
    "Kipas Angin": '''<rect x="143" y="130" width="14" height="42" fill="#90A4AE"/>
<rect x="110" y="170" width="80" height="12" rx="4" fill="#78909C"/>
<g class="angin" stroke="#4FC3F7" stroke-width="4"><line x1="235" y1="55" x2="260" y2="55"/>
<line x1="235" y1="85" x2="260" y2="85"/><line x1="235" y1="115" x2="260" y2="115"/></g>
<g class="baling"><ellipse cx="150" cy="45" rx="14" ry="38" fill="#3949AB"/>
<ellipse cx="150" cy="45" rx="14" ry="38" fill="#3949AB" transform="rotate(120 150 85)"/>
<ellipse cx="150" cy="45" rx="14" ry="38" fill="#3949AB" transform="rotate(240 150 85)"/></g>
<circle cx="150" cy="85" r="10" fill="#FFC107"/>
<circle cx="150" cy="85" r="66" fill="none" stroke="#78909C" stroke-width="3"/>''',
    "Setrika": '''<polygon class="alas" points="50,150 240,150 205,112 50,112" stroke="#37474F" stroke-width="3"/>
<polygon points="60,112 205,112 185,80 60,80" fill="#FF8A65" stroke="#37474F" stroke-width="3"/>
<rect x="85" y="50" width="90" height="30" fill="none" stroke="#37474F" stroke-width="6"/>
<circle class="uap" cx="100" cy="105" r="6" fill="none" stroke="#90A4AE" stroke-width="2"/>
<circle class="uap u2" cx="140" cy="105" r="6" fill="none" stroke="#90A4AE" stroke-width="2"/>
<circle class="uap u3" cx="180" cy="105" r="6" fill="none" stroke="#90A4AE" stroke-width="2"/>
<rect x="275" y="30" width="16" height="120" fill="#fff" stroke="#37474F" stroke-width="2"/>
<rect class="suhu" x="278" y="33" width="10" height="114" fill="#F44336"/>''',
    "Radio": '''<circle class="gel" cx="100" cy="105" r="36" fill="none" stroke="#BA68C8" stroke-width="4"/>
<circle class="gel g2" cx="100" cy="105" r="36" fill="none" stroke="#BA68C8" stroke-width="4"/>
<circle class="gel g3" cx="100" cy="105" r="36" fill="none" stroke="#BA68C8" stroke-width="4"/>
<line x1="230" y1="60" x2="285" y2="15" stroke="#546E7A" stroke-width="3"/>
<rect x="45" y="60" width="230" height="90" rx="10" fill="#7E57C2" stroke="#4527A0" stroke-width="3"/>
<circle cx="100" cy="105" r="32" fill="#311B92" stroke="#D1C4E9" stroke-width="2"/>
<circle cx="100" cy="105" r="12" fill="#5E35B1"/>
<circle cx="216" cy="92" r="11" fill="#FFCA28" stroke="#37474F"/>
<circle cx="246" cy="92" r="11" fill="#E0E0E0" stroke="#37474F"/>''',
}


def animasi(alat, nyala, laju=1, tinggi=210):
    """Animasi satu alat. nyala=False -> kondisi awal (mati). laju 1-3 = intensitas
    (kecepatan kipas, suhu setrika, volume radio, kecerahan lampu)."""
    css = (CSS.replace("@@D@@", f"{0.9 / laju:.2f}s").replace("@@P@@", f"{4.5 / laju:.1f}s")
              .replace("@@G@@", f"{2.4 / laju:.2f}s").replace("@@S@@", f"{1.8 + 0.5 * laju:.1f}")
              .replace("@@O@@", f"{0.35 + 0.3 * laju:.2f}"))
    kelas = "on" if nyala else "off"
    components.html(
        f"<style>{css}</style><div class='{kelas}'><svg viewBox='0 0 320 190' width='100%'>{SVG[alat]}</svg></div>",
        height=tinggi)


# =====================================================================
# 3. TAMPILAN: tema cerah, hero, gelembung Si Volta, kartu
# =====================================================================
# Info tambahan untuk mengisi halaman (edit bebas)
ENERGI_INFO = {
    "listrik": ("Energi yang mengalir lewat kabel.", "lampu, kipas, radio, dan setrika di rumah"),
    "cahaya": ("Energi yang membuat kita bisa melihat.", "lampu, senter, dan matahari"),
    "panas": ("Energi yang membuat benda terasa hangat atau panas.", "setrika, kompor, dan matahari"),
    "gerak": ("Energi yang membuat benda berputar atau berpindah.", "kipas berputar dan sepeda yang dikayuh"),
    "bunyi": ("Energi yang membuat kita bisa mendengar.", "radio, bel, dan alat musik"),
    "kimia": ("Energi yang tersimpan di dalam bahan.", "baterai, makanan, dan kayu bakar"),
}
LABEL_LAJU = {  # alat -> (nama pengatur, tiga tingkat)
    "Lampu": ("Kecerahan", ["Redup", "Sedang", "Terang"]), "Setrika": ("Suhu", ["Hangat", "Panas", "Sangat panas"]),
    "Kipas Angin": ("Kecepatan", ["Pelan", "Sedang", "Kencang"]), "Radio": ("Volume", ["Kecil", "Sedang", "Besar"]),
}
TAMBAHAN = {
    "Lampu": "Lampu LED mengubah lebih banyak listrik menjadi cahaya, jadi tidak terlalu panas.",
    "Setrika": "Setrika punya pengatur suhu supaya panasnya tidak berlebihan.",
    "Kipas Angin": "Kipas tidak mendinginkan udara. Angin membuat keringat cepat menguap sehingga kita merasa sejuk.",
    "Radio": "Radio menangkap gelombang radio, lalu mengubahnya menjadi bunyi.",
    "Senter": "Jika baterai habis, artinya energi kimia di dalamnya sudah terpakai.",
}
TIPS = ["Energi tidak hilang, tetapi berubah bentuk!", "Baterai menyimpan energi kimia.",
        "Alat listrik tidak boleh disentuh tanpa pendamping dewasa.", "Kipas berputar karena energi listrik berubah menjadi gerak."]
PAL = [("#FFE0B2", "#F8BBD0"), ("#B3E5FC", "#C8E6C9"), ("#E1BEE7", "#F8BBD0"), ("#FFF9C4", "#FFE0B2"), ("#C8E6C9", "#B3E5FC")]

TEMA_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Nunito:wght@400;700;800&display=swap');
.stApp{background:linear-gradient(135deg,#FFF1E0 0%,#E6F4FF 50%,#F6E8FF 100%);font-family:'Nunito',sans-serif;color:#1B2A4A}
.block-container{padding-top:2rem;max-width:1200px}
h1,h2,h3,h4,h5{font-family:'Baloo 2','Nunito',sans-serif!important;color:#1B2A4A}
[data-testid=stSidebar]{background:linear-gradient(180deg,#FFE3C4 0%,#FFD0E4 55%,#DCD0FF 100%)}
[data-testid=stVerticalBlockBorderWrapper]{background:rgba(255,255,255,.78);border:2px solid #FFD9B3!important;border-radius:22px!important;box-shadow:0 8px 22px rgba(230,74,25,.10)}
.stButton>button,.stDownloadButton>button{background:linear-gradient(135deg,#E64A19,#C2185B);color:#fff;border:0;border-radius:999px;font-weight:800;font-size:19px;padding:.55rem 1.5rem;box-shadow:0 5px 0 #8E1B3F;transition:.15s}
.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-3px);color:#fff}
.stButton>button:active{transform:translateY(2px);box-shadow:0 2px 0 #8E1B3F}
.stButton>button:disabled{background:#CFD8DC;color:#546E7A;box-shadow:none}
div[role=radiogroup]>label{background:#fff;border:2px solid #FFCC99;border-radius:999px;padding:6px 16px;margin:2px 6px 2px 0}
div[role=radiogroup]>label:has(input:checked){background:#FFE0B2;border-color:#E64A19}
.stTabs [data-baseweb=tab]{font-weight:800;font-size:18px}
.hero{display:flex;align-items:center;gap:22px;padding:22px 30px;border-radius:28px;color:#1B2A4A;box-shadow:0 8px 24px rgba(0,0,0,.08);margin-bottom:14px}
.hero h1{margin:0;font-size:2.3rem;line-height:1.1}.hero p{margin:4px 0 0;font-size:1.15rem}
.hero-ikon{font-size:3.6rem;animation:goyang 2.6s ease-in-out infinite}
@keyframes goyang{50%{transform:rotate(-9deg) scale(1.12)}}
.volta{display:flex;align-items:flex-start;gap:14px;margin:8px 0 14px}
.volta-avatar{font-size:2.6rem;background:#fff;border-radius:50%;padding:4px 10px;box-shadow:0 4px 10px rgba(0,0,0,.1);animation:melayang 3s ease-in-out infinite}
.gelembung{background:#fff;border:3px solid #FFB74D;border-radius:20px;padding:12px 18px;font-size:1.1rem;position:relative}
.gelembung:before{content:"";position:absolute;left:-14px;top:18px;border:8px solid transparent;border-right:12px solid #FFB74D}
.kt{border-radius:22px;padding:16px;text-align:center;box-shadow:0 6px 16px rgba(0,0,0,.08);transition:.2s;height:100%}
.kt:hover{transform:translateY(-6px) rotate(-1deg)}
.kt-ikon{font-size:3rem}.kt h4{margin:.2rem 0}.kt p{margin:0;font-size:1rem}
.pil{display:inline-block;padding:3px 12px;border-radius:999px;background:#fff;font-weight:800;font-size:.9rem;margin-top:8px}
.langkah{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0 12px}
.langkah span{padding:6px 14px;border-radius:999px;background:#fff;border:2px dashed #B0BEC5;font-weight:800}
.langkah span.ok{background:#C8E6C9;border:2px solid #2E7D32}
.dekor{position:fixed;font-size:40px;opacity:.22;pointer-events:none;animation:melayang 7s ease-in-out infinite;z-index:0}
@keyframes melayang{50%{transform:translateY(-22px)}}
</style>"""

DEKOR = "".join(f'<span class="dekor" style="left:{x}%;top:{y}%;animation-delay:{d}s">{e}</span>'
                for e, x, y, d in [("⚡", 4, 18, 0), ("💡", 92, 12, 1), ("🔋", 88, 70, 2), ("🌀", 6, 78, 3), ("🎵", 48, 92, 4), ("🔥", 60, 6, 5)])


def hero(judul, sub, ikon, pal=0):
    a, b = PAL[pal % len(PAL)]
    st.markdown(f'<div class="hero" style="background:linear-gradient(120deg,{a},{b})"><div class="hero-ikon">{ikon}</div>'
                f'<div><h1>{judul}</h1><p>{sub}</p></div></div>', unsafe_allow_html=True)


def volta(teks):
    """Gelembung ucapan Si Volta."""
    st.markdown(f'<div class="volta"><div class="volta-avatar">🤖</div><div class="gelembung">{teks}</div></div>',
                unsafe_allow_html=True)


def kartu(ikon, judul, teks, bg="#FFFFFF", extra=""):
    return (f'<div class="kt" style="background:{bg}"><div class="kt-ikon">{ikon}</div><h4>{judul}</h4>'
            f'<p>{teks}</p>{extra}</div>')


def pindah(tujuan):
    """Callback tombol: pindah halaman."""
    st.session_state.hal = tujuan


def tombol_lanjut(tujuan, label="Lanjut ▶"):
    st.button(label, on_click=pindah, args=(tujuan,), key=f"lanjut_{tujuan}_{label}")


def chips(rantai):
    """Rantai energi berwarna: [Kimia] ➜ [Listrik] ➜ [Cahaya]."""
    kotak = []
    for k in rantai:
        bg, fg = WARNA[k]
        kotak.append(f'<span style="background:{bg};color:{fg};padding:8px 14px;border-radius:14px;'
                     f'font-weight:800;font-size:19px;display:inline-block;margin:4px">{IKON[k]} Energi {k.capitalize()}</span>')
    st.markdown(" ➜ ".join(kotak), unsafe_allow_html=True)


def energi(k):
    return f"Energi {k.capitalize()}"


def raih(k, nama):
    """Memberi lencana sekali, lalu memicu balon dan pesan pada run berikutnya."""
    s = st.session_state
    if k not in s.lencana:
        s.lencana.add(k)
        s.efek = "balon"
        s.flash = ("success", f"{LENCANA[k]} Lencana {nama} kamu dapatkan! Hebat!")
        st.rerun()


# =====================================================================
# 4. HALAMAN
# =====================================================================
def hal_cover():
    s = st.session_state
    hero("Petualangan Energi", "Bersama Si Volta · IPAS Kelas IV · Mengubah Bentuk Energi", "⚡", 0)
    volta("Halo, Penjelajah Energi! Aku Si Volta 🤖. Hari ini kita akan menyelidiki bagaimana energi bisa "
          "<b>berubah bentuk</b>. Siap?")
    kiri, kanan = st.columns([3, 2])
    with kiri, st.container(border=True):
        st.subheader("✏️ Siapa namamu?")
        s.nama = st.text_input("Namaku", value=s.nama, placeholder="Tulis namamu di sini", label_visibility="collapsed")
        if s.nama:
            st.success(f"Halo, {s.nama}! Yuk mulai petualangan! 🚀")
        tombol_lanjut(H[1], "MULAI PETUALANGAN ▶")
        st.markdown("**Yang akan kamu lakukan:** 🎬 tonton · 🔍 jelajahi · 🧪 selidiki · 🎮 main")
    with kanan, st.container(border=True):
        st.subheader("🏅 Lencana yang bisa kamu dapat")
        for k, n, t in [("1", "Penjelajah", "kenali lima alat"), ("2", "Penyelidik", "selesaikan tiga lab"),
                        ("3", "Ahli Energi", "menangkan peta konsep")]:
            st.markdown(f"### {LENCANA[k]} {n}\n{t}")


def hal_petunjuk():
    hero("Petunjuk Misi", "Kenali dulu misimu, lalu kumpulkan tiga lencana!", "📖", 1)
    misi = [("🎬", "Tonton", "Lihat animasi senter menyala.", "#FFE0B2"), ("🔍", "Jelajahi", "Kenali lima alat dan energinya.", "#B3E5FC"),
            ("🧪", "Selidiki", "Catat energi awal dan akhir.", "#C8E6C9"), ("🎮", "Main", "Lengkapi peta konsep energi.", "#E1BEE7")]
    for kol, (i, j, t, bg) in zip(st.columns(4), misi):
        kol.markdown(kartu(i, j, t, bg), unsafe_allow_html=True)
    st.markdown("### 🎨 Kenalan dengan enam bentuk energi (klik tiap tombol!)")
    for kol, k in zip(st.columns(6), WARNA):
        with kol.popover(f"{IKON[k]} {k.capitalize()}", use_container_width=True):
            st.markdown(f"**Energi {k.capitalize()}**")
            st.write(ENERGI_INFO[k][0])
            st.caption("Contoh: " + ENERGI_INFO[k][1])
    volta("Aku selalu memakai <b>warna yang sama</b> untuk setiap energi, supaya mudah diingat. Perhatikan ya!")
    tombol_lanjut(H[2])


def hal_apersepsi():
    s = st.session_state
    hero("Apersepsi: Menyalakan Senter", "Perhatikan baik-baik, lalu tebak jawabannya!", "🔦", 3)
    kiri, kanan = st.columns(2)
    with kiri, st.container(border=True):
        if os.path.exists("media/apersepsi.mp4"):  # letakkan video sendiri di sini jika ada
            st.video("media/apersepsi.mp4")
        else:
            st.markdown("##### 🎬 Animasi: kamar gelap, senter dinyalakan")
            nyala = st.toggle("⏻ Geser untuk menyalakan senter", key="aper_on")
            animasi("Senter", nyala, 2)
            st.caption("Amati baterai, titik listrik, dan lampu senter." if nyala else "Kamarnya gelap. Nyalakan senternya!")
    with kanan, st.container(border=True):
        volta("Dari mana <b>energi cahaya</b> pada senter berasal?")
        pilihan = ["🔋 Baterai", "🌞 Matahari", "💡 Lampunya sendiri", "❓ Belum tahu"]
        idx = pilihan.index(s.dugaan) if s.dugaan in pilihan else None
        d = st.radio("Dugaanku:", pilihan, index=idx)
        if d:
            s.dugaan = d
            st.info("Menarik dugaanmu! Kita buktikan nanti ya. 🤖")
        st.caption("Semua jawaban diterima. Ini baru dugaan awal.")
    with st.expander("💡 Tahukah kamu?"):
        st.write("Baterai menyimpan **energi kimia**. Saat senter dinyalakan, energi itu berubah menjadi energi listrik, "
                 "lalu menjadi cahaya. Jawabannya akan kita buktikan di lab!")
    tombol_lanjut(H[3])


def hal_menu():
    s = st.session_state
    hero("Peta Petualangan", "Pilih pulau yang ingin kamu kunjungi", "🗺️", 2)
    with st.container(border=True):
        st.markdown("**🔋 Baterai kemajuan**")
        st.progress(len(s.lencana) / 3, text=f"{len(s.lencana)} dari 3 lencana")
        st.markdown('<span style="font-size:2.4rem">' + " ".join(LENCANA[k] if k in s.lencana else "⚪" for k in "123") + "</span>",
                    unsafe_allow_html=True)
    terbuka = {"1", "2"} <= s.lencana
    lokasi = [("🏝️", "Pulau Jelajah", "Kenali 5 alat dan main Tebak Cepat", H[4], True, "#FFE0B2", "1" in s.lencana),
              ("🧪", "Lab Penyelidik", "Selidiki senter, kipas, dan setrika", H[5], True, "#B3E5FC", "2" in s.lencana),
              ("🎯", "Arena Peta Konsep", "Seret kartu, lengkapi peta energi", H[6], terbuka, "#E1BEE7", "3" in s.lencana),
              ("🪞", "Cermin Refleksi", "Ceritakan yang kamu pelajari", H[7], True, "#C8E6C9", bool(s.refleksi))]
    for kol, (i, j, t, tujuan, buka, bg, selesai) in zip(st.columns(4), lokasi):
        status = "✔ Selesai" if selesai else ("🔒 Terkunci" if not buka else "Ayo mulai!")
        kol.markdown(kartu(i, j, t, bg, f'<span class="pil">{status}</span>'), unsafe_allow_html=True)
        kol.button("Masuk ▶" if buka else "🔒 Terkunci", on_click=pindah, args=(tujuan,), disabled=not buka,
                   key=f"menu_{tujuan}", use_container_width=True)
    if not terbuka:
        volta("Arena Peta Konsep terbuka setelah kamu mendapat 🥇 dan 🥈. Semangat!")
    elif len(s.lencana) == 3 and s.refleksi:
        tombol_lanjut(H[8], "Ke Penutup 🏁")


def tab_jelajah():
    s = st.session_state
    a = st.radio("Pilih kartu alat:", list(ALAT), horizontal=True, key="kartu_alat",
                 format_func=lambda x: f"{'✔ ' if x in s.dibuka else ''}{ALAT[x]['ikon']} {x}")
    s.dibuka.add(a)
    d = ALAT[a]
    kiri, kanan = st.columns([5, 6])
    with kiri, st.container(border=True):
        st.markdown(f"##### {d['ikon']} {a}")
        nyala = st.toggle("⏻ Tekan ON", key=f"eks_{a}")
        laju = 1
        if a in LABEL_LAJU:
            nama, tingkat = LABEL_LAJU[a]
            laju = tingkat.index(st.select_slider(nama, options=tingkat, value=tingkat[1], key=f"laju_{a}")) + 1
        animasi(a, nyala, laju)
        st.caption("👆 Tekan ON, lalu ubah pengaturannya!" if not nyala else "Lihat energinya bergerak!")
    with kanan, st.container(border=True):
        chips(d["rantai"])
        st.markdown(f"### {d['kalimat']}")
        volta(d["fakta"])
        st.info("💡 Tahukah kamu? " + TAMBAHAN[a])
        if a == "Setrika":
            st.warning("⚠️ Setrika hanya boleh disentuh orang dewasa!")
        st.progress(len(s.dibuka) / len(ALAT), text=f"Kartu dibuka: {len(s.dibuka)} dari {len(ALAT)}")


def soal_baru():
    """Menyiapkan soal Tebak Cepat: satu alat + empat pilihan energi."""
    t = st.session_state.tebak
    t["alat"] = random.choice(list(ALAT))
    benar = ALAT[t["alat"]]["rantai"][-1]
    lain = [k for k in WARNA if k != benar]
    t["opsi"] = random.sample([benar] + random.sample(lain, 3), 4)
    t["hasil"] = None


def jawab(pilihan):
    t = st.session_state.tebak
    benar = ALAT[t["alat"]]["rantai"][-1]
    t["main"] += 1
    if pilihan == benar:
        t["skor"] += 1
        t["streak"] += 1
        t["hasil"] = ("ok", f"🎉 Benar! {ALAT[t['alat']]['kalimat']}")
        st.toast("Benar! ⭐", icon="🎉")
    else:
        t["streak"] = 0
        t["hasil"] = ("salah", f"Hampir! Jawabannya {energi(benar)}. Coba soal berikutnya ya!")


def tab_tebak():
    t = st.session_state.tebak
    if t["alat"] is None:
        soal_baru()
    m1, m2, m3 = st.columns(3)
    m1.metric("⭐ Benar", t["skor"])
    m2.metric("🔥 Beruntun", t["streak"])
    m3.metric("🎯 Dimainkan", t["main"])
    a = t["alat"]
    with st.container(border=True):
        st.markdown(f"<h2 style='text-align:center'>{ALAT[a]['ikon']} {a}</h2>"
                    "<p style='text-align:center;font-size:1.2rem'>Alat ini menghasilkan energi apa?</p>", unsafe_allow_html=True)
        for kol, k in zip(st.columns(4), t["opsi"]):
            kol.button(f"{IKON[k]} {k.capitalize()}", key=f"tb_{k}", on_click=jawab, args=(k,),
                       disabled=t["hasil"] is not None, use_container_width=True)
        if t["hasil"]:
            (st.success if t["hasil"][0] == "ok" else st.warning)(t["hasil"][1])
            st.button("Soal berikutnya ▶", on_click=soal_baru, key="tb_next")


def tab_ringkasan():
    s = st.session_state
    with st.container(border=True):
        st.subheader("📋 Ringkasan Rantai Energi")
        if s.dibuka:  # tabel terisi otomatis dari kartu yang sudah dibuka
            st.table([{"Alat": f"{ALAT[x]['ikon']} {x}", "Energi awal": energi(ALAT[x]["rantai"][0]),
                       "Energi akhir": energi(ALAT[x]["rantai"][-1])} for x in ALAT if x in s.dibuka])
        if len(s.dibuka) == len(ALAT):
            if "1" in s.lencana:
                st.success("🥇 Lencana Penjelajah sudah kamu dapat!")
            elif st.button("Aku paham! 🥇"):
                raih("1", "Penjelajah")
        else:
            st.info(f"Buka semua kartu alat ({len(s.dibuka)} dari {len(ALAT)}) di tab Jelajah untuk mendapat lencana.")


def hal_eksplorasi():
    hero("Pulau Jelajah", "Jelajahi alat, ubah pengaturannya, lalu uji dirimu!", "🏝️", 4)
    t1, t2, t3 = st.tabs(["🔍 Jelajah alat", "🎮 Tebak cepat", "📋 Ringkasan"])
    with t1:
        tab_jelajah()
    with t2:
        tab_tebak()
    with t3:
        tab_ringkasan()
    tombol_lanjut(H[5], "Ke Lab Penyelidik ▶")


def hal_simulasi():
    s = st.session_state
    hero("Lab Penyelidik", "Selidiki apa yang terjadi saat alat dihidupkan!", "🧪", 1)
    with st.expander("📮 Surat Misi: baca dulu", expanded=not s.lab_selesai):
        st.markdown("1. Amati kondisi awal  \n2. Hidupkan alat  \n3. Amati kondisi akhir  \n4. Catat bentuk energinya")
    lab = st.radio("Pilih pintu lab:", list(LAB), horizontal=True,
                   format_func=lambda x: f"{'✅ ' if x in s.lab_selesai else ''}{ALAT[x]['ikon']} {x}")
    awal_k, akhir_k, e_awal, e_akhir, tantangan = LAB[lab]
    pel = st.empty()  # pelacak langkah, diisi setelah semua isian dibaca

    k1, k2, k3 = st.columns([3, 2, 3])
    with k1, st.container(border=True):
        st.markdown('<span class="pil" style="background:#FFE0B2">🌑 SEBELUM</span>', unsafe_allow_html=True)
        animasi(lab, False)
        p_awal = st.selectbox("Kondisi awal:", OPSI_KONDISI, index=None, placeholder="Pilih kata...", key=f"aw_{lab}")
    with k2, st.container(border=True):
        st.markdown('<span class="pil" style="background:#FFF9C4">🎛️ TOMBOL</span>', unsafe_allow_html=True)
        pasang = st.checkbox("🔋 Pasang baterai", key="pasang") if lab == "Senter" else True
        nyala = st.toggle("⏻ Hidupkan alat", key=f"on_{lab}", disabled=not pasang) and pasang
        if not pasang:
            st.caption("Pasang baterai dulu ya!")
        elif nyala:
            st.success("Alat menyala!")
            chips(ALAT[lab]["rantai"])
    with k3, st.container(border=True):
        st.markdown('<span class="pil" style="background:#C8E6C9">🌟 SESUDAH</span>', unsafe_allow_html=True)
        animasi(lab, nyala, 2)
        p_akhir = st.selectbox("Kondisi akhir:", OPSI_KONDISI, index=None, placeholder="Pilih kata...",
                               key=f"ak_{lab}", disabled=not nyala)

    with st.container(border=True):
        st.markdown("#### 📒 Catatan Penyelidik")
        c1, c2 = st.columns(2)
        p_ea = c1.selectbox("Energi awal:", OPSI_ENERGI, index=None, placeholder="Pilih...", key=f"ea_{lab}")
        p_ek = c2.selectbox("Energi akhir:", OPSI_ENERGI, index=None, placeholder="Pilih...", key=f"ek_{lab}")
        if st.button("✅ Periksa catatan", key=f"cek_{lab}"):
            if (p_awal, p_akhir, p_ea, p_ek) == (awal_k, akhir_k, e_awal, e_akhir):
                s.lab_selesai.add(lab)
                s.flash = ("success", f"Stempel ✅ Catatan {lab} benar! Hebat!")
                st.rerun()
            else:
                st.warning("Hampir! Coba lagi ya! Hidupkan alatnya dan amati dengan teliti.")

    langkah = [("1 Amati awal", bool(p_awal)), ("2 Hidupkan", nyala), ("3 Amati akhir", bool(p_akhir)),
               ("4 Catat energi", bool(p_ea and p_ek))]
    pel.markdown('<div class="langkah">' + "".join(
        f'<span class="{"ok" if ok else ""}">{"✅" if ok else "⬜"} {t}</span>' for t, ok in langkah) + "</div>",
        unsafe_allow_html=True)
    volta(f"<b>Tantangan:</b> {tantangan}")

    if s.lab_selesai >= set(LAB):
        raih("2", "Penyelidik")
        st.success("🥈 Lencana Penyelidik sudah kamu dapat!")
        with st.container(border=True):
            st.markdown("#### 6e · Kesimpulan penyelidikan")
            st.table([{"Alat": a, "Energi awal": LAB[a][2], "Energi akhir": LAB[a][3]} for a in LAB])
            st.info("Energi cahaya pada senter berasal dari **energi kimia** pada baterai. 🔋 ➜ ⚡ ➜ 💡")
        tombol_lanjut(H[3], "Ke Peta Petualangan ▶")


def papan(nama):
    """Papan seret-lepas. Mengembalikan {nama_kotak: [kartu di dalamnya]}."""
    s = st.session_state
    lv = LEVEL[nama]
    if nama not in s.kartu:  # acak urutan kartu satu kali per sesi
        k = list(lv["slot"].values()) + lv["pengecoh"]
        random.shuffle(k)
        s.kartu[nama] = k
    kartu_lv = s.kartu[nama]
    if ADA_DRAG:
        wadah = [{"header": "🧰 Gudang kartu", "items": list(kartu_lv)}] + \
                [{"header": h, "items": []} for h in lv["slot"]]
        hasil = sort_items(wadah, multi_containers=True, key=f"dd_{nama}")
        return {w["header"]: w["items"] for w in hasil[1:]}
    st.caption("Mode pilihan (pasang streamlit-sortables untuk seret-lepas).")
    isi = {}
    for h in lv["slot"]:
        p = st.selectbox(h, ["-"] + kartu_lv, key=f"sb_{nama}_{h}")
        isi[h] = [] if p == "-" else [p]
    return isi


def hal_evaluasi():
    s = st.session_state
    hero("Arena Peta Konsep", "Lengkapi rantai energi dengan menyeret kartu!", "🎯", 2)
    if not {"1", "2"} <= s.lencana:
        st.warning("🔒 Selesaikan Eksplorasi (🥇) dan Simulasi (🥈) dulu ya!")
        return
    total = sum(s.skor.values())
    with st.container(border=True):
        cols = st.columns(len(LEVEL) + 1)
        for kol, n in zip(cols, LEVEL):
            kol.metric(n.split(" · ")[0], s.skor.get(n, "—"))
        cols[-1].metric("🏆 Total", f"{total} / 100")
        st.progress(min(total, 100) / 100, text=f"Batas tuntas: {KKM} poin")
    nama = st.radio("Pilih level:", list(LEVEL), horizontal=True)
    lv = LEVEL[nama]
    volta("Seret kartu dari <b>gudang</b> ke kotak yang tepat. Kartu jebakan juga ada, hati-hati ya!" if lv["pengecoh"]
          else "Seret kartu dari <b>gudang</b> ke kotak yang tepat.")
    with st.container(border=True):
        isi = papan(nama)

    kiri, kanan = st.columns(2)
    if kiri.button("✅ Periksa jawaban", key=f"cek_{nama}"):
        benar = [h for h, jw in lv["slot"].items() if isi.get(h) == [jw]]
        s.skor[nama] = len(benar) * lv["poin"]
        for h in lv["slot"]:
            st.success(f"{h} ✔") if h in benar else st.warning(f"{h}: Hampir! Coba lagi ya!")
        salah = {k for h in lv["slot"] for k in isi.get(h, []) if k in lv["pengecoh"]}
        if salah:
            st.info(f"{', '.join(salah)} bukan jawaban di peta ini. Angin dan air bukan bentuk energi pada alat-alat ini.")
    dipakai = s.hint.get(nama, 0)
    if kanan.button("💡 Petunjuk", key=f"pt_{nama}", disabled=dipakai >= 2):
        s.hint[nama] = dipakai + 1
        belum = [h for h, jw in lv["slot"].items() if isi.get(h) != [jw]]
        if belum:
            k = lv["slot"][belum[0]].split()[-1].lower()
            st.info(f"Kotak '{belum[0]}' butuh kartu berwarna {IKON[k]}")
        st.caption(f"Sisa petunjuk level ini: {2 - s.hint[nama]}")

    if len(s.skor) == len(LEVEL):
        bintang = 3 if total >= 90 else 2 if total >= KKM else 1
        with st.container(border=True):
            st.markdown(f"### Hasil: {'⭐' * bintang}{'☆' * (3 - bintang)}")
            if total >= KKM:
                raih("3", "Ahli Energi")
                st.success("🥉 Lencana Ahli Energi! Kamu tuntas!")
                tombol_lanjut(H[7], "Ke Cermin Refleksi ▶")
            else:
                st.warning("Ayo belajar lagi sedikit, lalu coba lagi!")
                tombol_lanjut(H[4], "📚 Belajar lagi")


def hal_refleksi():
    s = st.session_state
    r = s.refleksi
    hero("Cermin Refleksi", "Ceritakan apa yang kamu rasakan dan pelajari", "🪞", 0)
    kiri, kanan = st.columns([3, 2])
    with kiri, st.container(border=True):
        rasa = st.radio("Bagaimana perasaanmu belajar hari ini?", ["😄 Seru", "🙂 Biasa", "😕 Sulit"],
                        horizontal=True, index=None)
        if rasa:
            r["rasa"] = rasa
        r["paham"] = st.slider("Seberapa paham kamu tentang perubahan energi? (0 = belum, 10 = paham banget)",
                               0, 10, r.get("paham", 5))
        fav = st.selectbox("Alat mana yang paling menarik? ⭐", list(ALAT), index=None, placeholder="Pilih alat...")
        if fav:
            r["fav"] = fav
        r["baru"] = st.text_input("Satu hal baru yang kupelajari…", value=r.get("baru", ""))
        r["rumah"] = st.text_input("Alat di rumahku yang mengubah energi adalah…", value=r.get("rumah", ""))
    with kanan, st.container(border=True):
        st.subheader("🔄 Dulu dan sekarang")
        st.markdown(kartu("🤔", "Dulu aku kira", s.dugaan or "belum menjawab", "#FFE0B2"), unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(kartu("💡", "Sekarang aku tahu", "energi cahaya senter berasal dari energi kimia pada baterai 🔋", "#C8E6C9"),
                    unsafe_allow_html=True)
    tombol_lanjut(H[8])


def sertifikat_html(nama, lencana):
    """Sertifikat untuk diunduh (berkas HTML mandiri)."""
    lencana_teks = " ".join(LENCANA[k] for k in sorted(lencana)) or "-"
    return ("<html><meta charset='utf-8'><body style=\"font-family:sans-serif;text-align:center;"
            "border:12px double #FF7043;padding:40px\"><h1>🏅 Sertifikat Penyelidik Energi</h1>"
            f"<p>Diberikan kepada</p><h2>{html.escape(nama) or 'Penjelajah Energi'}</h2>"
            "<p>yang telah menyelesaikan petualangan Mengubah Bentuk Energi</p>"
            f"<p style='font-size:44px'>{lencana_teks}</p><p>Si Volta ⚡</p></body></html>")


def hal_penutup():
    s = st.session_state
    hero("Penutup", "Petualanganmu selesai. Terima kasih sudah belajar!", "🏁", 3)
    if not s.balon:
        st.balloons()
        s.balon = True
    nama = html.escape(s.nama) or "Penjelajah Energi"
    lencana = " ".join(LENCANA[k] for k in sorted(s.lencana)) or "—"
    st.markdown(
        '<div style="background:linear-gradient(135deg,#FFF9C4,#FFE0B2);border:8px double #E64A19;border-radius:24px;'
        'padding:28px;text-align:center"><div style="font-size:3rem">🏅</div><h2>Sertifikat Penyelidik Energi</h2>'
        f'<p>Diberikan kepada</p><h1 style="color:#C2410C">{nama}</h1>'
        '<p>yang telah menyelesaikan petualangan Mengubah Bentuk Energi</p>'
        f'<div style="font-size:3rem">{lencana}</div><p><b>Si Volta ⚡</b></p></div>', unsafe_allow_html=True)
    volta("Energi tidak hilang, tetapi <b>berubah bentuk</b>. <b>Misi Rumah:</b> cari 3 alat lain di rumahmu dan tebak "
          "perubahan energinya!")
    r = s.refleksi
    rekap = ("Nama,Level 1,Level 2,Level 3,Total,Perasaan,Pemahaman(0-10)\n"
             f"{s.nama},{','.join(str(s.skor.get(n, 0)) for n in LEVEL)},{sum(s.skor.values())},"
             f"{r.get('rasa', '')},{r.get('paham', '')}\n")
    k1, k2, k3 = st.columns(3)
    k1.download_button("🏅 Unduh sertifikat", sertifikat_html(s.nama, s.lencana), "sertifikat.html", "text/html")
    k2.download_button("📊 Rekap untuk guru (CSV)", rekap, "rekap_siswa.csv", "text/csv")
    k3.button("🔁 Main lagi", on_click=st.session_state.clear)


# =====================================================================
# 5. UTAMA
# =====================================================================
PETA = {H[0]: hal_cover, H[1]: hal_petunjuk, H[2]: hal_apersepsi, H[3]: hal_menu, H[4]: hal_eksplorasi,
        H[5]: hal_simulasi, H[6]: hal_evaluasi, H[7]: hal_refleksi, H[8]: hal_penutup}


def init():
    """Data sesi disimpan di variabel biasa agar tidak hilang saat pindah halaman."""
    awal = {"hal": H[0], "nama": "", "dugaan": "", "dibuka": set(), "lencana": set(), "lab_selesai": set(),
            "skor": {}, "hint": {}, "kartu": {}, "refleksi": {}, "balon": False, "flash": None, "efek": None,
            "tip": random.choice(TIPS),
            "tebak": {"skor": 0, "streak": 0, "main": 0, "alat": None, "opsi": [], "hasil": None}}
    for k, v in awal.items():
        st.session_state.setdefault(k, v)


def sidebar():
    s = st.session_state
    with st.sidebar:
        st.markdown('<div style="text-align:center"><div style="font-size:64px">🤖</div><h3>Si Volta</h3></div>',
                    unsafe_allow_html=True)
        st.caption(f"Halo, {s.nama or 'Penjelajah'}!")
        st.radio("Menu", H, key="hal")
        st.progress(len(s.lencana) / 3, text=f"🔋 {len(s.lencana)} dari 3 lencana")
        st.markdown("### " + " ".join(LENCANA[k] if k in s.lencana else "⚪" for k in "123"))
        st.info("💡 " + s.tip)


def main():
    init()
    st.markdown(TEMA_CSS + DEKOR, unsafe_allow_html=True)
    sidebar()
    s = st.session_state
    if s.flash:  # pesan singkat setelah rerun
        getattr(st, s.flash[0])(s.flash[1])
        s.flash = None
    if s.efek == "balon":
        st.balloons()
        s.efek = None
    PETA[s.hal]()


main()
