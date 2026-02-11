# Demo2 – Xử lý & Kiểm tra Dữ liệu Bài hát 

## 1. Giới thiệu
Dự án **demo2** được xây dựng nhằm mục đích:
- Thu thập và xử lý dữ liệu bài hát
- Loại bỏ dữ liệu trùng lặp
- Tóm gọn thông tin bài hát bằng AI
- Kiểm tra tính toàn vẹn và trùng lặp của dữ liệu sau xử lý

Dự án sử dụng **Python** và **Jupyter Notebook**.

---

## 2. Cấu trúc thư mục

```text
demo2/
├── mocktest/
│   ├── mock_test_1_data_flow.py
│   └── mock_test_2_source1_logic.py
│
├── countsong.py
├── datasong-100.ipynb
├── solverawdata.py
├── testdescriptions.py
├── testmetadata.py
│
├── songs_dedup.json
├── songs_details.json
│
├── docs/
│   └── report.docx
│
└── README.md
```

---

## 3. Mô tả chi tiết các file

### mocktest/
Chứa các file **mock test** dùng để kiểm tra logic và luồng dữ liệu.

- **mock_test_1_data_flow.py**  
  → Kiểm tra luồng xử lý dữ liệu (data flow) từ dữ liệu đầu vào đến đầu ra.

- **mock_test_2_source1_logic.py**  
  → Kiểm tra logic xử lý dữ liệu từ nguồn dữ liệu số 1.

---

### countsong.py
- Dùng để **đếm số lượng bài hát** trong dữ liệu.
- Phục vụ việc kiểm tra quy mô dataset trước và sau khi xử lý.

---

### datasong-100.ipynb
- Jupyter Notebook lấy từ **Kaggle**
- Notebook **đã chạy cell mocktest**, dùng để demo hoặc phân tích dữ liệu ban đầu.

---

### solverawdata.py
- File chính để **xử lý dữ liệu thô**
- Thực hiện:
  - Làm sạch dữ liệu
  - Loại bỏ bài hát trùng lặp
- Xuất kết quả ra file:

---

### songs_dedup.json
- File JSON chứa **dữ liệu bài hát đã được loại bỏ trùng lặp**
- Là dữ liệu đầy đủ sau khi xử lý.

---

### songs_details.json
- File JSON chứa **dữ liệu đã được tóm gọn**
- Chỉ bao gồm:
- Tên bài hát
- Mô tả chung
- Phần mô tả được **AI suy luận và tóm tắt** từ dữ liệu gốc.

---

### testdescriptions.py
- Dùng để **test dữ liệu đầy đủ**
- Kiểm tra file:
- Mục tiêu:
- Phát hiện bài hát bị trùng
- Đảm bảo dữ liệu sau xử lý là duy nhất

---

### testmetadata.py
- Dùng để **test metadata**
- Kiểm tra file:


- Mục tiêu:
- Kiểm tra trùng lặp tên bài hát
- Đảm bảo dữ liệu tóm gọn không bị lặp

---

### docs/
- Chứa **file báo cáo dự án**
- Trình bày:
- Mục tiêu
- Quy trình xử lý dữ liệu
- Kết quả và đánh giá

---

## 4. Công nghệ sử dụng
- Python 3
- Jupyter Notebook
- JSON
- AI (cho bước tóm tắt dữ liệu)

---

## 5. Mục đích học tập
- Thực hành xử lý dữ liệu
- Làm quen với kiểm thử (testing)
- Áp dụng AI vào tiền xử lý dữ liệu
- Phục vụ bài tập lớn / demo môn học

---

## 6. Ghi chú
- Dự án mang tính học thuật
- Dữ liệu sử dụng cho mục đích học tập, không dùng thương mại

---

**Tác giả:** ChuTien  
**Project:** Demo2 – Python Data Processing
