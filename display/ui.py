import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from processing.image_utils import load_image_to_canvas, zoom_in, zoom_out
from processing.file_utils import load_labels, save_labels, search_image, run_predict_all
from model.ocr_model import OCRCore
import os
from PIL import Image
import threading

class OCRLabelTool:
    def __init__(self, master):
        self.master = master
        self.master.title("OCR Label Tool")
        self.master.geometry("950x720")
        self.master.configure(bg='#f0f0f0')

        self.image_dir = ""
        self.image_list = []
        self.filtered_image_list = []
        self.current_image_index = 0
        self.labels = {}
        self.history = []  # Initialize history to keep track of actions
        self.show_all = tk.BooleanVar(value=True)  # For filtering images
        self.images_per_page = tk.IntVar(value=1)  # Default images per page
        self.current_page = 0  # To track pagination

        self.ocr_core = OCRCore()  # Initialize OCR model
        self.cancel_prediction = False  # Biến để kiểm soát việc hủy dự đoán

        self.setup_ui()

        # Bind events for keyboard shortcuts
        self.master.bind("<Tab>", lambda event: self.next_image())
        self.master.bind("<Shift-Tab>", lambda event: self.prev_image())
        self.master.bind_all("<Alt-KeyPress>", self.handle_alt_shortcuts)

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Khung trái cho các nút điều khiển
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))


        button_width = 15  # Set a fixed width for all buttons
        ttk.Button(left_frame, text="Image Dir", command=self.choose_image_dir, width=button_width).grid(row=0, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Load Labels", command=self.load_labels, width=button_width).grid(row=1, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Save Labels", command=self.save_labels, width=button_width).grid(row=2, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Predict Image", command=self.predict_label, width=button_width).grid(row=3, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Delete Image", command=self.delete_image, width=button_width).grid(row=4, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Predict All", command=self.predict_all, width=button_width).grid(row=5, column=0, pady=5, sticky=tk.W)

        # Text input cho nhãn
        ttk.Label(left_frame, text="Label:").grid(row=6, column=0, pady=(20,5), sticky=tk.W)
        self.label_entry = tk.Text(left_frame, width=40, height=4, wrap=tk.WORD)
        self.label_entry.grid(row=7, column=0, pady=5, sticky=tk.W)

        # Tìm kiếm hình ảnh
        ttk.Label(left_frame, text="Search Image:").grid(row=8, column=0, pady=(20,5), sticky=tk.W)
        self.search_entry = ttk.Entry(left_frame, width=30)
        self.search_entry.grid(row=9, column=0, pady=5, sticky=tk.W)
        ttk.Button(left_frame, text="Search", command=self.search_image, width=button_width).grid(row=10, column=0, pady=5, sticky=tk.W)

        # Filter (All/Labeled/Unlabeled)
        self.filter_var = tk.StringVar(value="all")
        ttk.Radiobutton(left_frame, text="Show All", variable=self.filter_var, value="all", command=self.update_filter).grid(row=11, column=0, pady=(10,5), sticky=tk.W)
        ttk.Radiobutton(left_frame, text="Labeled", variable=self.filter_var, value="labeled", command=self.update_filter).grid(row=12, column=0, pady=(10,5), sticky=tk.W)
        ttk.Radiobutton(left_frame, text="Unlabeled", variable=self.filter_var, value="unlabeled", command=self.update_filter).grid(row=13, column=0, pady=(10,5), sticky=tk.W)

        # Progress bar để hiển thị tiến độ
        self.progress = ttk.Progressbar(left_frame, orient='horizontal', length=200, mode='determinate')
        self.progress.grid(row=14, column=0, pady=5, sticky=tk.W)

        # Nút Cancel để ngừng quá trình dự đoán
        self.cancel_button = ttk.Button(left_frame, text="Cancel", command=self.cancel_predict_all)
        self.cancel_button.grid(row=14, column=1, padx=5, pady=5, sticky=tk.W)

        # Label để hiển thị danh sách ảnh đã predict
        self.predicted_image_label = tk.Label(left_frame, text="Predicted Images:", anchor="w")
        self.predicted_image_label.grid(row=15, column=0, pady=5, sticky=tk.W)
        self.predicted_images_listbox = tk.Listbox(left_frame, width=55, height=4)
        self.predicted_images_listbox.grid(row=16, column=0, pady=5, sticky=tk.W)

        # Khung bên phải cho hiển thị hình ảnh
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(1, weight=1)

        # Canvas cho hiển thị hình ảnh
        self.canvas = tk.Canvas(right_frame, width=260, height=260, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Nút zoom in và zoom out
        zoom_frame = ttk.Frame(right_frame, padding="5")
        zoom_frame.pack(side=tk.TOP, pady=5)
        ttk.Button(zoom_frame, text="+ Zoom In +", command=self.zoom_in).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(zoom_frame, text="- Zoom Out -", command=self.zoom_out).pack(side=tk.LEFT, padx=5, pady=5)

        # Hiển thị số thứ tự hình ảnh
        self.image_number_label = ttk.Label(right_frame, text="Image: 0 / 0")
        self.image_number_label.pack(pady=10)

        # Hiển thị tên file
        file_frame = ttk.Frame(right_frame)
        file_frame.pack(pady=10)
        self.file_name_label = ttk.Label(file_frame, text="Current file: None")
        self.file_name_label.pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Copy", command=self.copy_file_name).pack(side=tk.LEFT, padx=1, pady=1)

        # Điều hướng hình ảnh
        navigation_frame = ttk.Frame(right_frame, padding="5")
        navigation_frame.pack(side=tk.TOP, pady=5)
        ttk.Button(navigation_frame, text="Back image", command=self.prev_image).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(navigation_frame, text="Next image", command=self.next_image).pack(side=tk.LEFT, padx=5, pady=5)

    def choose_image_dir(self):
        """Chọn thư mục chứa hình ảnh"""
        self.image_dir = filedialog.askdirectory()
        self.image_list = [f for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
        self.filtered_image_list = self.image_list  # Mặc định hiển thị tất cả hình ảnh
        self.load_image()

    def load_labels(self):
        """Tải nhãn từ file"""
        label_file = filedialog.askopenfilename(initialdir=self.image_dir, filetypes=[("Text files", "*.txt")])
        if label_file:
            self.labels = load_labels(label_file)
            if self.filtered_image_list and self.filtered_image_list[self.current_image_index] in self.labels:
                self.label_entry.delete('1.0', tk.END)
                self.label_entry.insert(tk.END, self.labels[self.filtered_image_list[self.current_image_index]])
    

    def save_labels(self):
        """Lưu nhãn vào file"""
        if not self.image_dir:
            messagebox.showerror("Error", "Please choose an image directory first.")
            return
        self.save_current_label()
        save_labels(self.labels, self.image_dir)
        messagebox.showinfo("Success", f"Labels saved successfully to {self.image_dir}/label.txt")
    

    def load_image(self):
        """Load và hiển thị hình ảnh hiện tại"""
        if self.filtered_image_list:
            image_path = os.path.join(self.image_dir, self.filtered_image_list[self.current_image_index])
            self.image = Image.open(image_path)
            load_image_to_canvas(self.canvas, self.image, self.canvas.winfo_width(), self.canvas.winfo_height())

            # Hiển thị nhãn cho hình ảnh hiện tại
            self.label_entry.delete('1.0', tk.END)
            if self.filtered_image_list[self.current_image_index] in self.labels:
                self.label_entry.insert(tk.END, self.labels[self.filtered_image_list[self.current_image_index]])

            self.update_image_number_label()

    def update_image_number_label(self):
        """Cập nhật nhãn hiển thị số lượng hình ảnh"""
        total_images = len(self.filtered_image_list)
        current_image = self.current_image_index + 1
        current_file_name = self.filtered_image_list[self.current_image_index]
        self.image_number_label.config(text=f"Image {current_image} of {total_images}")
        self.file_name_label.config(text=f"Current file: {current_file_name}")

    def prev_image(self):
        """Chuyển đến hình ảnh trước đó"""
        if self.current_image_index > 0:
            self.save_current_label()
            self.current_image_index -= 1
            self.load_image()
        else:
            messagebox.showinfo("Info", "This is the last image.")

    def next_image(self):
        """Chuyển đến hình ảnh tiếp theo"""
        if self.current_image_index < len(self.filtered_image_list) - 1:
            self.save_current_label()
            self.current_image_index += 1
            self.load_image()
        else:
            messagebox.showinfo("Info", "This is the first image.")

    def save_current_label(self):
        """Lưu nhãn cho hình ảnh hiện tại"""
        current_image = self.filtered_image_list[self.current_image_index]
        current_label = self.label_entry.get('1.0', tk.END).strip()
        if current_label:
            self.labels[current_image] = current_label

    def predict_label(self):
        """Dự đoán nhãn cho hình ảnh hiện tại"""
        if self.filtered_image_list:
            image_path = os.path.join(self.image_dir, self.filtered_image_list[self.current_image_index])
            predicted_text = self.ocr_core.predict_label(image_path)
            self.label_entry.delete('1.0', tk.END)
            self.label_entry.insert(tk.END, predicted_text)

    def predict_all(self):
        """Khởi động luồng dự đoán tất cả hình ảnh"""
        if not self.filtered_image_list:
            messagebox.showerror("Error", "No images to predict.")
            return

        # Tạo và khởi động một luồng riêng để chạy quá trình dự đoán
        self.cancel_prediction = False
        prediction_thread = threading.Thread(target=run_predict_all, args=(
            self.image_dir,
            self.filtered_image_list,
            self.ocr_core,
            self.labels,
            self.progress,
            self.update_progress,
            self.cancel_prediction
        ))
        prediction_thread.start()



    def update_progress(self, value, image_name):
        """Cập nhật thanh tiến trình và danh sách ảnh đã dự đoán"""
        # Gọi cập nhật giao diện từ luồng chính
        self.master.after(0, lambda: self._update_progress_ui(value, image_name))

    def _update_progress_ui(self, value, image_name):
        """Thực hiện cập nhật UI - thanh tiến trình và danh sách ảnh"""
        self.progress['value'] = value
        self.predicted_images_listbox.insert(tk.END, image_name)
        self.master.update_idletasks()
    def cancel_predict_all(self):
        """Hủy quá trình dự đoán"""
        self.cancel_prediction = True


    def search_image(self):
        """Tìm kiếm hình ảnh"""
        search_term = self.search_entry.get().strip().lower()
        found_image = search_image(self.image_list, search_term)
        if found_image:
            self.current_image_index = self.image_list.index(found_image)
            self.load_image()
        else:
            messagebox.showerror("Error", "Image not found")

    def delete_image(self):
        """Xóa hình ảnh hiện tại"""
        if not self.filtered_image_list:
            messagebox.showerror("Error", "No image to delete.")
            return

        image_name = self.filtered_image_list[self.current_image_index]
        image_path = os.path.join(self.image_dir, image_name)

        # Remove the image and label
        deleted_annotation = self.labels.pop(image_name, None)
        self.history.append(('delete_image', image_path, self.current_image_index, deleted_annotation))

        try:
            os.remove(image_path)
        except OSError as e:
            messagebox.showerror("Error", f"Error deleting file: {e}")
            return

        # Update image lists
        if image_name in self.image_list:
            self.image_list.remove(image_name)
        if image_name in self.filtered_image_list:
            self.filtered_image_list.remove(image_name)

        self.update_filter()
        self.save_labels()

        # Load the next image if available, otherwise load the previous image
        if self.filtered_image_list:
            if self.current_image_index >= len(self.filtered_image_list):
                self.current_image_index = len(self.filtered_image_list) - 1
            self.load_image()
        else:
            self.canvas.delete("all")
            self.image_number_label.config(text="Image: 0 / 0")
            self.file_name_label.config(text="Current file: None")
            messagebox.showinfo("Info", "No more images.")


    def update_filter(self):
        """Cập nhật bộ lọc hình ảnh"""
        filter_value = self.filter_var.get()
        if filter_value == "all":
            self.filtered_image_list = self.image_list
        elif filter_value == "labeled":
            self.filtered_image_list = [img for img in self.image_list if img in self.labels]
        elif filter_value == "unlabeled":
            self.filtered_image_list = [img for img in self.image_list if img not in self.labels]

        if not self.filtered_image_list:
            self.canvas.delete("all")
            self.canvas.create_text(self.canvas.winfo_width() // 2, 
                                    self.canvas.winfo_height() // 2,
                                    text="No images to display", 
                                    font=("Arial", 20), 
                                    fill="gray")
        else:
            self.current_image_index = 0
            self.load_image()

    def zoom_in(self):
        """Phóng to hình ảnh"""
        if self.image:
            self.image = zoom_in(self.image)
            load_image_to_canvas(self.canvas, self.image, self.canvas.winfo_width(), self.canvas.winfo_height())

    def zoom_out(self):
        """Thu nhỏ hình ảnh"""
        if self.image:
            self.image = zoom_out(self.image)
            load_image_to_canvas(self.canvas, self.image, self.canvas.winfo_width(), self.canvas.winfo_height())

    def copy_file_name(self):
        """Copy tên file hiện tại vào clipboard"""
        current_file_name = self.file_name_label.cget("text").replace("Current file: ", "")
        self.master.clipboard_clear()
        self.master.clipboard_append(current_file_name)

    def handle_alt_shortcuts(self, event):
        """Xử lý các phím tắt Alt+D, Alt+R, Alt+W"""
        key = event.char.lower()
        if key == 'd':
            self.predict_label()  # Alt+D: Dự đoán nhãn cho hình ảnh hiện tại
        elif key == 'r':
            self.delete_image()   # Alt+R: Xóa hình ảnh hiện tại
        elif key == 'w':
            self.clear_and_focus_label()  # Alt+W: Xóa nội dung label và focus

    def clear_and_focus_label(self):
        """Clear the label entry and set focus to it."""
        self.label_entry.delete('1.0', tk.END)  # Xóa nội dung của text widget
        self.label_entry.focus_set()  # Đặt focus vào text widget

