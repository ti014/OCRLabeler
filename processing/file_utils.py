import os
from tkinter import messagebox

def load_labels(label_file_path):
    """Tải nhãn từ file"""
    labels = {}
    with open(label_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) == 2:
                image_path, label = parts
                labels[os.path.basename(image_path)] = label
    return labels


def save_labels(labels, image_dir):
    """Lưu nhãn vào file với đường dẫn tương đối chứa dấu '/'"""
    label_file = os.path.join(image_dir, 'label.txt')
    with open(label_file, 'w', encoding='utf-8') as f:
        for image, label in labels.items():
            # Tạo đường dẫn tương đối và thay thế dấu \ bằng /
            relative_image_path = os.path.join(os.path.basename(image_dir), image).replace("\\", "/")
            f.write(f"{relative_image_path}\t{label}\n")

def run_predict_all(image_dir, filtered_image_list, ocr_core, labels, progress, update_progress, cancel_prediction):
    """Chạy dự đoán tất cả hình ảnh và lưu trực tiếp vào file label.txt"""
    label_file_path = os.path.join(image_dir, "label.txt")

    # Mở file label.txt để ghi
    with open(label_file_path, 'w', encoding='utf-8') as label_file:
        total_images = len(filtered_image_list)
        progress['value'] = 0
        progress['maximum'] = total_images

        for i, image_name in enumerate(filtered_image_list):
            if cancel_prediction:  # Kiểm tra nếu người dùng đã hủy
                messagebox.showinfo("Cancelled", "Prediction process was cancelled.")
                break

            # Dự đoán nhãn cho từng hình ảnh
            image_path = os.path.join(image_dir, image_name)
            predicted_text = ocr_core.predict_label(image_path)  # Gọi hàm dự đoán

            # Tạo đường dẫn tương đối và thay thế dấu \ bằng /
            relative_image_path = os.path.join(os.path.basename(image_dir), image_name).replace("\\", "/")

            # Ghi nhãn vào file
            label_file.write(f"{relative_image_path}\t{predicted_text}\n")

            # Lưu nhãn vào bộ nhớ để có thể sử dụng lại nếu cần
            labels[image_name] = predicted_text

            # Cập nhật tiến trình và danh sách ảnh đã dự đoán trên giao diện
            update_progress(i + 1, image_name)

    if not cancel_prediction:
        messagebox.showinfo("Success", f"Labels predicted for all images and saved to {label_file_path}")

def search_image(image_list, search_term):
    """Tìm kiếm hình ảnh theo từ khóa"""
    for image in image_list:
        if search_term.lower() in image.lower():
            return image
    return None
