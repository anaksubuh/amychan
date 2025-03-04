import streamlit as st
import json
import requests
import base64
import toml
import pandas as pd
import os

#######################################################################################################

st.set_page_config(
    page_title='PSS K3 A',
    page_icon='logo.png',
    #layout='wide',  
    initial_sidebar_state='expanded',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': 'https://www.extremelycoolapp.com/bug',
         'About': '# This is a header. This is an *extremely* cool app!'
    }
)

# Load file config
config = toml.load(".streamlit/config.toml")

# Terapkan tema dari config
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {config["theme"]["backgroundColor"]};
            background-image: url('.streamlit/gg.png');
            background-size: cover;
            color: {config["theme"]["textColor"]};
            font-family: {config["theme"]["font"]};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
bin_str = get_base64('.streamlit/gg.png')

page_bg_img = '''
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
}
</style>
'''% bin_str
st.markdown(page_bg_img, unsafe_allow_html=True)

#######################################################################################################

# 🔹 Token & Repo Info
TOKEN_FILE = "D:\\Master Amy\\github_token.json"

GITHUB_TOKEN = None

# Coba baca token dari file
if os.path.exists(TOKEN_FILE):
    try:
        with open(TOKEN_FILE, "r") as file:
            token_data = json.load(file)
            GITHUB_TOKEN = token_data.get("GITHUB_TOKEN", None)
    except Exception as e:
        st.error(f"❌ Gagal membaca file token! Error: {e}")
else:
    #st.warning("⚠️ File github_token.json tidak ditemukan! Mencoba membaca dari Secrets Streamlit...")
    pass

# Jika file tidak ada atau gagal dibaca, ambil dari Secrets Streamlit
if not GITHUB_TOKEN:
    try:
        GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
        #st.success("✅ Token berhasil diakses dari Secrets Streamlit!")
        print("✅ API : TRUE")
    except Exception as e:
        st.error(f"❌ API : FALSE . Error: {e}")

# Pastikan token tersedia sebelum lanjut
if not GITHUB_TOKEN:
    st.stop()

# Info repo GitHub
REPO_OWNER = "anaksubuh"
REPO_NAME = "amychan"
FILE_PATH = "data.json"

# Coba fetch data dari GitHub
headers = {"Authorization": f"token {GITHUB_TOKEN}"}
url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"

# 🔹 Headers dengan Format yang Benar
headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

# 🔹 Fungsi Membaca Data dari GitHub
def read_github_data():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_info = response.json()
        file_content = base64.b64decode(file_info["content"]).decode("utf-8")
        return json.loads(file_content)
    elif response.status_code == 404:
        return []  # Jika file tidak ada, kembalikan list kosong
    else:
        st.error(f"❌ Gagal mengambil data! Status code: {response.status_code}, Response: {response.text}")
        return []

# 🔹 Fungsi Menyimpan Data ke GitHub
def save_github_data(new_data):
    existing_data = read_github_data()

    # Cek Duplikasi
    for data in existing_data:
        if (
            data["Nama"].lower() == new_data["Nama"].lower()
            and data["Jurusan"].lower() == new_data["Jurusan"].lower()
            and data["Fakultas"].lower() == new_data["Fakultas"].lower()
            and data["Universitas"].lower() == new_data["Universitas"].lower()
        ):
            st.warning("⚠️ Data sudah ada! Tidak perlu ditambahkan lagi.")
            st.session_state.page = 4
            return

    # Tambahkan Data Baru
    existing_data.append(new_data)
    updated_content = json.dumps(existing_data, indent=4)
    encoded_content = base64.b64encode(updated_content.encode()).decode()

    # Ambil SHA untuk Update File
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha", "")
    elif response.status_code == 404:
        sha = ""  # Jika file tidak ada, akan dibuat baru
    else:
        st.error(f"❌ Gagal mengambil SHA file: {response.text}")
        return

    # Payload untuk Update File di GitHub
    payload = {
        "message": "Menambah data baru",
        "content": encoded_content,
        "sha": sha
    }

    save_response = requests.put(url, headers=headers, data=json.dumps(payload))

    if save_response.status_code in [200, 201]:
        st.session_state.page = 3
    else:
        st.error(f"❌ Gagal menyimpan data! Status: {save_response.status_code}, Response: {save_response.text}")

