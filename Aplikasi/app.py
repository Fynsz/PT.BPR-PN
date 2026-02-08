import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import json
from io import BytesIO

# =========================
# KONFIGURASI PATH FILE
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "hasil_prediksi.json")

# =========================
# LOAD MODEL
# =========================
@st.cache_resource
def load_model():
    """Load model dengan caching untuk performa lebih baik"""
    try:
        model_path = os.path.join(BASE_DIR, "model_random_forest_pip.pkl")
        
        if not os.path.exists(model_path):
            st.error(f"Model tidak ditemukan di: {model_path}")
            st.stop()
        
        model = joblib.load(model_path)
        
        # Deteksi nama kolom yang digunakan model
        if hasattr(model, 'feature_names_in_'):
            feature_names = list(model.feature_names_in_)
            st.session_state.model_features = feature_names
        
        return model
    except Exception as e:
        st.error(f"Error saat loading model: {str(e)}")
        st.stop()

model = load_model()

# =========================
# FUNGSI UNTUK MANAJEMEN DATA
# =========================
def load_predictions():
    """Load data prediksi dari file JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    return json.loads(content)
                else:
                    return []
        except json.JSONDecodeError as e:
            st.error(f"Error membaca file JSON: {e}")
            return []
        except Exception as e:
            st.error(f"Error loading predictions: {e}")
            return []
    return []

def save_predictions(data):
    """Simpan data prediksi ke file JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error menyimpan data: {e}")
        return False

def add_prediction(prediction_data):
    """Tambah prediksi baru ke database"""
    try:
        predictions = load_predictions()
        predictions.append(prediction_data)
        success = save_predictions(predictions)
        return success
    except Exception as e:
        st.error(f"Error menambah prediksi: {e}")
        return False

def add_multiple_predictions(prediction_list):
    """Tambah multiple prediksi sekaligus"""
    try:
        predictions = load_predictions()
        predictions.extend(prediction_list)
        success = save_predictions(predictions)
        return success
    except Exception as e:
        st.error(f"Error menambah multiple prediksi: {e}")
        return False

def delete_prediction(index):
    """Hapus prediksi berdasarkan index"""
    try:
        predictions = load_predictions()
        if 0 <= index < len(predictions):
            predictions.pop(index)
            save_predictions(predictions)
            return True
        return False
    except Exception as e:
        st.error(f"Error menghapus prediksi: {e}")
        return False

def delete_all_predictions():
    """Hapus semua prediksi"""
    try:
        save_predictions([])
        return True
    except Exception as e:
        st.error(f"Error menghapus semua data: {e}")
        return False

# =========================
# FUNGSI UNTUK DETEKSI SEPARATOR CSV
# =========================
def detect_csv_separator(file_content):
    """Deteksi separator CSV (comma atau semicolon)"""
    # Baca beberapa baris pertama
    first_lines = file_content[:1000]
    
    # Hitung jumlah comma dan semicolon
    comma_count = first_lines.count(',')
    semicolon_count = first_lines.count(';')
    
    # Return separator yang paling banyak
    if semicolon_count > comma_count:
        return ';'
    else:
        return ','

# =========================
# FUNGSI PREDIKSI
# =========================
def get_model_column_names():
    """Deteksi nama kolom yang digunakan model"""
    if hasattr(model, 'feature_names_in_'):
        features = model.feature_names_in_
        
        # Cek apakah model menggunakan format lama atau baru
        if 'Alasan_Layak PIP' in features:
            # Model lama (dengan spasi)
            return {
                'penghasilan_ayah': 'Penghasilan_ayah',
                'penghasilan_ibu': 'Penghasilan_ibu',
                'penghasilan_wali': 'Penghasilan_wali',
                'alasan': 'Alasan_Layak PIP',
                'nilai': 'Nilai_rata-rata siswa',
                'hadir': 'Hadir'
            }
        elif 'Alasan_Layak_PIP' in features:
            # Model baru (dengan underscore)
            return {
                'penghasilan_ayah': 'Penghasilan_ayah',
                'penghasilan_ibu': 'Penghasilan_ibu',
                'penghasilan_wali': 'Penghasilan_wali',
                'alasan': 'Alasan_Layak_PIP',
                'nilai': 'Nilai_rata-rata',
                'hadir': 'Hadir'
            }
    
    # Default ke format lama jika tidak terdeteksi
    return {
        'penghasilan_ayah': 'Penghasilan_ayah',
        'penghasilan_ibu': 'Penghasilan_ibu',
        'penghasilan_wali': 'Penghasilan_wali',
        'alasan': 'Alasan_Layak PIP',
        'nilai': 'Nilai_rata-rata siswa',
        'hadir': 'Hadir'
    }

