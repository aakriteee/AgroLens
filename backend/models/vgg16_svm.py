


import os
import numpy as np
import joblib
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model

from utils.preprocessing import load_and_preprocess_image

MODEL_DIR = os.path.dirname(__file__)
SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_classifier.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# Recommendation shown to the farmer alongside the prediction.
# Kept simple/generic on purpose -- swap in agronomist-approved text later.
RECOMMENDATIONS = {
    "Healthy": "Leaf looks healthy. No action needed, keep monitoring weekly.",
    "Early_Blight": "Early blight detected. Remove affected leaves, apply a "
                     "copper-based or chlorothalonil fungicide, and avoid "
                     "overhead watering to reduce leaf wetness.",
    "Late_Blight": "Late blight detected -- this spreads fast. Remove and "
                    "destroy infected plants, apply a systemic fungicide "
                    "immediately, and improve field air circulation.",
    "Leaf_Mold": "Leaf mold detected. Improve greenhouse/field ventilation, "
                 "reduce humidity around plants, and apply a suitable "
                 "fungicide if spread continues.",
}


class DiseaseDetector:
    """Loads VGG16 (feature extractor) + trained SVM once, then reused
    for every prediction. Instantiate this ONCE at Flask app startup,
    not per-request -- loading VGG16 weights is slow."""

    def __init__(self):
        # include_top=False -> drop VGG16's original 1000-class ImageNet
        # classifier head, we only want the convolutional feature maps.
        # pooling='avg' -> global average pool the last conv block down
        # to a flat 512-d vector per image (instead of a 7x7x512 tensor).
        base_model = VGG16(weights="imagenet", include_top=False, pooling="avg")
        self.feature_extractor = Model(
            inputs=base_model.input, outputs=base_model.output
        )

        if not os.path.exists(SVM_MODEL_PATH):
            raise FileNotFoundError(
                f"No trained SVM found at {SVM_MODEL_PATH}. "
                "Run `python models/train_model.py` first."
            )

        self.svm = joblib.load(SVM_MODEL_PATH)
        self.label_encoder = joblib.load(LABEL_ENCODER_PATH)

    def extract_features(self, preprocessed_image):
        """preprocessed_image: numpy array (1, 224, 224, 3) -> (1, 512) features"""
        features = self.feature_extractor.predict(preprocessed_image, verbose=0)
        return features

    def predict(self, image_path_or_file):
        """
        Returns: (label:str, confidence:float 0-1, all_class_probs:dict)
        """
        preprocessed = load_and_preprocess_image(image_path_or_file)
        features = self.extract_features(preprocessed)

        # SVM was trained with probability=True so predict_proba is available
        probs = self.svm.predict_proba(features)[0]
        class_index = int(np.argmax(probs))
        label = self.label_encoder.inverse_transform([class_index])[0]
        confidence = float(probs[class_index])

        all_class_probs = {
            cls: float(p)
            for cls, p in zip(self.label_encoder.classes_, probs)
        }

        return label, confidence, all_class_probs

    def get_recommendation(self, label):
        return RECOMMENDATIONS.get(label, "No recommendation available.")
