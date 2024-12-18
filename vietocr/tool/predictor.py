from vietocr.tool.translate import build_model, translate, translate_beam_search, process_input
import os
import torch
from collections import defaultdict

class Predictor:
    def __init__(self, config):
        self.config = config
        self.device = config['device']

        # Xây dựng mô hình và từ điển
        self.model, self.vocab = build_model(config)

        # Kiểm tra nếu 'weights' không tồn tại trong cấu hình
        if 'weights' not in config:
            raise KeyError("Configuration is missing the 'weights' key")

        # Đoạn mã sau để lấy đường dẫn trọng số
        base_path = os.path.abspath(".")
        weights_path = os.path.join(base_path, config['weights'])

        # Kiểm tra xem trọng số có tồn tại không
        if not os.path.exists(weights_path):
            raise FileNotFoundError(f"Weights file not found at {weights_path}")

        # Load trọng số mô hình
        self.model.load_state_dict(torch.load(weights_path, map_location=torch.device(self.device)))
        self.model.to(self.device)

    def predict(self, img, return_prob=False):
        # Xử lý ảnh đầu vào
        img = process_input(img, self.config['dataset']['image_height'], 
                            self.config['dataset']['image_min_width'], 
                            self.config['dataset']['image_max_width'])
        img = img.to(self.device)

        # Dự đoán với beam search hoặc không
        if self.config['predictor']['beamsearch']:
            s = translate_beam_search(img, self.model)
            prob = None
        else:
            s, prob = translate(img, self.model)
            s = s[0].tolist()
            prob = prob[0]

        # Giải mã kết quả dự đoán
        result = self.vocab.decode(s)

        if return_prob:
            return result, prob
        else:
            return result

    def predict_batch(self, imgs, return_prob=False):
        bucket = defaultdict(list)
        bucket_idx = defaultdict(list)
        bucket_pred = {}

        sents, probs = [0] * len(imgs), [0] * len(imgs)

        for i, img in enumerate(imgs):
            img = process_input(img, self.config['dataset']['image_height'], 
                                self.config['dataset']['image_min_width'], 
                                self.config['dataset']['image_max_width'])
            bucket[img.shape[-1]].append(img)
            bucket_idx[img.shape[-1]].append(i)

        for k, batch in bucket.items():
            batch = torch.cat(batch, 0).to(self.device)
            s, prob = translate(batch, self.model)
            prob = prob.tolist()

            s = s.tolist()
            s = self.vocab.batch_decode(s)

            bucket_pred[k] = (s, prob)

        for k in bucket_pred:
            idx = bucket_idx[k]
            sent, prob = bucket_pred[k]
            for i, j in enumerate(idx):
                sents[j] = sent[i]
                probs[j] = prob[i]

        if return_prob:
            return sents, probs
        else:
            return sents
