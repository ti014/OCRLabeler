import torch
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg
from PIL import Image
from config.app_config import app_config
class OCRCore:
    def __init__(self):
        self.detector = self.setup_ocr_model()

    def setup_ocr_model(self):
        """Thiết lập mô hình OCR"""
        # Load cấu hình mô hình từ file app_config
        model_config = Cfg.load_config_from_file(app_config['OCR_CFG'])
        model_config['cnn']['pretrained'] = False
        model_config['device'] = app_config.get('device', 'cpu')

        if torch.cuda.is_available():
            model_config['device'] = 'cuda:0'

        # Thiết lập đường dẫn trọng số từ app_config
        model_config['weights'] = app_config['OCR_MODEL_PATH']

        return Predictor(model_config)

    def predict_label(self, image_path):
        """Dự đoán nhãn từ hình ảnh"""
        try:
            img = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise ValueError(f"Cannot open image from {image_path}: {e}")
        return self.detector.predict(img)