def predict_single(data_dict):
    """Prediksi untuk satu data - OTOMATIS MENYESUAIKAN dengan model"""
    penghasilan_mapping = {
        "Tidak Berpenghasilan": 0,
        "Kurang dari 500000": 1,
        "Kurang dari  500000": 1,
        "500000-999999": 2,
        "1000000-1999999": 3,
        " 1000000-1999999": 3,
        "200000-4999999": 4,
        "2000000-4999999": 4,
        "Lebih dari 2000000": 4
    }
    
    alasan_mapping = {
        "Tidak Ada Keterangan": 0,
        "Siswa Miskin / Rentan Miskin": 1,
        "Siswa Miskin/Rentan Miskin": 1,
        "Pemegang PKH / KPS / KKS": 1,
        "Pemegang PKH/KPS/KKS": 1
    }
    
    penghasilan_ayah_clean = str(data_dict['penghasilan_ayah']).strip()
    penghasilan_ibu_clean = str(data_dict['penghasilan_ibu']).strip()
    penghasilan_wali_clean = str(data_dict['penghasilan_wali']).strip()
    alasan_clean = str(data_dict['alasan_layak_pip']).strip()
    
    penghasilan_ayah = penghasilan_mapping.get(penghasilan_ayah_clean, 0)
    penghasilan_ibu = penghasilan_mapping.get(penghasilan_ibu_clean, 0)
    penghasilan_wali = penghasilan_mapping.get(penghasilan_wali_clean, 0)
    alasan = alasan_mapping.get(alasan_clean, 0)
    
    # Dapatkan nama kolom yang sesuai dengan model
    col_names = get_model_column_names()
    
    # Buat DataFrame dengan nama kolom yang sesuai
    data = pd.DataFrame([[
        penghasilan_ayah,
        penghasilan_ibu,
        penghasilan_wali,
        alasan,
        float(data_dict['nilai_rata_rata']),
        float(data_dict['kehadiran'])
    ]], columns=[
        col_names['penghasilan_ayah'],
        col_names['penghasilan_ibu'],
        col_names['penghasilan_wali'],
        col_names['alasan'],
        col_names['nilai'],
        col_names['hadir']
    ])
    
    hasil = model.predict(data)[0]
    proba = model.predict_proba(data)[0]
    
    return {
        'hasil': hasil,
        'prob_tidak_layak': proba[0] * 100,
        'prob_layak': proba[1] * 100,
        'confidence': max(proba) * 100
    }

