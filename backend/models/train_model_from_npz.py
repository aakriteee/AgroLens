"""
train_model_from_npz.py
-------------------------
Alternative to train_model.py -- use this instead if your dataset is
already packaged as train_data.npz / val_data.npz (images + labels
as numpy arrays) rather than a folder of individual image files.

Expected input files (edit NPZ_DIR below if yours live elsewhere):
    backend/dataset_npz/train_data.npz   -> keys: "images", "labels"
    backend/dataset_npz/val_data.npz     -> keys: "images", "labels"
    backend/dataset_npz/label_encoder.pkl  (optional, joblib-saved)

Expected image array format: shape (N, 224, 224, 3), float32, values
already scaled to the 0-1 range (i.e. original_pixel / 255). This is
the common "cleaned/preprocessed" format many dataset-prep pipelines
produce. If your arrays are a different scale or size, see the NOTE
in `load_npz_split()` below.

WHY A SEPARATE SCRIPT: the original train_model.py reads raw image
files and applies VGG16's preprocess_input() during loading. Your
images are already resized + rescaled to [0,1], so this script
converts them back to the 0-255 range and applies the same
preprocess_input() step, so the VGG16 features produced here are
identical in kind to the ones produced at prediction time in
models/vgg16_svm.py (that consistency is what keeps accuracy high --
mismatched preprocessing between train and inference is one of the
most common causes of a model that scores well in training but badly
in the real app).

Run from the backend/ folder:
    python models/train_model_from_npz.py
"""

import os
import sys
import numpy as np
import joblib
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.models import Model

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NPZ_DIR = os.path.join(BACKEND_DIR, "dataset_npz")  # <-- put your files here
MODEL_DIR = os.path.dirname(__file__)
SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_classifier.pkl")
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

BATCH_SIZE = 32  # tune down (e.g. 8-16) if you hit memory errors


def build_feature_extractor():
    """Same VGG16 setup as models/vgg16_svm.py -- MUST stay identical."""
    base_model = VGG16(weights="imagenet", include_top=False, pooling="avg")
    return Model(inputs=base_model.input, outputs=base_model.output)


def load_npz_split(filename):
    """Loads one .npz split and returns (images_0to255_float, labels)."""
    path = os.path.join(NPZ_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find {path}. Put train_data.npz / val_data.npz "
            f"inside {NPZ_DIR}/"
        )

    data = np.load(path, allow_pickle=True)
    images = data["images"]
    labels = data["labels"]

    # NOTE: this assumes images are float32 scaled to [0, 1]. If your
    # arrays are already 0-255, delete the "* 255.0" line below. If
    # they're a different size than 224x224, resize them with
    # tf.image.resize before this step -- VGG16 needs exactly 224x224.
    if images.max() <= 1.0 + 1e-6:
        images = images * 255.0

    return images.astype(np.float32), labels


def extract_features_in_batches(feature_extractor, images):
    """Runs VGG16 in batches so we don't need the whole feature matrix
    computed in one giant call. preprocess_input is applied per-batch
    right before feeding into VGG16."""
    all_features = []
    n = len(images)
    for start in range(0, n, BATCH_SIZE):
        end = min(start + BATCH_SIZE, n)
        batch = images[start:end].copy()
        batch = preprocess_input(batch)  # BGR conversion + mean-centering
        features = feature_extractor.predict(batch, verbose=0)
        all_features.append(features)
        if (start // BATCH_SIZE) % 10 == 0:
            print(f"    ...{end}/{n} images processed")
    return np.concatenate(all_features, axis=0)


def main():
    print("Loading VGG16 feature extractor (ImageNet weights)...")
    feature_extractor = build_feature_extractor()

    print("\nLoading training split...")
    train_images, train_labels_raw = load_npz_split("train_data.npz")
    print(f"  {len(train_images)} training images")

    print("Loading validation split...")
    val_images, val_labels_raw = load_npz_split("val_data.npz")
    print(f"  {len(val_images)} validation images")

    # Reuse the label encoder that came with the dataset if present,
    # so class-index <-> class-name mapping matches whatever was used
    # to build the arrays. Otherwise fit a fresh one.
    provided_encoder_path = os.path.join(NPZ_DIR, "label_encoder.pkl")
    if os.path.exists(provided_encoder_path):
        print("\nUsing provided label_encoder.pkl from the dataset folder.")
        label_encoder = joblib.load(provided_encoder_path)
    else:
        print("\nNo label_encoder.pkl found in dataset folder, fitting a new one.")
        label_encoder = LabelEncoder()
        label_encoder.fit(train_labels_raw)

    y_train = label_encoder.transform(train_labels_raw)
    y_val = label_encoder.transform(val_labels_raw)

    print("\nExtracting VGG16 features for training set...")
    X_train = extract_features_in_batches(feature_extractor, train_images)

    print("\nExtracting VGG16 features for validation set...")
    X_val = extract_features_in_batches(feature_extractor, val_images)

    print(f"\nFeature shapes -> train: {X_train.shape}, val: {X_val.shape}")

    print("\nTraining SVM (RBF kernel)...")
    svm = SVC(kernel="rbf", C=10, gamma="scale", probability=True, random_state=42)
    svm.fit(X_train, y_train)

    y_pred = svm.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    print(f"\nValidation accuracy: {acc * 100:.2f}%")
    print(classification_report(y_val, y_pred, target_names=label_encoder.classes_))

    joblib.dump(svm, SVM_MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    print(f"\nSaved trained SVM to: {SVM_MODEL_PATH}")
    print(f"Saved label encoder to: {LABEL_ENCODER_PATH}")


if __name__ == "__main__":
    main()
