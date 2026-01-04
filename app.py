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

# --- CSS FIX LỖI DARK MODE & UI ---
st.markdown("""
<style>
    /* 1. Class cho thẻ kết quả (Card) */
    .lucky-card {
        background-color: #f0f8ff; /* Nền sáng */
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        /* QUAN TRỌNG: Ép màu chữ gốc của thẻ thành đen */
        color: #000000 !important; 
    }

    /* 2. Ép tất cả các thành phần con (p, div, span) bên trong card thành màu đen 
       để chống lại setting mặc định của Streamlit Dark Mode */
    .lucky-card div, .lucky-card p, .lucky-card span {
        color: #000000 !important;
    }

    /* 3. Style cho số to */
    .big-number {
        font-size: 36px !important;
        font-weight: 900 !important;
        margin-bottom: 5px;
        line-height: 1.2;
    }

    /* 4. Style cho box thông tin Mệnh ở trên */
    .result-header-box {
        border: 2px solid #1565C0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        background-color: #E3F2FD; /* Xanh rất nhạt */
        color: #0d47a1 !important; /* Xanh đậm */
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .result-header-box h3, .result-header-box div {
        color: #0d47a1 !important;
    }
    
    /* 5. Style cho Intro text */
    .intro-text {
        font-family: "Times New Roman";
        font-size: 18px;
        font-style: italic;
        text-align: justify;
        background-color: #eceff1;
        color: #37474f !important;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #607d8b;
    }

    /* 6. Style cho Summary box */
    .summary-box {
        margin-top: 25px;
        padding: 15px;
        background-color: #FFF3E0;
        border: 1px dashed #FF9800;
        border-radius: 5px;
        color: #333 !important;
    }
    .summary-box b, .summary-box div {
        color: #000000 !important;
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

# --- HÀM LOGIC ---

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

# --- UI CHÍNH ---

st.title("18h30 Team")
st.subheader("DỰ ĐOÁN SỐ MAY MẮN & PHONG THỦY")

st.markdown("""
<div class="intro-text">
    Ngẫu nhiên không được tạo ra. Nó được khai sinh.<br>
    Sử dụng Entropy, Kinh dịch thời gian thực kết hợp với Ngũ Hành Bát Quái để tìm ra con số không chỉ ngẫu nhiên mà còn hòa hợp với vận mệnh của bạn.
</div>
""", unsafe_allow_html=True)

if not HAS_LUNAR_LIB:
    st.warning("⚠️ Chưa cài đặt thư viện 'lunardate'. Vui lòng chạy: pip install lunardate")

st.divider()

with st.form("main_form"):
    st.markdown("**1. Ngày sinh (Để tính Mệnh)**")
    dob = st.date_input("Chọn ngày sinh", min_value=datetime(1900, 1, 1), value=datetime(2000, 1, 1))

    st.markdown("**2. Bạn chọn số cho ngày nào?**")
    target_date = st.date_input("Chọn ngày dự đoán", value=datetime.now())

    st.markdown("**3. Những con số bạn đang nghĩ tới (Tối đa 5 số có 2 chữ số)**")
    cols = st.columns(5)
    fav_inputs = []
    for i, col in enumerate(cols):
        with col:
            val = st.text_input(f"Số {i+1}", max_chars=2, placeholder="--")
            fav_inputs.append(val)

    submitted = st.form_submit_button("PHÂN TÍCH & LUẬN GIẢI", use_container_width=True, type="primary")

if submitted:
    valid_favs = []
    errors = []
    for i, f in enumerate(fav_inputs, 1):
        f = f.strip()
        if f:
            if not f.isdigit() or len(f) != 2: errors.append(f"Số thứ {i} ('{f}') không hợp lệ.")
            else: valid_favs.append(f)
    
    if errors:
        for e in errors: st.error(e)
    else:
        with st.spinner("Đang kết nối Server & Tính toán..."):
            now_dt, is_online = get_google_time_hanoi()
            lunar_year = get_lunar_year_number(dob)
            user_menh = calculate_menh_nien(lunar_year)
            
            # Seed generator
            dob_str = dob.strftime("%d%m%Y")
            target_str = target_date.strftime("%d%m%Y")
            seed_val = f"{dob_str}{target_str}{now_dt.strftime('%d%m%Y%H%M%S')}{''.join(valid_favs)}"
            random.seed(seed_val)
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # HEADER KẾT QUẢ
            st.markdown(f"""
            <div class="result-header-box">
                <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">BẠN SINH NĂM {lunar_year} (ÂM LỊCH) - MỆNH {user_menh}</div>
                <h3 style="margin:0;">KẾT QUẢ PHÂN TÍCH</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # HIỂN THỊ SỐ
            cols = st.columns(5)
            compatible_count = 0
            
            for idx, num in enumerate(kq):
                num_menh = get_number_element(num)
                is_hop, ly_do = check_compatibility(user_menh, num_menh)
                
                # Màu sắc riêng cho từng số
                if is_hop:
                    compatible_count += 1
                    num_color = "#1b5e20" # Xanh đậm
                    # UPDATED: Viền dày 5px và màu xanh lá đậm
                    border_css = "5px solid #2E7D32" 
                    note_color = "#2E7D32"
                else:
                    num_color = "#212121" # Đen xám
                    border_css = "1px solid #B0BEC5"
                    note_color = "#546E7A"
                
                with cols[idx]:
                    # Sử dụng class .lucky-card đã định nghĩa ở CSS
                    st.markdown(f"""
                    <div class="lucky-card" style="border: {border_css};">
                        <div class="big-number" style="color: {num_color} !important;">{num}</div>
                        <div style="font-size: 14px; font-weight: bold; color: #424242 !important;">Hành: {num_menh}</div>
                        <div style="font-size: 13px; margin-top: 5px; color: {note_color} !important; font-weight: bold;">{ly_do}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # SUMMARY
            st.markdown(f"""
            <div class="summary-box">
                <b>🔮 TỔNG KẾT:</b><br>
                Có <b>{compatible_count}/5</b> con số hợp mệnh (Tương sinh/Bình hòa).<br>
                <i>(Hành của số tính theo Hà Đồ)</i>
            </div>
            """, unsafe_allow_html=True)
            
            # Time check
            source = "Google Server" if is_online else "Offline"
            st.caption(f"Giờ động tâm: {now_dt.strftime('%H:%M:%S')} ({source})")

st.markdown('<div class="footer">Created by MinhMup</div>', unsafe_allow_html=True)