def process_batch_data(df):
    """Proses batch data dari file upload - TANPA membutuhkan kolom timestamp"""
    results = []
    errors = []
    
    # Info jumlah kolom dan baris
    st.info(f"📊 File memiliki {len(df.columns)} kolom dan {len(df)} baris")
    
    # Hapus kolom timestamp jika ada
    timestamp_columns = [col for col in df.columns if 'timestamp' in col.lower()]
    if timestamp_columns:
        df = df.drop(columns=timestamp_columns)
        st.info(f"🗑️ Kolom timestamp dihapus: {', '.join(timestamp_columns)}")
    
    column_mapping = {}
    
    # Definisi variasi nama kolom (case-insensitive)
    column_variants = {
        'Nama Siswa': ['nama siswa', 'nama_siswa', 'nama'],
        'Penghasilan_ayah': ['penghasilan_ayah', 'penghasilan ayah', 'gaji ayah', 'gaji_ayah'],
        'Penghasilan_ibu': ['penghasilan_ibu', 'penghasilan ibu', 'gaji ibu', 'gaji_ibu'],
        'Penghasilan_wali': ['penghasilan_wali', 'penghasilan wali', 'gaji wali', 'gaji_wali'],
        'Alasan_Layak PIP': ['alasan_layak pip', 'alasan layak pip', 'alasan_layak_pip', 'alasan pip', 'alasan'],
        'Nilai_rata-rata siswa': ['nilai_rata-rata siswa', 'nilai rata-rata siswa', 'nilai_rata-rata', 'nilai', 'nilai rata-rata'],
        'Hadir': ['hadir', 'kehadiran', 'absensi'],
        'Label_PIP': ['label_pip', 'label pip', 'label', 'status', 'keterangan']
    }
    
    # Buat mapping kolom (case-insensitive)
    df_columns_lower = {col.lower().strip(): col for col in df.columns}
    
    # Cari kolom yang cocok
    for target_col, variants in column_variants.items():
        found = False
        for variant in variants:
            if variant in df_columns_lower:
                column_mapping[target_col] = df_columns_lower[variant]
                found = True
                break
        
        # Jika tidak ketemu exact match, coba partial match
        if not found and target_col != 'Label_PIP':
            for df_col_lower, df_col_original in df_columns_lower.items():
                for variant in variants:
                    if variant in df_col_lower or df_col_lower in variant:
                        column_mapping[target_col] = df_col_original
                        found = True
                        break
                if found:
                    break
    
    # Kolom yang wajib ada (TANPA timestamp)
    required_cols = ['Nama Siswa', 'Penghasilan_ayah', 'Penghasilan_ibu', 
                     'Penghasilan_wali', 'Alasan_Layak PIP', 
                     'Nilai_rata-rata siswa', 'Hadir']
    
    missing_columns = [col for col in required_cols if col not in column_mapping]
    
    if missing_columns:
        st.error(f"❌ Kolom yang tidak ditemukan: {', '.join(missing_columns)}")
        with st.expander("🔍 Debug: Informasi Kolom"):
            st.write("**Kolom yang tersedia di file Anda:**")
            for i, col in enumerate(df.columns, 1):
                st.write(f"{i}. `{col}` (tipe: {df[col].dtype})")
            st.write("\n**Kolom yang berhasil dimapping:**")
            for key, value in column_mapping.items():
                st.write(f"✓ {key} → `{value}`")
            st.write("\n**Kolom yang hilang:**")
            for col in missing_columns:
                st.write(f"✗ {col}")
        return None
    
    # Proses setiap baris
    total_rows = len(df)
    for idx, row in df.iterrows():
        try:
            # Ambil nama siswa
            nama = str(row[column_mapping['Nama Siswa']]).strip()
            
            # Skip baris kosong
            if not nama or nama.lower() in ['nan', 'none', '']:
                continue
            
            # Ambil data dengan pengecekan tipe data
            try:
                nilai_siswa = float(row[column_mapping['Nilai_rata-rata siswa']])
            except (ValueError, TypeError):
                st.warning(f"Baris {idx + 2} ({nama}): Nilai tidak valid, diset ke 0")
                nilai_siswa = 0.0
            
            try:
                kehadiran_siswa = float(row[column_mapping['Hadir']])
            except (ValueError, TypeError):
                st.warning(f"Baris {idx + 2} ({nama}): Kehadiran tidak valid, diset ke 0")
                kehadiran_siswa = 0.0
            
            data_dict = {
                'nama_siswa': nama,
                'penghasilan_ayah': str(row[column_mapping['Penghasilan_ayah']]).strip(),
                'penghasilan_ibu': str(row[column_mapping['Penghasilan_ibu']]).strip(),
                'penghasilan_wali': str(row[column_mapping['Penghasilan_wali']]).strip(),
                'alasan_layak_pip': str(row[column_mapping['Alasan_Layak PIP']]).strip(),
                'nilai_rata_rata': nilai_siswa,
                'kehadiran': kehadiran_siswa
            }
            
            # Prediksi
            pred_result = predict_single(data_dict)
            
            # Ambil label asli jika ada
            label_asli = None
            if 'Label_PIP' in column_mapping:
                try:
                    label_asli = str(row[column_mapping['Label_PIP']]).strip()
                except:
                    pass
            
            # Simpan hasil dengan timestamp otomatis
            result = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nama_siswa": data_dict['nama_siswa'],
                "penghasilan_ayah": data_dict['penghasilan_ayah'],
                "penghasilan_ibu": data_dict['penghasilan_ibu'],
                "penghasilan_wali": data_dict['penghasilan_wali'],
                "alasan_layak_pip": data_dict['alasan_layak_pip'],
                "nilai_rata_rata": data_dict['nilai_rata_rata'],
                "kehadiran": data_dict['kehadiran'],
                "hasil_prediksi": "Layak" if pred_result['hasil'] == 1 else "Tidak Layak",
                "probabilitas_layak": pred_result['prob_layak'],
                "probabilitas_tidak_layak": pred_result['prob_tidak_layak'],
                "confidence": pred_result['confidence']
            }
            
            if label_asli:
                result['label_asli'] = label_asli
            
            results.append(result)
            
        except Exception as e:
            nama_siswa = row.get(column_mapping.get('Nama Siswa', 'Nama Siswa'), 'Unknown')
            error_msg = f"Baris {idx + 2} ({nama_siswa}): {str(e)}"
            errors.append(error_msg)
            continue
    
    # Tampilkan ringkasan
    if len(results) > 0:
        st.success(f"✅ Berhasil: {len(results)} dari {total_rows} baris")
    else:
        st.error(f"❌ Tidak ada data yang berhasil diproses dari {total_rows} baris")
    
    # Tampilkan error jika ada
    if errors:
        with st.expander(f"⚠️ {len(errors)} baris gagal diproses"):
            for error in errors[:10]:  # Tampilkan max 10 error
                st.warning(error)
            if len(errors) > 10:
                st.info(f"... dan {len(errors) - 10} error lainnya")
    
    return results

# =========================
# KONFIGURASI HALAMAN
# =========================
st.set_page_config(
    page_title="Klasifikasi Beasiswa PIP",
    page_icon="🎓",
    layout="wide"
)

# =========================
# HEADER APLIKASI
# =========================
st.title("Sistem Klasifikasi Penerima Beasiswa PIP")
st.markdown("**SMA Negeri 1 Lubuk Basung**")
st.caption("Aplikasi berbasis Random Forest untuk klasifikasi kelayakan penerima beasiswa PIP")
st.markdown("---")

# =========================
# BAGIAN 1: PREDIKSI TUNGGAL
# =========================
st.header("1. PREDIKSI TUNGGAL")
st.markdown("Masukkan data siswa untuk melakukan prediksi kelayakan beasiswa PIP")

