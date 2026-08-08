"""
preprocessing.py
-----------------
Shared image preprocessing used by BOTH:
  - models/train_model.py   (when building the training feature set)
  - models/vgg16_svm.py     (when predicting on a new uploaded leaf image)

Keeping this identical in both places matters a lot: if training and
prediction preprocess images differently, the SVM will get feature
vectors it was never trained on and accuracy will collapse.

Steps (matches proposal section 3.3.2 "Preprocessing Data"):
  1. Load image, force RGB
  2. Resize to 224x224 (VGG16's expected input size)
  3. Convert to numpy array
  4. Apply Keras' VGG16 preprocess_input (this internally converts
     RGB -> BGR and mean-centers each channel, exactly like the
     proposal describes)
"""

import numpy as np
from PIL import Image
from tensorflow.keras.applications.vgg16 import preprocess_input

IMG_SIZE = (224, 224)


def load_and_preprocess_image(image_path_or_file):
    """
    Accepts either a filesystem path (str) or a file-like object
    (e.g. Flask's request.files['image']) and returns a preprocessed
    numpy array of shape (1, 224, 224, 3), ready for VGG16.
    """
    img = Image.open(image_path_or_file).convert("RGB")
    img = img.resize(IMG_SIZE)

    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)  # (1, 224, 224, 3)
    img_array = preprocess_input(img_array)         # VGG16-specific normalization

    return img_array
