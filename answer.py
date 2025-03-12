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
    layout='wide',  
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

def read_github_data():
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_info = response.json()
        file_content = file_info.get("content", "")
        decoded_bytes = base64.b64decode(file_content)
        decoded_content = decoded_bytes.decode("utf-8")
        return json.loads(decoded_content)
    else:
        st.error(f"❌ Gagal mengambil data dari GitHub! Status code: {response.status_code}")
        return []

# Ambil data dari GitHub
data = read_github_data()

# Jika data kosong, stop aplikasi
if not data:
    st.stop()

# Format data menjadi DataFrame
formatted_data = []
total_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

for item in data:
    row = {
        "Nama": item["Nama"],
        "Jurusan": item["Jurusan"],
        "Fakultas": item["Fakultas"],
        "Universitas": item["Universitas"],
    }
    for key, value in item["Jawaban"].items():
        row[key] = str(value)
        if str(value) in total_counts:
            total_counts[str(value)] += 1
    formatted_data.append(row)

df = pd.DataFrame(formatted_data)

# Sidebar menu
menu = ["ALL IN", "MODEL1", "MODEL2", "MODEL3", "MODEL4", "MODEL5", "MODEL6"]
choice = st.sidebar.selectbox("📌 Pilih Menu", menu)

# Statistik Total Jawaban
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Jawaban 1", total_counts["1"])
col2.metric("Total Jawaban 2", total_counts["2"])
col3.metric("Total Jawaban 3", total_counts["3"])
col4.metric("Total Jawaban 4", total_counts["4"])
col5.metric("Total Jawaban 5", total_counts["5"])

if choice == "ALL IN":

    # Tampilkan tabel dengan Streamlit
    st.title("Data Responden")
    df.index += 1  # Agar dimulai dari 1
    df.index.name = "No."
    st.dataframe(df)

    col1, col2, col3 = st.columns(3)

    ###############################################################################################################################

    with col1:
        # Hitung jawaban yang paling banyak muncul di setiap pertanyaan
        most_frequent_answers = {}
        for i in range(1, 16):  # Anggap ada 15 pertanyaan (P1 sampai P15)
            question = f"pertanyaan{i}"  # Sesuaikan dengan nama kolom pertanyaan
            if question in df.columns:  
                most_frequent_answers[question] = df[question].mode()[0]  # Ambil nilai yang paling sering muncul

        # Konversi ke DataFrame
        most_frequent_df = pd.DataFrame(most_frequent_answers.items(), columns=["Pertanyaan", "Jawaban Terbanyak"])

        # Tambahkan kolom "No."
        most_frequent_df.index += 1  # Biar mulai dari 1
        most_frequent_df.index.name = "No."

        # Tampilkan hasil jawaban terbanyak
        st.markdown("📊 Jawaban Terbanyak per Pertanyaan")
        st.write(most_frequent_df)

    ###############################################################################################################################

    with col2:
        def calculate_average(data):
            df = pd.DataFrame([mhs["Jawaban"] for mhs in data])
            df_numeric = df.iloc[:, :-2]  # Hanya ambil pertanyaan 1-15 (tanpa 15 dan 16 karena teks)
            return df_numeric.mean().to_frame(name="Rata-rata")

        average_df = calculate_average(data)

        st.markdown("📊 Rata-rata Jawaban Mahasiswa")
        st.dataframe(average_df)

    ###############################################################################################################################

    with col3:
        # Hitung jumlah setiap jawaban (1-5) untuk setiap pertanyaan
        answer_counts = {}

        for i in range(1, 16):  # Anggap ada 15 pertanyaan (P1 sampai P15)
            question = f"pertanyaan{i}"  # Sesuaikan dengan nama kolom pertanyaan
            if question in df.columns:
                answer_counts[question] = df[question].value_counts().to_dict()  # Hitung jumlah masing-masing jawaban

        # Konversi ke DataFrame untuk ditampilkan
        answer_counts_df = pd.DataFrame(answer_counts).fillna(0).astype(int).T  # Ubah ke tabel dan isi NaN dengan 0

        # Tambahkan label "Pertanyaan" di index
        answer_counts_df.index.name = "Pertanyaan"  

        # Tampilkan hasil jumlah jawaban per angka
        st.markdown("📊 Jumlah Jawaban per Pertanyaan")
        st.write(answer_counts_df)

###############################################################################################################################

elif choice == "MODEL1":
    # Tampilkan tabel dengan Streamlit
    st.title("Data Responden")
    df.index += 1  # Agar dimulai dari 1
    df.index.name = "No."
    st.dataframe(df)

###############################################################################################################################