with st.expander("Panduan Pengisian", expanded=False):
    st.write("""
    - **Nama Siswa**: Masukkan nama lengkap siswa
    - **Penghasilan**: Pilih kategori penghasilan orang tua/wali per bulan
    - **Alasan Layak PIP**: Pilih alasan yang sesuai dengan kondisi siswa
    - **Nilai Rata-rata**: Masukkan nilai rata-rata raport siswa (0-100)
    - **Kehadiran**: Masukkan persentase kehadiran siswa (0-100)
    """)

with st.form("form_prediksi_tunggal"):
    nama_siswa = st.text_input(
        "Nama Siswa",
        placeholder="Contoh: Ahmad Rizki",
        help="Masukkan nama lengkap siswa"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Data Ekonomi Keluarga**")
        
        penghasilan_ayah_label = st.selectbox(
            "Penghasilan Ayah",
            [
                "Tidak Berpenghasilan",
                "Kurang dari Rp. 500.000",
                "Rp. 500.000 - Rp. 999.999",
                "Rp. 1.000.000 - Rp. 1.999.999",
                "Lebih dari Rp. 2.000.000"
            ]
        )
        
        penghasilan_ibu_label = st.selectbox(
            "Penghasilan Ibu",
            [
                "Tidak Berpenghasilan",
                "Kurang dari Rp. 500.000",
                "Rp. 500.000 - Rp. 999.999",
                "Rp. 1.000.000 - Rp. 1.999.999",
                "Lebih dari Rp. 2.000.000"
            ]
        )
        
        penghasilan_wali_label = st.selectbox(
            "Penghasilan Wali",
            [
                "Tidak Berpenghasilan",
                "Kurang dari Rp. 500.000",
                "Rp. 500.000 - Rp. 999.999",
                "Rp. 1.000.000 - Rp. 1.999.999",
                "Lebih dari Rp. 2.000.000"
            ]
        )
    
    with col2:
        st.markdown("**Data Akademik & Kelayakan**")
        
        alasan_label = st.selectbox(
            "Alasan Layak PIP",
            [
                "Tidak Ada Keterangan",
                "Siswa Miskin/Rentan Miskin",
                "Pemegang PKH/KPS/KKS"
            ]
        )
        
        nilai = st.number_input(
            "Nilai Rata-rata Siswa", 
            min_value=0.0, 
            max_value=100.0,
            value=75.0,
            step=0.1
        )
        
        hadir = st.number_input(
            "Kehadiran (%)", 
            min_value=0.0, 
            max_value=100.0,
            value=90.0,
            step=0.1
        )
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        submitted = st.form_submit_button("Prediksi", use_container_width=True, type="primary")
    with col_btn2:
        reset = st.form_submit_button("Reset", use_container_width=True)

if submitted:
    if not nama_siswa or nama_siswa.strip() == "":
        st.error("Nama siswa tidak boleh kosong!")
    else:
        try:
            data_dict = {
                'nama_siswa': nama_siswa.strip(),
                'penghasilan_ayah': penghasilan_ayah_label,
                'penghasilan_ibu': penghasilan_ibu_label,
                'penghasilan_wali': penghasilan_wali_label,
                'alasan_layak_pip': alasan_label,
                'nilai_rata_rata': float(nilai),
                'kehadiran': float(hadir)
            }
            
            pred_result = predict_single(data_dict)
            
            st.session_state.last_prediction = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "nama_siswa": data_dict['nama_siswa'],
                "penghasilan_ayah": data_dict['penghasilan_ayah'],
                "penghasilan_ibu": data_dict['penghasilan_ibu'],
                "penghasilan_wali": data_dict['penghasilan_wali'],
                "alasan_layak_pip": data_dict['alasan_layak_pip'],
                "nilai_rata_rata": data_dict['nilai_rata_rata'],
                "kehadiran": data_dict['kehadiran'],
                "hasil_prediksi": "Layak" if pred_result['hasil'] == 1 else "Tidak Layak",
                "probabilitas_layak": pred_result['prob_layak'],
                "probabilitas_tidak_layak": pred_result['prob_tidak_layak'],
                "confidence": pred_result['confidence']
            }
            
            st.markdown("#### Hasil Prediksi")
            
            col_result1, col_result2 = st.columns([2, 1])
            
            with col_result1:
                if pred_result['hasil'] == 1:
                    st.success(f"**{nama_siswa}** LAYAK menerima Beasiswa PIP")
                else:
                    st.error(f"**{nama_siswa}** TIDAK LAYAK menerima Beasiswa PIP")
            
            with col_result2:
                st.metric("Tingkat Keyakinan", f"{pred_result['confidence']:.2f}%")
            
            col_prob1, col_prob2 = st.columns(2)
            with col_prob1:
                st.metric("Probabilitas Tidak Layak", f"{pred_result['prob_tidak_layak']:.2f}%")
            with col_prob2:
                st.metric("Probabilitas Layak", f"{pred_result['prob_layak']:.2f}%")
            
        except Exception as e:
            st.error(f"Terjadi kesalahan saat prediksi: {str(e)}")

