import tkinter as tk
from PIL import Image, ImageTk

# Lưu trữ đối tượng ảnh toàn cục để không bị giải phóng bộ nhớ
def load_image_to_canvas(canvas, image, width, height):
    """Load và hiển thị hình ảnh lên canvas"""
    canvas.delete("all")
    # Resize image to fit the canvas if needed
    photo = ImageTk.PhotoImage(image)
    
    # Gán đối tượng PhotoImage cho canvas để không bị garbage collected
    canvas.image = photo  # Lưu ảnh dưới dạng thuộc tính của canvas
    canvas.create_image(width // 2, height // 2, anchor=tk.CENTER, image=photo)

def zoom_in(image):
    """Phóng to hình ảnh 10%"""
    new_width = int(image.width * 1.1)
    new_height = int(image.height * 1.1)
    return image.resize((new_width, new_height), Image.LANCZOS)

def zoom_out(image):
    """Thu nhỏ hình ảnh 10%"""
    new_width = int(image.width * 0.9)
    new_height = int(image.height * 0.9)
    return image.resize((new_width, new_height), Image.LANCZOS)
