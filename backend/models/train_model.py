

import os
import sys
import numpy as np
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras.applications import VGG16
from tensorflow.keras.models import Model

# allow `python models/train_model.py` to import sibling package `utils`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.preprocessing import load_and_preprocess_image  # noqa: E402

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset")
MODEL_DIR = os.path.dirname(__file__)
SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_classifier.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")


def build_feature_extractor():
    """Same VGG16 setup as models/vgg16_svm.py -- MUST stay identical."""
    base_model = VGG16(weights="imagenet", include_top=False, pooling="avg")
    return Model(inputs=base_model.input, outputs=base_model.output)


def load_dataset_and_extract_features(feature_extractor):
    """Walks dataset/<class_name>/*.jpg and returns (X_features, y_labels)."""
    if not os.path.isdir(DATASET_DIR):
        raise FileNotFoundError(
            f"Dataset folder not found at {DATASET_DIR}. "
            "Create backend/dataset/<ClassName>/ folders with leaf images "
            "(e.g. Healthy, Early_Blight, Late_Blight, Leaf_Mold)."
        )

    class_names = sorted(
        d for d in os.listdir(DATASET_DIR)
        if os.path.isdir(os.path.join(DATASET_DIR, d))
    )
    if not class_names:
        raise ValueError("No class subfolders found inside dataset/.")

    print(f"Found classes: {class_names}")

    features_list = []
    labels_list = []

    for class_name in class_names:
        class_dir = os.path.join(DATASET_DIR, class_name)
        image_files = [
            f for f in os.listdir(class_dir)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        print(f"  {class_name}: {len(image_files)} images")

        for i, filename in enumerate(image_files):
            image_path = os.path.join(class_dir, filename)
            try:
                preprocessed = load_and_preprocess_image(image_path)
                feature_vector = feature_extractor.predict(preprocessed, verbose=0)[0]
                features_list.append(feature_vector)
                labels_list.append(class_name)
            except Exception as e:
                print(f"    Skipping {filename}: {e}")

            if (i + 1) % 50 == 0:
                print(f"    ...{i + 1}/{len(image_files)} processed")

    X = np.array(features_list)
    y = np.array(labels_list)
    return X, y


def train_svm(X, y):
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    print("\nTraining SVM (RBF kernel)...")
    # probability=True is required so predict_proba() works at inference time
    svm = SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42)
    svm.fit(X_train, y_train)

    y_pred = svm.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    return svm, label_encoder


def main():
    print("Loading VGG16 feature extractor (ImageNet weights)...")
    feature_extractor = build_feature_extractor()

    print("Extracting features from dataset...")
    X, y = load_dataset_and_extract_features(feature_extractor)
    print(f"\nTotal samples: {len(X)}, feature dimension: {X.shape[1]}")

    svm, label_encoder = train_svm(X, y)

    joblib.dump(svm, SVM_MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    print(f"\nSaved trained SVM to: {SVM_MODEL_PATH}")
    print(f"Saved label encoder to: {LABEL_ENCODER_PATH}")


if __name__ == "__main__":
    main()