if 'last_prediction' in st.session_state:
    col_save1, col_save2 = st.columns([2, 2])
    
    with col_save1:
        if st.button("Simpan Hasil Prediksi", use_container_width=True, type="primary", key="save_single"):
            success = add_prediction(st.session_state.last_prediction)
            
            if success:
                st.success(f"Hasil prediksi untuk **{st.session_state.last_prediction['nama_siswa']}** berhasil disimpan!")
                del st.session_state.last_prediction
                st.rerun()
            else:
                st.error("Gagal menyimpan data!")
    
    with col_save2:
        if st.button("Prediksi Baru", use_container_width=True):
            del st.session_state.last_prediction
            st.rerun()

st.markdown("---")

# =========================
# BAGIAN 2: PREDIKSI BATCH
# =========================
st.header("2. PREDIKSI BATCH (UPLOAD FILE)")
st.markdown("Upload file CSV atau Excel untuk melakukan prediksi massal")

col_info, col_template = st.columns([2, 1])

with col_info:
    st.info("""
    **Format File yang Diterima:** CSV, Excel (.xlsx, .xls)
    
    **Kolom yang Diperlukan (TANPA timestamp):**
    - Nama Siswa
    - Penghasilan_ayah
    - Penghasilan_ibu
    - Penghasilan_wali
    - Alasan_Layak PIP
    - Nilai_rata-rata siswa
    - Hadir
    - Label_PIP (opsional - untuk perbandingan)
    
    **Catatan:** 
    - Untuk CSV: Sistem akan otomatis mendeteksi separator (koma atau titik koma)
    - Timestamp akan otomatis ditambahkan oleh sistem
    """)