# 🔹 Simpan status halaman dengan session state
if "page" not in st.session_state:
    st.session_state.page = 1

# 🔹 Halaman 1: Form Data Diri
if st.session_state.page == 1:

    st.markdown("<h1 style='text-align: center;'>KUISIONER TERKAIT MOTIVASI BELAJAR MAHASISWA</h1>", unsafe_allow_html=True)
    st.markdown("<h6 >Kuesioner ini bertujuan untuk mengukur tingkat motivasi belajar mahasiswa, termasuk faktor internal dan eksternal yang memengaruhinya. Respon yang diberikan akan digunakan untuk memahami pola belajar serta menemukan strategi yang dapat meningkatkan semangat dan efektivitas belajar mahasiswa.</h6>", unsafe_allow_html=True)

    nama = st.text_input("Nama :")
    jurusan = st.text_input("Jurusan :")
    fakultas = st.text_input("Fakultas :")
    universitas = st.text_input("Universitas :")
    
    if st.button("Berikutnya"):
        if nama and jurusan and fakultas and universitas:
            st.session_state.nama = nama 
            st.session_state.jurusan = jurusan
            st.session_state.fakultas = fakultas
            st.session_state.universitas = universitas
            st.session_state.page = 2
        else:
            st.warning("Silakan isi semua bidang terlebih dahulu!")

# 🔹 Halaman 2: Pertanyaan Utama
elif st.session_state.page == 2:
    st.markdown("<h2 >Evaluasi Kebiasaan dan Motivasi Belajar</h2>", unsafe_allow_html=True)
    st.info('PILIHAN : 1.Sangat Tidak Setuju | 2.Tidak Setuju | 3.Netral | 4.Setuju | 5.Sangat Setuju', icon="ℹ️")
    pertanyaan_slider = [
        "1. Saya selalu berusaha dengan sungguh² untuk meningkatkan pemahaman belajar di kelas",
        "2. Saya selalu berusaha menyelesaikan tantangan akademik yang sulit",
        "3. Bagi saya kemajuan dalam mencapai tugas akademik sangat penting",
        "4. Saya berusaha untuk mencapai target akademik",
        "5. Saya merasa puas ketika berhasil menyelesaikan tugas atau ujian yg sulit",
        "6. Saya termotivasi oleh persaingan akademik dengan teman² sekelas",
        "7. Saya merasa puas saat mendapatkan nilai lebih tinggi dibandingkan teman²",
        "8. Saya merasa terdorong untuk berprestasi lebih baik",
        "9. Saya aktif dalam menyampaikan pendapat secara langsung",
        "10. Saya aktif dalam diskusi kelompok",
        "11. Cara belajar saya mempengaruhi teman² dalam menyelesaikan tugas",
        "12. Saya selalu berinteraksi dengan teman² dan dosen (ya atau tidak)",
        "13. Menurut saya pertemanan penting dalam perkuliahan",
        "14. Saya merasa lebih nyaman belajar sendiri dibanding belajar kelompok",
    ]
    
    jawaban = {f"pertanyaan{i+1}": st.slider(f"{i+1}. {p}", 1, 5, 3, 1) for i, p in enumerate(pertanyaan_slider)}
    jawaban["pertanyaan15"] = st.radio("15. Saya lebih suka belajar dengan cara praktis", ["YA", "TIDAK"])
    jawaban["pertanyaan16"] = st.text_area("16. Bagaimana cara meningkatkan motivasi belajar Anda?", placeholder="Tuliskan pendapat Anda...")
    
    if st.button("✅ SUBMIT"):
        data = {
            "Nama": st.session_state.get("nama", ""),
            "Jurusan": st.session_state.get("jurusan", ""),
            "Fakultas": st.session_state.get("fakultas", ""),
            "Universitas": st.session_state.get("universitas", ""),
            "Jawaban": jawaban,
        }
        save_github_data(data)

# 🔹 Halaman 3: Konfirmasi Data Berhasil Disimpan
elif st.session_state.page == 3:
    st.success('✅Terima kasih sudah mengisi form ini, semoga harimu menyenangkan!')

# 🔹 Halaman 4: Data Sudah Ada
elif st.session_state.page == 4:
    st.warning("⚠ Data sudah ada! Tidak akan disimpan lagi.")

