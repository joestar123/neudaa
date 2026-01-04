import streamlit as st
import urllib.request
import random
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# --- IMPORT THƯ VIỆN ÂM LỊCH ---
try:
    from lunardate import LunarDate
    HAS_LUNAR_LIB = True
except ImportError:
    HAS_LUNAR_LIB = False

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="18h30 Team - Phong Thủy",
    page_icon="🔮",
    layout="centered"
)

# --- CSS TÙY CHỈNH (QUAN TRỌNG: ĐÃ XÓA MÀU CỨNG Ở .big-font) ---
st.markdown("""
<style>
    .big-font {
        font-size: 30px !important;
        font-weight: bold;
        /* ĐÃ XÓA DÒNG 'color: ...' ĐỂ PYTHON TỰ QUYẾT ĐỊNH MÀU */
        text-align: center;
        margin-bottom: 5px;
    }
    
    .result-box {
        border: 2px solid #1565C0;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        background-color: #f0f8ff; /* Nền xanh nhạt cố định */
        color: #000000 !important; /* Chữ mặc định đen */
        margin-top: 20px;
    }
    
    .intro-text {
        font-family: "Times New Roman";
        font-size: 18px;
        font-style: italic;
        text-align: justify;
        color: #455A64 !important;
        background-color: #eceff1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #607d8b;
    }
    
    .element-text {
        font-size: 14px;
        color: #555555 !important;
        font-weight: bold;
    }
    
    .menh-info {
        font-size: 18px; 
        color: #2E7D32 !important;
        font-weight: bold; 
        margin-bottom: 15px;
        text-transform: uppercase;
    }
    
    .summary-box {
        margin-top: 15px;
        padding: 10px;
        background-color: #FFF3E0;
        color: #000000 !important;
        border-radius: 5px;
        border: 1px dashed #FF9800;
    }
    
    .footer {
        text-align: center;
        margin-top: 50px;
        font-size: 12px;
        color: #888;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# --- CÁC HÀM LOGIC ---

def get_lunar_year_number(date_obj):
    if HAS_LUNAR_LIB:
        lunar = LunarDate.fromSolarDate(date_obj.year, date_obj.month, date_obj.day)
        return lunar.year
    else:
        return date_obj.year

def calculate_menh_nien(year):
    can_values = {4:1, 5:1, 6:2, 7:2, 8:3, 9:3, 0:4, 1:4, 2:5, 3:5}
    can_val = can_values[year % 10]
    
    chi_mod = year % 12
    if chi_mod in [4, 5, 10, 11]: chi_val = 0
    elif chi_mod in [6, 7, 0, 1]: chi_val = 1
    else: chi_val = 2
    
    total = can_val + chi_val
    if total > 5: total -= 5
    menh_map = {1: "Kim", 2: "Thủy", 3: "Hỏa", 4: "Thổ", 5: "Mộc"}
    return menh_map[total]

def get_number_element(number_str):
    last_digit = int(number_str[-1])
    if last_digit in [1, 6]: return "Thủy"
    if last_digit in [2, 7]: return "Hỏa"
    if last_digit in [3, 8]: return "Mộc"
    if last_digit in [4, 9]: return "Kim"
    return "Thổ"

def check_compatibility(user_menh, num_menh):
    tuong_sinh = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
    if user_menh == num_menh: return True, "Bình Hòa"
    if tuong_sinh.get(num_menh) == user_menh: return True, "Tương Sinh"
    return False, "Không Hợp"

def get_google_time_hanoi():
    try:
        req = urllib.request.Request("https://www.google.com", method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            date_str = response.headers['Date']
            utc_time = parsedate_to_datetime(date_str)
            return (utc_time + timedelta(hours=7)).replace(tzinfo=None), True
    except:
        return datetime.now(), False

# --- GIAO DIỆN CHÍNH ---

st.title("18h30 Team")
st.subheader("DỰ ĐOÁN SỐ MAY MẮN & PHONG THỦY")

st.markdown("""
<div class="intro-text">
    Ngẫu nhiên không được tạo ra. Nó được khai sinh.<br>
    Sử dụng Entropy, Kinh dịch thời gian thực kết hợp với Ngũ Hành Bát Quái để tìm ra con số không chỉ ngẫu nhiên mà còn hòa hợp với vận mệnh của bạn.
</div>
""", unsafe_allow_html=True)

if not HAS_LUNAR_LIB:
    st.warning("⚠️ Chưa cài đặt thư viện 'lunardate'. Vui lòng cài đặt: pip install lunardate")

st.divider()

with st.form("main_form"):
    st.markdown("**1. Ngày sinh (Để tính Mệnh)**")
    dob = st.date_input("Chọn ngày sinh của bạn", min_value=datetime(1900, 1, 1), value=datetime(2000, 1, 1))
    st.markdown("**2. Bạn chọn số cho ngày nào?**")
    target_date = st.date_input("Chọn ngày muốn dự đoán", value=datetime.now())
    st.markdown("**3. Những con số bạn đang nghĩ tới (Tối đa 5 số)**")
    cols = st.columns(5)
    fav_inputs = []
    for i, col in enumerate(cols):
        with col:
            fav_inputs.append(st.text_input(f"Số {i+1}", max_chars=2, placeholder="--"))
    submitted = st.form_submit_button("PHÂN TÍCH & LUẬN GIẢI", use_container_width=True, type="primary")

if submitted:
    valid_favs = [f.strip() for f in fav_inputs if f.strip().isdigit() and len(f.strip()) == 2]
    
    if len(valid_favs) < len([f for f in fav_inputs if f.strip()]):
        st.error("Vui lòng chỉ nhập số có 2 chữ số!")
    else:
        with st.spinner("Đang kết nối Google Server..."):
            now_dt, is_online = get_google_time_hanoi()
            lunar_year = get_lunar_year_number(dob)
            user_menh = calculate_menh_nien(lunar_year)
            
            # Seed generator
            seed_val = f"{dob.strftime('%d%m%Y')}{target_date.strftime('%d%m%Y')}{now_dt.strftime('%d%m%Y%H%M%S')}{''.join(valid_favs)}"
            random.seed(seed_val)
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            st.markdown(f"""
            <div class="result-box">
                <div class="menh-info">BẠN SINH NĂM {lunar_year} (Âm Lịch) - MỆNH {user_menh}</div>
                <h3>KẾT QUẢ PHÂN TÍCH</h3>
            """, unsafe_allow_html=True)
            
            cols = st.columns(5)
            compatible_count = 0
            
            for idx, num in enumerate(kq):
                num_menh = get_number_element(num)
                is_hop, ly_do = check_compatibility(user_menh, num_menh)
                
                # --- QUYẾT ĐỊNH MÀU SẮC ---
                if is_hop:
                    compatible_count += 1
                    # Màu Xanh Đậm (Green)
                    final_color = "#1b5e20" 
                    note_color = "#2E7D32"
                else:
                    # Màu Đen Xám (Dark Gray)
                    final_color = "#333333"
                    note_color = "#757575"
                
                with cols[idx]:
                    st.markdown(f"""
                    <div style="text-align: center;">
                        <div class="big-font" style="color: {final_color} !important;">{num}</div>
                        <div class="element-text">Hành: {num_menh}</div>
                        <div style="font-size: 12px; font-weight: bold; color: {note_color} !important;">{ly_do}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="summary-box">
                <b>🔮 LUẬN GIẢI:</b><br>
                Có <b>{compatible_count}/5</b> con số hợp mệnh với bạn.<br>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption(f"Time check: {now_dt.strftime('%H:%M:%S')} ({'Google Server' if is_online else 'Offline'})")

st.markdown('<div class="footer">Created by MinhMup</div>', unsafe_allow_html=True)