with col_template:
    st.markdown("**Download Template**")
    
    # Template TANPA timestamp
    template_data = {
        'Nama Siswa': ['ADITYA EFENDI', 'AFRIYAN SAMAWA', 'Aira Herlina Putri'],
        'Penghasilan_ayah': ['500000-999999', 'Kurang dari 500000', '500000-999999'],
        'Penghasilan_ibu': ['Tidak Berpenghasilan', 'Tidak Berpenghasilan', 'Tidak Berpenghasilan'],
        'Penghasilan_wali': ['Tidak Berpenghasilan', 'Tidak Berpenghasilan', 'Tidak Berpenghasilan'],
        'Alasan_Layak PIP': ['Siswa Miskin/Rentan Miskin', 'Tidak Ada Keterangan', 'Siswa Miskin/Rentan Miskin'],
        'Nilai_rata-rata siswa': [85, 96, 81],
        'Hadir': [95, 90, 85],
        'Label_PIP': ['Ya', 'Ya', 'Ya']
    }
    template_df = pd.DataFrame(template_data)
    
    # Template CSV dengan SEMICOLON (sesuai file asli Anda)
    csv_template = template_df.to_csv(index=False, encoding='utf-8-sig', sep=';')
    st.download_button(
        label="CSV (Semicolon)",
        data=csv_template,
        file_name="template_prediksi_pip.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name='Data Siswa')
    excel_template = output.getvalue()
    
    st.download_button(
        label="Excel",
        data=excel_template,
        file_name="template_prediksi_pip.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

uploaded_file = st.file_uploader(
    "Pilih file CSV atau Excel",
    type=['csv', 'xlsx', 'xls'],
    help="Upload file dengan format sesuai template"
)

if uploaded_file is not None:
    try:
        # Baca file dengan deteksi separator otomatis untuk CSV
        if uploaded_file.name.endswith('.csv'):
            # Baca konten file untuk deteksi separator
            file_content = uploaded_file.read().decode('utf-8-sig')
            uploaded_file.seek(0)  # Reset pointer
            
            # Deteksi separator
            separator = detect_csv_separator(file_content)
            st.info(f"🔍 Separator terdeteksi: `{separator}` ({'semicolon' if separator == ';' else 'comma'})")
            
            # Baca CSV dengan separator yang terdeteksi
            from io import StringIO
            df_upload = pd.read_csv(StringIO(file_content), sep=separator)
        else:
            df_upload = pd.read_excel(uploaded_file)
        
        st.success(f"✅ File berhasil diupload: **{uploaded_file.name}**")
        st.info(f"📊 Total baris: {len(df_upload)} | Total kolom: {len(df_upload.columns)}")
        
        with st.expander("👁️ Preview Data (10 baris pertama)"):
            st.dataframe(df_upload.head(10), use_container_width=True)
        
        if st.button("🚀 Proses Prediksi Batch", type="primary", use_container_width=True):
            with st.spinner("⏳ Memproses data..."):
                results = process_batch_data(df_upload)
                
                if results and len(results) > 0:
                    st.session_state.batch_results = results
                    st.rerun()
                elif results is not None:
                    st.warning("⚠️ Tidak ada data yang berhasil diproses")
        
        if 'batch_results' in st.session_state:
            st.markdown("---")
            st.markdown("#### 📊 Hasil Prediksi Batch")
            
            results_df = pd.DataFrame(st.session_state.batch_results)
            
            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            
            total_batch = len(results_df)
            total_layak_batch = len(results_df[results_df['hasil_prediksi'] == 'Layak'])
            total_tidak_layak_batch = total_batch - total_layak_batch
            avg_confidence = results_df['confidence'].mean()
            
            with col_stat1:
                st.metric("Total Siswa", total_batch)
            with col_stat2:
                st.metric("Layak", total_layak_batch)
            with col_stat3:
                st.metric("Tidak Layak", total_tidak_layak_batch)
            with col_stat4:
                st.metric("Rata-rata Keyakinan", f"{avg_confidence:.1f}%")
            
            if 'label_asli' in results_df.columns:
                st.markdown("**Perbandingan dengan Label Asli**")
                
                results_df['label_asli_binary'] = results_df['label_asli'].map({'Ya': 'Layak', 'Tidak': 'Tidak Layak'})
                
                correct = (results_df['hasil_prediksi'] == results_df['label_asli_binary']).sum()
                accuracy = (correct / total_batch) * 100
                
                col_acc1, col_acc2, col_acc3 = st.columns(3)
                with col_acc1:
                    st.metric("Akurasi", f"{accuracy:.2f}%")
                with col_acc2:
                    st.metric("Prediksi Benar", correct)
                with col_acc3:
                    st.metric("Prediksi Salah", total_batch - correct)
            
            # Legenda warna
            st.markdown("**Keterangan Warna:**")
            col_legend1, col_legend2, col_legend3 = st.columns(3)
            
            with col_legend1:
                st.markdown("🟦 = Biru (Layak)")
            with col_legend2:
                st.markdown("⬜ Abu-Abu = Prediksi Benar (Tidak Layak)")
            with col_legend3:
                st.markdown("🟥 Merah = Prediksi Salah")
            
            display_df = results_df[[
                'nama_siswa', 'nilai_rata_rata', 'kehadiran', 
                'hasil_prediksi', 'confidence'
            ]].copy()
            
            if 'label_asli' in results_df.columns:
                display_df['label_asli'] = results_df['label_asli']
                display_df.columns = [
                    'Nama Siswa', 'Nilai Rata-rata', 'Kehadiran (%)', 
                    'Hasil Prediksi', 'Keyakinan (%)', 'Label Asli'
                ]
            else:
                display_df.columns = [
                    'Nama Siswa', 'Nilai Rata-rata', 'Kehadiran (%)', 
                    'Hasil Prediksi', 'Keyakinan (%)'
                ]
            
            def highlight_hasil(row):
                if 'Label Asli' in row.index:
                    if row['Hasil Prediksi'] == 'Layak' and row['Label Asli'] == 'Ya':
                        return ['background-color: #2B27B2'] * len(row)
                    elif row['Hasil Prediksi'] == 'Tidak Layak' and row['Label Asli'] == 'Tidak':
                        return ['background-color: #536878'] * len(row)
                    else:
                        return ['background-color: #A80815'] * len(row)
                else:
                    if row['Hasil Prediksi'] == 'Layak':
                        return ['background-color: #2B27B2'] * len(row)
                    else:
                        return ['background-color: #A80815'] * len(row)
            
            st.dataframe(
                display_df.style.apply(highlight_hasil, axis=1),
                use_container_width=True,
                hide_index=True
            )
            
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                csv_result = results_df.to_csv(index=False, encoding='utf-8-sig', sep=';')
                st.download_button(
                    label="Download CSV",
                    data=csv_result,
                    file_name=f"hasil_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_action2:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    results_df.to_excel(writer, index=False, sheet_name='Hasil Prediksi')
                excel_result = output.getvalue()
                
                st.download_button(
                    label="Download Excel",
                    data=excel_result,
                    file_name=f"hasil_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col_action3:
                if st.button("Simpan ke Database", type="primary", use_container_width=True):
                    batch_to_save = []
                    for result in st.session_state.batch_results:
                        result_copy = result.copy()
                        result_copy.pop('label_asli', None)
                        result_copy.pop('label_asli_binary', None)
                        batch_to_save.append(result_copy)
                    
                    success = add_multiple_predictions(batch_to_save)
                    if success:
                        st.success(f"Berhasil menyimpan {len(batch_to_save)} data ke database!")
                        del st.session_state.batch_results
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan data!")
            
    except Exception as e:
        st.error(f"❌ Error membaca file: {str(e)}")
        with st.expander("Detail Error"):
            st.code(str(e))
            import traceback
            st.code(traceback.format_exc())

st.markdown("---")

# =========================
# BAGIAN 3: RIWAYAT PREDIKSI (DENGAN SEMUA FITUR)
# =========================
st.header("3. RIWAYAT PREDIKSI")
st.markdown("Daftar semua hasil prediksi yang telah disimpan")

predictions = load_predictions()

col_info_riwayat, col_refresh = st.columns([3, 1])
with col_info_riwayat:
    st.info(f"📊 Total data tersimpan: {len(predictions)} prediksi")
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

if len(predictions) == 0:
    st.warning("📭 Belum ada data prediksi yang tersimpan.")
    st.info("💡 Lakukan prediksi terlebih dahulu di menu 'Prediksi Tunggal' atau 'Prediksi Batch'")
else:
    # ==================
    # FITUR 3: STATISTIK RINGKAS
    # ==================
    st.markdown("### 📈 Ringkasan Statistik")
    
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    total_data = len(predictions)
    total_layak = sum(1 for p in predictions if p['hasil_prediksi'] == 'Layak')
    total_tidak_layak = total_data - total_layak
    persentase_layak = (total_layak / total_data * 100) if total_data > 0 else 0
    avg_nilai = sum(p['nilai_rata_rata'] for p in predictions) / total_data
    
    with col_stat1:
        st.metric("Total Prediksi", total_data)
    with col_stat2:
        st.metric("Layak", total_layak, delta=f"{persentase_layak:.1f}%")
    with col_stat3:
        st.metric("Tidak Layak", total_tidak_layak, delta=f"{100-persentase_layak:.1f}%", delta_color="inverse")
    with col_stat4:
        st.metric("Rata-rata Nilai", f"{avg_nilai:.1f}")
    
    st.markdown("---")
    
    # ==================
    # FITUR 4: ANALISIS CONFIDENCE
    # ==================
    st.markdown("### 🎯 Analisis Tingkat Keyakinan Model")
    
    df_confidence = pd.DataFrame(predictions)
    
    tab1, tab2 = st.tabs(["🔝 Confidence Tertinggi", "⚠️ Confidence Terendah"])
    
    with tab1:
        st.markdown("**Top 10 Prediksi dengan Keyakinan Tertinggi**")
        st.caption("Model sangat yakin dengan prediksi ini")
        
        top_confidence = df_confidence.nlargest(10, 'confidence')
        
        display_top = top_confidence[[
            'nama_siswa', 'hasil_prediksi', 'confidence', 
            'nilai_rata_rata', 'kehadiran'
        ]].copy()
        
        display_top.columns = ['Nama Siswa', 'Hasil', 'Keyakinan (%)', 'Nilai', 'Kehadiran (%)']
        
        def highlight_conf(row):
            if row['Hasil'] == 'Layak':
                return ['background-color: #00823D'] * len(row)
            else:
                return ['background-color: #801616'] * len(row)
        
        st.dataframe(
            display_top.style.apply(highlight_conf, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        avg_top = top_confidence['confidence'].mean()
        st.info(f"📊 Rata-rata confidence: {avg_top:.2f}%")
    
    with tab2:
        st.markdown("**Top 10 Prediksi dengan Keyakinan Terendah**")
        st.caption("⚠️ Pertimbangkan review manual untuk data ini")
        
        low_confidence = df_confidence.nsmallest(10, 'confidence')
        
        display_low = low_confidence[[
            'nama_siswa', 'hasil_prediksi', 'confidence', 
            'nilai_rata_rata', 'kehadiran'
        ]].copy()
        
        display_low.columns = ['Nama Siswa', 'Hasil', 'Keyakinan (%)', 'Nilai', 'Kehadiran (%)']
        
        st.dataframe(
            display_low.style.apply(highlight_conf, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        avg_low = low_confidence['confidence'].mean()
        st.warning(f"⚠️ Rata-rata confidence: {avg_low:.2f}%")
    
    # Distribusi Confidence
    st.markdown("**📊 Distribusi Tingkat Keyakinan**")
    
    def categorize_confidence(conf):
        if conf >= 90:
            return "Sangat Tinggi (≥90%)"
        elif conf >= 75:
            return "Tinggi (75-89%)"
        elif conf >= 60:
            return "Sedang (60-74%)"
        else:
            return "Rendah (<60%)"
    
    df_confidence['kategori'] = df_confidence['confidence'].apply(categorize_confidence)
    conf_dist = df_confidence['kategori'].value_counts()
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    
    categories = ["Sangat Tinggi (≥90%)", "Tinggi (75-89%)", "Sedang (60-74%)", "Rendah (<60%)"]
    cols = [col_c1, col_c2, col_c3, col_c4]
    
    for cat, col in zip(categories, cols):
        with col:
            count = conf_dist.get(cat, 0)
            pct = (count / total_data * 100) if total_data > 0 else 0
            st.metric(cat.split('(')[0].strip(), count, delta=f"{pct:.1f}%")
    
    st.markdown("---")
    
    # ==================
    # FITUR 2: FILTER & PENCARIAN
    # ==================
    st.markdown("### 🔍 Filter & Pencarian")
    
    col_filter1, col_filter2 = st.columns([2, 1])
    
    with col_filter1:
        search = st.text_input(
            "Cari Nama Siswa", 
            placeholder="Ketik nama siswa...",
            help="Pencarian tidak case-sensitive"
        )
    
    with col_filter2:
        filter_hasil = st.selectbox(
            "Filter Hasil",
            ["Semua", "Layak", "Tidak Layak"],
            help="Filter berdasarkan hasil klasifikasi"
        )
    
    # ==================
    # FITUR 1: MANAJEMEN HASIL + PENERAPAN FILTER
    # ==================
    df_predictions = pd.DataFrame(predictions)
    
    df_display = df_predictions.copy()
    df_display = df_display.rename(columns={
        'timestamp': 'Waktu Prediksi',
        'nama_siswa': 'Nama Siswa',
        'nilai_rata_rata': 'Nilai Rata-rata',
        'kehadiran': 'Kehadiran (%)',
        'hasil_prediksi': 'Hasil',
        'confidence': 'Keyakinan (%)'
    })
    
    # Sort by timestamp (terbaru di atas)
    df_display = df_display.sort_values('Waktu Prediksi', ascending=False)
    
    # Apply filter
    df_filtered = df_display.copy()
    
    if search:
        df_filtered = df_filtered[
            df_filtered['Nama Siswa'].str.contains(search, case=False, na=False)
        ]
    
    if filter_hasil != "Semua":
        df_filtered = df_filtered[df_filtered['Hasil'] == filter_hasil]
    
    st.markdown(f"**Menampilkan {len(df_filtered)} dari {total_data} data**")
    
    # Legenda warna
    st.markdown("**Keterangan Warna:**")
    col_leg1, col_leg2 = st.columns(2)
    with col_leg1:
        st.markdown("🟩 **Hijau** = Layak menerima PIP")
    with col_leg2:
        st.markdown("🟥 **Merah** = Tidak Layak menerima PIP")
    
    # Display dengan warna
    display_columns = [
        'Waktu Prediksi', 'Nama Siswa', 'Nilai Rata-rata',
        'Kehadiran (%)', 'Hasil', 'Keyakinan (%)'
    ]
    
    def highlight_hasil(row):
        if row['Hasil'] == 'Layak':
            return ['background-color: #00823D'] * len(row)  # Hijau
        else:
            return ['background-color: #801616'] * len(row)  # Merah
    
    st.dataframe(
        df_filtered[display_columns].style.apply(highlight_hasil, axis=1),
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    with st.expander("📋 Lihat Detail Lengkap"):
        st.dataframe(df_filtered, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # ==================
    # FITUR 6: EKSPOR DATA
    # ==================
    st.markdown("### 💾 Kelola Data")
    
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        csv = df_predictions.to_csv(index=False, encoding='utf-8-sig', sep=';')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"riwayat_prediksi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download dalam format CSV"
        )
    
    with col_download2:
        try:
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: Data lengkap
                df_predictions.to_excel(writer, index=False, sheet_name='Hasil Prediksi')
                
                # Sheet 2: Statistik
                stats_data = {
                    'Metrik': [
                        'Total Prediksi', 'Jumlah Layak', 'Jumlah Tidak Layak',
                        'Persentase Layak', 'Rata-rata Nilai', 'Rata-rata Kehadiran'
                    ],
                    'Nilai': [
                        total_data, total_layak, total_tidak_layak,
                        f"{persentase_layak:.2f}%", f"{avg_nilai:.2f}",
                        f"{df_predictions['kehadiran'].mean():.2f}%"
                    ]
                }
                pd.DataFrame(stats_data).to_excel(writer, index=False, sheet_name='Statistik')
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"riwayat_prediksi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                help="Download dalam format Excel dengan sheet statistik"
            )
        except ImportError:
            st.warning("⚠️ Install openpyxl: pip install openpyxl")
    
    # ==================
    # FITUR 5: HAPUS DATA
    # ==================
    st.markdown("**🗑️ Hapus Data**")
    
    col_delete1, col_delete2 = st.columns([4, 1])
    
    with col_delete1:
        nama_list = [f"{i+1}. {p['nama_siswa']} - {p['timestamp']}" for i, p in enumerate(predictions)]
        selected_index = st.selectbox(
            "Pilih data untuk dihapus",
            range(len(nama_list)),
            format_func=lambda x: nama_list[x]
        )
    
    with col_delete2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Hapus Terpilih", use_container_width=True, type="secondary"):
            if delete_prediction(selected_index):
                st.success("✅ Data berhasil dihapus!")
                st.rerun()
    
    if st.button("🗑️ Hapus Semua Data", use_container_width=True, type="secondary"):
        if st.session_state.get('confirm_delete', False):
            if delete_all_predictions():
                st.success("✅ Semua data berhasil dihapus!")
                st.session_state.confirm_delete = False
                st.rerun()
        else:
            st.session_state.confirm_delete = True
            st.warning("⚠️ Klik sekali lagi untuk konfirmasi!")

# =========================
# FOOTER
# =========================
st.caption("Developed for SMA Negeri 1 Lubuk Basung | Powered by Random Forest Algorithm | © 2026")