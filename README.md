# AgroLens:Tomato Disease Detection

Mobile app that detects tomato leaf disease (Early Blight, Late Blight,
Leaf Mold, or Healthy) using VGG16 for feature extraction and
SVM for classification.

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

