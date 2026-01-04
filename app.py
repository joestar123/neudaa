import streamlit as st
import urllib.request
import random
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="NEU DAA Digital Team",
    page_icon="🔮",
    layout="centered"
)

# --- CSS TÙY CHỈNH ĐỂ GIỐNG GIAO DIỆN CŨ ---
st.markdown("""
<style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
        color: #D32F2F;
        text-align: center;
    }
    .result-box {
        border: 2px solid #1565C0;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        background-color: #f0f8ff;
        margin-top: 20px;
    }
    .intro-text {
        font-family: "Times New Roman";
        font-size: 18px;
        font-style: italic;
        text-align: justify;
        color: #455A64;
        background-color: #eceff1;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #607d8b;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. HÀM LẤY GIỜ TỪ GOOGLE (GIỮ NGUYÊN LOGIC) ---
def get_google_time_hanoi():
    try:
        req = urllib.request.Request("https://www.google.com", method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            date_str = response.headers['Date']
            utc_time = parsedate_to_datetime(date_str)
            hanoi_time = utc_time + timedelta(hours=7)
            return hanoi_time.replace(tzinfo=None), True
    except Exception as e:
        return datetime.now(), False

# --- 2. GIAO DIỆN CHÍNH ---

st.title("NEU DAA Digital Team")
st.subheader("DỰ ĐOÁN SỐ MAY MẮN")

# Đoạn văn giới thiệu Entropy
st.markdown("""
<div class="intro-text">
    Ngẫu nhiên không được tạo ra. Nó được khai sinh.<br><br>
    Từ Entropy — sự hỗn loạn nguyên thủy — hệ thống hấp thụ dữ liệu cá nhân và thời gian thực để định hình những con số chỉ tồn tại trong một khoảnh khắc duy nhất.<br><br>
    Khoảnh khắc trôi qua, con số biến mất. Không thể tái hiện.
</div>
""", unsafe_allow_html=True)

st.divider()

# --- FORM NHẬP LIỆU ---
with st.form("main_form"):
    # 1. Ngày sinh
    st.markdown("**1. Ngày sinh**")
    dob = st.date_input("Chọn ngày sinh của bạn", min_value=datetime(1900, 1, 1))

    # 2. Ngày chọn số
    st.markdown("**2. Bạn chọn số cho ngày nào?**")
    target_date = st.date_input("Chọn ngày muốn dự đoán", value=datetime.now())

    # 3. Số yêu thích (Đã sửa: Tối đa 5 số, không bắt buộc)
    st.markdown("**3. Những con số bạn đang nghĩ tới (2 chữ số, VD: 05, 99). Tối đa 5 số, có thể để trống.**")
    
    # Tạo 5 cột cho 5 ô nhập
    cols = st.columns(5)
    fav_inputs = []
    
    # Tạo input trong vòng lặp cho gọn
    for i, col in enumerate(cols):
        with col:
            val = st.text_input(f"Số {i+1}", max_chars=2, placeholder="--")
            fav_inputs.append(val)

    # Nút bấm
    submitted = st.form_submit_button("PHÂN TÍCH NGAY", use_container_width=True, type="primary")

# --- XỬ LÝ KHI BẤM NÚT ---
if submitted:
    # Validation logic mới
    valid_favs = []
    errors = []
    
    # Kiểm tra từng ô nhập
    for i, f in enumerate(fav_inputs, 1):
        f = f.strip() # Xóa khoảng trắng thừa
        if f: # Chỉ kiểm tra nếu người dùng CÓ nhập
            if not f.isdigit() or len(f) != 2:
                errors.append(f"Số thứ {i} ('{f}') không hợp lệ (Phải là 2 chữ số).")
            else:
                valid_favs.append(f)
    
    if errors:
        for e in errors:
            st.error(e)
    else:
        with st.spinner("Đang kết nối Google Server để lấy Entropy thời gian thực..."):
            # Lấy giờ
            now_dt, is_online = get_google_time_hanoi()
            
            # Hiển thị trạng thái kết nối
            time_color = "green" if is_online else "red"
            source_text = "Google Server" if is_online else "Offline Mode"
            st.markdown(f"⏱️ Time check: **{now_dt.strftime('%d/%m/%Y - %H:%M:%S')}** (<span style='color:{time_color}'>{source_text}</span>)", unsafe_allow_html=True)

            # --- TẠO SEED ---
            # Format lại ngày tháng từ object date sang chuỗi ddmmyyyy
            dob_str = dob.strftime("%d%m%Y")
            target_date_str = target_date.strftime("%d%m%Y")
            
            # Seed kết hợp: Ngày sinh + Ngày chọn + Thời gian thực + Số yêu thích (chỉ lấy số hợp lệ)
            # Nếu không nhập số nào, valid_favs là rỗng -> vẫn chạy bình thường dựa trên ngày giờ
            fav_string = "".join(valid_favs)
            
            seed_val = f"{dob_str}{target_date_str}{now_dt.strftime('%d%m%Y%H%M%S')}{fav_string}"
            
            # Debug (có thể xóa dòng này nếu không muốn hiện seed ra console)
            # print(f"Seed generated: {seed_val}") 
            
            # Áp dụng seed
            random.seed(seed_val)
            
            # Tạo 5 số ngẫu nhiên
            kq = [f"{random.randint(0,99):02d}" for _ in range(5)]
            
            # Hiển thị kết quả
            st.markdown(f"""
            <div class="result-box">
                <h3>KẾT QUẢ PHÂN TÍCH</h3>
                <div class="big-font">{kq[0]} - {kq[1]} - {kq[2]} - {kq[3]} - {kq[4]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.caption("Phân tích hoàn tất bởi NEU DAA Digital Team.")