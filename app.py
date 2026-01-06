import streamlit as st
import urllib.request
import random
import time
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
    page_title="18h30 Team - Phong Thủy & Boss Mode",
    page_icon="🔮",
    layout="centered"
)

# --- CSS FIX LỖI DARK MODE & UI ---
st.markdown("""
<style>
    /* 1. Class cho thẻ kết quả (Card) */
    .lucky-card {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #000000 !important; 
    }

    .lucky-card div, .lucky-card p, .lucky-card span {
        color: #000000 !important;
    }

    /* 2. Style cho số to */
    .big-number {
        font-size: 36px !important;
        font-weight: 900 !important;
        margin-bottom: 5px;
        line-height: 1.2;
    }

    /* 3. Style cho box thông tin Mệnh ở trên */
    .result-header-box {
        border: 2px solid #1565C0;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        background-color: #E3F2FD;
        color: #0d47a1 !important;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .result-header-box h3, .result-header-box div {
        color: #0d47a1 !important;
    }
    
    /* 4. Style cho Intro text */
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

    /* 5. Style cho Summary box */
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
    
    /* Boss Mode Styles */
    .boss-status {
        padding: 10px;
        background-color: #e8f5e9;
        color: #2e7d32;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 10px;
        font-weight: bold;
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
        with urllib.request.urlopen(req, timeout=2) as response:
            date_str = response.headers['Date']
            utc_time = parsedate_to_datetime(date_str)
            return (utc_time + timedelta(hours=7)).replace(tzinfo=None), True
    except:
        return datetime.now(), False

# Hàm cốt lõi để tính toán (Dùng chung cho cả nút thường và nút Boss)
def calculate_logic(dob, target_date, valid_favs):
    # Lấy giờ thực
    now_dt, _ = get_google_time_hanoi()
    
    # Tính mệnh
    lunar_year = get_lunar_year_number(dob)
    user_menh = calculate_menh_nien(lunar_year)
    
    # Tạo seed
    dob_str = dob.strftime("%d%m%Y")
    target_str = target_date.strftime("%d%m%Y")
    # Seed bao gồm cả giây hiện tại để thay đổi mỗi lần chạy
    seed_val = f"{dob_str}{target_str}{now_dt.strftime('%d%m%Y%H%M%S')}{''.join(valid_favs)}"
    random.seed(seed_val)
    
    # Random 5 số
    kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
    
    # Kiểm tra độ hợp
    details = []
    compatible_count = 0
    for num in kq:
        num_menh = get_number_element(num)
        is_hop, ly_do = check_compatibility(user_menh, num_menh)
        if is_hop:
            compatible_count += 1
        details.append({
            "num": num,
            "menh": num_menh,
            "is_hop": is_hop,
            "ly_do": ly_do
        })
        
    return {
        "lunar_year": lunar_year,
        "user_menh": user_menh,
        "kq": kq,
        "details": details,
        "compatible_count": compatible_count,
        "now_dt": now_dt
    }

def display_results(result_data):
    # HEADER KẾT QUẢ
    st.markdown(f"""
    <div class="result-header-box">
        <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">BẠN SINH NĂM {result_data['lunar_year']} (ÂM LỊCH) - MỆNH {result_data['user_menh']}</div>
        <h3 style="margin:0;">KẾT QUẢ PHÂN TÍCH</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # HIỂN THỊ SỐ
    cols = st.columns(5)
    
    for idx, item in enumerate(result_data['details']):
        # Màu sắc riêng cho từng số
        if item['is_hop']:
            num_color = "#1b5e20" # Xanh đậm
            border_css = "5px solid #2E7D32" 
            note_color = "#2E7D32"
        else:
            num_color = "#212121" # Đen xám
            border_css = "1px solid #B0BEC5"
            note_color = "#546E7A"
        
        with cols[idx]:
            st.markdown(f"""
            <div class="lucky-card" style="border: {border_css};">
                <div class="big-number" style="color: {num_color} !important;">{item['num']}</div>
                <div style="font-size: 14px; font-weight: bold; color: #424242 !important;">Hành: {item['menh']}</div>
                <div style="font-size: 13px; margin-top: 5px; color: {note_color} !important; font-weight: bold;">{item['ly_do']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # SUMMARY
    st.markdown(f"""
    <div class="summary-box">
        <b>🔮 TỔNG KẾT:</b><br>
        Có <b>{result_data['compatible_count']}/5</b> con số hợp mệnh (Tương sinh/Bình hòa).<br>
        <i>(Hành của số tính theo Hà Đồ)</i>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-top: 10px;">
        Giờ động tâm: {result_data['now_dt'].strftime('%H:%M:%S - %d/%m/%Y')}
    </div>
    """, unsafe_allow_html=True)

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

# Session state cho Boss Mode
if 'boss_active' not in st.session_state:
    st.session_state.boss_active = False

with st.form("main_form"):
    st.markdown("**1. Ngày sinh (Để tính Mệnh)**")
    dob = st.date_input("Chọn ngày sinh", min_value=datetime(1900, 1, 1), value=datetime(2000, 1, 1))

    st.markdown("**2. Bạn chọn số cho ngày nào?**")
    target_date = st.date_input("Chọn ngày dự đoán", value=datetime.now())

    st.markdown("**3. Những con số bạn đang nghĩ tới (Tối đa 5 số có 2 chữ số)**")
    cols = st.columns(5)
    fav_inputs = []
    # Lưu giá trị input vào biến ngoài để dùng cho Boss mode
    fav_values = [] 
    
    for i, col in enumerate(cols):
        with col:
            # Key giúp giữ giá trị khi rerun
            val = st.text_input(f"Số {i+1}", max_chars=2, placeholder="--", key=f"fav_{i}")
            fav_inputs.append(val)
            fav_values.append(val)

    submitted = st.form_submit_button("PHÂN TÍCH & LUẬN GIẢI", use_container_width=True, type="primary")

# NÚT BOSS (Nằm ngoài form)
if st.button("BOSS", use_container_width=True):
    st.session_state.show_boss_login = True

# LOGIC XỬ LÝ
# 1. Xử lý khi bấm nút thường
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
        with st.spinner("Đang tính toán..."):
            result = calculate_logic(dob, target_date, valid_favs)
            display_results(result)

# 2. Xử lý Boss Mode
if st.session_state.get("show_boss_login"):
    st.markdown("### 🔒 Chế độ BOSS")
    password = st.text_input("Nhập mật khẩu kích hoạt:", type="password")
    
    if st.button("Kích hoạt chạy tự động"):
        if password == "DAANEU123":
            st.session_state.boss_active = True
            st.session_state.show_boss_login = False # Ẩn login
            st.rerun()
        else:
            st.error("Sai mật khẩu!")

if st.session_state.get("boss_active"):
    # Kiểm tra input hợp lệ trước khi chạy
    valid_favs = [f.strip() for f in fav_values if f.strip().isdigit() and len(f.strip()) == 2]
    
    st.info("Đang chạy chế độ BOSS... (Dừng khi: 5/5 số hợp mệnh VÀ có số trùng giây hiện tại)")
    status_placeholder = st.empty()
    result_placeholder = st.empty()
    
    stop_loop = False
    
    while not stop_loop:
        # Chạy logic phân tích
        res = calculate_logic(dob, target_date, valid_favs)
        
        current_second = res['now_dt'].second
        
        # Điều kiện dừng:
        # 1. 5/5 số hợp mệnh (compatible_count == 5)
        # 2. 1 trong 5 số trùng với giây hiện tại
        
        cond_1 = (res['compatible_count'] == 5)
        cond_2 = any(int(num) == current_second for num in res['kq'])
        
        # Hiển thị trạng thái chạy thời gian thực
        with status_placeholder.container():
            st.markdown(f"""
            <div class='boss-status'>
                Giây hiện tại: {current_second:02d} | Số tìm được: {', '.join(res['kq'])}<br>
                Số lượng hợp mệnh: {res['compatible_count']}/5
            </div>
            """, unsafe_allow_html=True)
        
        if cond_1 and cond_2:
            stop_loop = True
            status_placeholder.empty() # Xóa dòng trạng thái
            st.balloons()
            st.success(f"🎯 ĐÃ TÌM THẤY! Giây động tâm: {current_second}")
            # Hiển thị kết quả cuối cùng
            display_results(res)
            
            # Thêm nút Reset để tắt mode
            if st.button("Dừng chế độ BOSS"):
                st.session_state.boss_active = False
                st.rerun()
            break
        
        # Chờ 1 giây rồi lặp lại
        time.sleep(1)

# Footer nằm ngoài cùng để luôn hiển thị
st.markdown('<div class="footer">Created by MinhMup</div>', unsafe_allow_html=True)