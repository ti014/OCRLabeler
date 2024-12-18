# OCRLabeler

## Giới thiệu

OCRLabeler là một ứng dụng giao diện người dùng (GUI) được xây dựng bằng Python và Tkinter, giúp người dùng dễ dàng gán nhãn cho các hình ảnh sử dụng công nghệ nhận dạng ký tự quang học (OCR).



## Cài đặt

1. **Clone dự án từ GitHub:**

    ```sh
    git clone https://github.com/ti014/OCRLabeler.git
    cd OCRLabelTool
    ```

2. **Cài đặt các thư viện cần thiết:**

    Sử dụng `pip` để cài đặt các thư viện từ file [requirements.txt](./requirements.txt):

    ```sh
    pip install -r requirements.txt
    ```

## Sử dụng

1. **Chạy ứng dụng:**

    Chạy file [main.py](./main.py) để khởi động ứng dụng:

    ```sh
    python main.py
    ```

2. **Giao diện người dùng:**

    - **Chọn thư mục hình ảnh:** Nhấn nút "Image Dir" để chọn thư mục chứa các hình ảnh cần gán nhãn.
    - **Tải nhãn:** Nhấn nút "Load Labels" để tải các nhãn từ file.
    - **Lưu nhãn:** Nhấn nút "Save Labels" để lưu các nhãn vào file.
    - **Dự đoán nhãn:** Nhấn nút "Predict Image" để dự đoán nhãn cho hình ảnh hiện tại.
    - **Xóa hình ảnh:** Nhấn nút "Delete Image" để xóa hình ảnh hiện tại.
    - **Dự đoán tất cả:** Nhấn nút "Predict All" để dự đoán nhãn cho tất cả các hình ảnh trong thư mục.
## Demo
- Phần giao diện:
![Demo1](./images/1.jpg)
- Nhãn sau khi save sẽ nằm cùng thư mục ảnh và có cấu trúc sau:
![Demo2](./images/2.jpg)

## Cấu hình

File cấu hình [app_config.py](./config/app_config.py) chứa các thông tin cấu hình cho mô hình OCR và đường dẫn tới các file trọng số và cấu hình.

## Đóng gói ứng dụng

Sử dụng `PyInstaller` để đóng gói ứng dụng thành file thực thi:

```sh
pyinstaller main.spec
```

## Model Weights

Bạn có thể tải file trọng số của mô hình tại [đây](https://github.com/ti014/OCRLabeler/releases/download/v1.0/vgg_transformer.zip).
