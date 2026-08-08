# AgroLens — Tomato Disease Detection

Mobile app that detects tomato leaf disease (Early Blight, Late Blight,
Leaf Mold, or Healthy) using **VGG16** for feature extraction and
**SVM** for classification, matching your project proposal.

```
AgroLens/
├── backend/                 Python/Flask API + ML pipeline
│   ├── app.py                Main server: login, signup, scan, history
│   ├── database.py           SQLite (users + scan history)
│   ├── models/
│   │   ├── vgg16_svm.py       VGG16 feature extractor + SVM prediction
│   │   └── train_model.py     Script to train the SVM on your dataset
│   ├── utils/
│   │   └── preprocessing.py   Shared image preprocessing (train + predict)
│   ├── dataset/               Put training images here (see below)
│   ├── uploads/                Uploaded leaf photos get saved here
│   └── requirements.txt
│
└── mobile/                  React Native (Expo) app
    ├── App.js                Navigation setup
    ├── screens/
    │   ├── LoginScreen.js
    │   ├── SignupScreen.js
    │   ├── HomeScreen.js
    │   ├── ScanScreen.js       Camera + Upload
    │   ├── ResultScreen.js     Diagnosis + confidence + recommendation
    │   └── HistoryScreen.js
    └── services/
        ├── api.js              All backend calls (login/scan/history)
        └── config.js           Set your backend IP here
```

## 1. Backend setup (VS Code, Terminal 1)

```bash
cd AgroLens/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 1a. Add your dataset

Put leaf images into these folders (from your proposal, PlantVillage
dataset, ~500 images per class):

```
backend/dataset/Healthy/*.jpg
backend/dataset/Early_Blight/*.jpg
backend/dataset/Late_Blight/*.jpg
backend/dataset/Leaf_Mold/*.jpg
```

### 1b. Train the SVM on VGG16 features

```bash
python models/train_model.py
```

This extracts a 512-d VGG16 feature vector per image, trains an SVM,
prints accuracy/precision/recall, and saves:
- `models/svm_classifier.pkl`
- `models/label_encoder.pkl`

Re-run this any time you add more training images.

### 1c. Start the API server

```bash
python app.py
```

Server runs at `http://0.0.0.0:5000`. Test it:

```bash
curl http://localhost:5000/api/health
```

## 2. Mobile app setup (VS Code, Terminal 2)

```bash
cd AgroLens/mobile
npm install
```

### 2a. Point the app at your backend

Find your computer's LAN IP (phone and laptop must be on the same WiFi):
- Windows: `ipconfig` → IPv4 Address
- Mac: `ipconfig getifaddr en0`
- Linux: `hostname -I`

Edit `mobile/services/config.js`:

```js
export const API_BASE_URL = "http://YOUR_LAN_IP:5000";
```

### 2b. Run the app

```bash
npx expo start
```

Scan the QR code with the **Expo Go** app on your phone (Android/iOS),
or press `a` for an Android emulator / `i` for an iOS simulator.

## 3. How the ML pipeline works

1. **Upload/Scan** — user takes or picks a leaf photo (`ScanScreen.js`)
2. **Preprocess** — resize to 224×224, VGG16-style normalization (`utils/preprocessing.py`)
3. **VGG16 feature extraction** — `include_top=False, pooling='avg'` turns the image into a 512-d feature vector (`models/vgg16_svm.py`)
4. **SVM classification** — RBF-kernel SVM predicts one of 4 classes + confidence (`models/train_model.py` trains it, `models/vgg16_svm.py` runs it)
5. **Result** — class, confidence, per-class probabilities, and a treatment recommendation are returned to the app and shown on `ResultScreen.js`

## 4. API reference

| Method | Endpoint              | Auth | Purpose                       |
|--------|------------------------|------|--------------------------------|
| POST   | `/api/auth/register`   | No   | Create account                 |
| POST   | `/api/auth/login`      | No   | Log in, returns JWT            |
| POST   | `/api/scan`            | Yes  | Upload image, get diagnosis    |
| GET    | `/api/history`         | Yes  | List past scans                |
| GET    | `/api/health`          | No   | Server/model status check      |

Auth uses `Authorization: Bearer <token>` header, issued at login/signup.

## 5. Notes for your report

- Dataset split: 80% train / 20% test (`train_test_split`, stratified) in `train_model.py`.
- Evaluation metrics (precision, recall, F1, accuracy) print automatically after training, matching proposal section 3.3.5.
- SQLite is used for simplicity during development; swap `database.py` for Firebase/Postgres later without touching `app.py`'s route logic much.