if choice == "MODEL2":
    # Hitung jawaban yang paling banyak muncul di setiap pertanyaan
    most_frequent_answers = {}
    for i in range(1, 16):  # Anggap ada 15 pertanyaan (P1 sampai P15)
        question = f"pertanyaan{i}"  # Sesuaikan dengan nama kolom pertanyaan
        if question in df.columns:  
            most_frequent_answers[question] = df[question].mode()[0]  # Ambil nilai yang paling sering muncul

    # Konversi ke DataFrame
    most_frequent_df = pd.DataFrame(most_frequent_answers.items(), columns=["Pertanyaan", "Jawaban Terbanyak"])

    # Tambahkan kolom "No."
    most_frequent_df.index += 1  # Biar mulai dari 1
    most_frequent_df.index.name = "No."

    # Tampilkan hasil jawaban terbanyak
    st.subheader("📊 Jawaban Terbanyak per Pertanyaan")
    st.write(most_frequent_df)

if choice == "MODEL3":

    # Buat DataFrame
    df = pd.DataFrame(data)

    # Cek apakah ada kolom 'Jawaban'
    if "Jawaban" in df.columns:
        # Pecah kolom "Jawaban"
        df_jawaban = df["Jawaban"].apply(pd.Series)
        df = pd.concat([df.drop(columns=["Jawaban"]), df_jawaban], axis=1)

        # Pastikan semua kolom 1-15 berupa angka
        pertanyaan_cols = [f"pertanyaan{i}" for i in range(1, 15)]
        for col in pertanyaan_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Hitung rata-rata
        average_answers = {col: df[col].mean() for col in pertanyaan_cols if col in df.columns}
        average_df = pd.DataFrame(average_answers.items(), columns=["Pertanyaan", "Rata-rata Jawaban"])

        # Tambahkan nomor urut
        average_df.index += 1
        average_df.index.name = "No."

        # Tampilkan
        st.subheader("📊 Rata-rata Jawaban per Pertanyaan")
        st.write(average_df)

    else:
        st.warning("Data tidak memiliki kolom 'Jawaban'. Pastikan struktur data sudah benar.")

if choice == "MODEL4":
    # Hitung jumlah setiap jawaban (1-5) untuk setiap pertanyaan
    answer_counts = {}

    for i in range(1, 16):  # Anggap ada 15 pertanyaan (P1 sampai P15)
        question = f"pertanyaan{i}"  # Sesuaikan dengan nama kolom pertanyaan
        if question in df.columns:
            answer_counts[question] = df[question].value_counts().to_dict()  # Hitung jumlah masing-masing jawaban

    # Konversi ke DataFrame untuk ditampilkan
    answer_counts_df = pd.DataFrame(answer_counts).fillna(0).astype(int).T  # Ubah ke tabel dan isi NaN dengan 0

    # Tambahkan label "Pertanyaan" di index
    answer_counts_df.index.name = "Pertanyaan"  

    # Tampilkan hasil jumlah jawaban per angka
    st.subheader("📊 Jumlah Jawaban per Pertanyaan")
    st.write(answer_counts_df)

if choice == "MODEL5":
    st.title("📊 Data Responden Berdasarkan Nama")
    selected_name = st.selectbox("🔍 Pilih Nama Responden", df["Nama"].unique())
    filtered_df = df[df["Nama"] == selected_name].drop(columns=["Nama"])
    filtered_df = filtered_df.T
    filtered_df.index.name = "Pertanyaan"
    filtered_df.columns = [selected_name]
    st.write(f"📌 **Jawaban untuk {selected_name}:**")
    st.write(filtered_df)

if choice == "MODEL6":
    st.title("📊 Jawaban Pertanyaan 16")

    # Konversi data ke DataFrame
    df = pd.DataFrame(data)

    if "Jawaban" not in df.columns:
        st.error("❌ Data tidak memiliki kolom 'Jawaban'. Pastikan struktur data benar!")
    else:
        # Ambil hanya kolom Nama dan pertanyaan16
        df_filtered = df[["Nama"]].copy()
        df_filtered["pertanyaan16"] = df["Jawaban"].apply(lambda x: x.get("pertanyaan16", "Tidak ada jawaban") if isinstance(x, dict) else "Tidak ada data")

        # Menampilkan data dalam bentuk tabel di bawahnya
        st.subheader("📊 Data dalam Tabel")
        st.dataframe(df_filtered)

        # Menampilkan data dengan columns (dibagi menjadi 5 kolom)
        st.subheader("📌 Data dalam Format Grid")
        cols = st.columns(5)  # Membuat 5 kolom

        for index, row in df_filtered.iterrows():
            with cols[index % 5]:  # Distribusi data ke 5 kolom
                st.write(f"**{row['Nama']}**")
                st.write(f"Jawaban: {row['pertanyaan16']}")
                st.markdown("---")  # Garis pemisah
