# 📱 Ugphone All-In-One Tool

Tool tích hợp **Reg Acc + Auto Buy** và **Auto Get Gems + Order UVIP** trong cùng 1 script.

---

## ⚙️ Cách dùng

### 1️⃣ Cài đặt

- **Python 3.8+** 
- Cần có **Chrome** và **ChromeDriver** (tool sẽ tự tải nếu chưa có)
- Chuẩn bị file:
  - `proxies.txt`: danh sách proxy (mỗi dòng `ip:port`)
  - `accounts.txt`: (nếu chạy reg bằng file), mỗi dòng `email|password`

---

### 2️⃣ Chạy tool

#### 📌 Reg Acc Ugphone

```bash
python reg.py reg --quantity 10 --mode 1 --threads 3
```

**Tham số:**
- `--quantity`: số lượng acc cần reg
- `--mode`: 
  - `1` → dùng API auto buy
  - `2` → dùng file accounts.txt
- `--threads`: số luồng chạy song song

✅ **Kết quả:** file `registrations.txt` chứa format:
```
email|password|localStorage
```

#### 📌 Auto Get Kim Cương + Order UVIP

```bash
python autobuyug.py gems
```

- Nhập `localStorage` khi tool hỏi
- Tool sẽ tự động:
  - Lấy gems
  - Lấy config UVIP
  - Đặt order gói free 4 giờ

✅ **Output:** hiển thị Order ID khi thành công

---

## 📋 Cài đặt dependencies

```bash
pip install -r requirements.txt
```

---

## 📁 Cấu trúc thư mục

```
ugphone-tool/
├── reg.py
├── autobuyug.py
├── proxies.txt
├── accounts.txt
├── registrations.txt
└── requirements.txt
```

---

## ⚠️ Lưu ý

- Đảm bảo proxy hoạt động tốt để tránh bị block
- Không chạy quá nhiều luồng cùng lúc
- Kiểm tra kết nối internet ổn định

---

## ✍️ Tác giả

**Nguyễn Mạnh Hiếu (HieuDz)**

*Một phần tham khảo từ: withstock / github.com/longstock*
