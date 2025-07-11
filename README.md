**Civility Check** is a Flask web app that detects offensive content in images using OCR and the Sightengine API. It scans image text for cyberbullying using a trained ML model and analyzes visual content for nudity, violence, and more.

## 🔍 Features

- 📷 Upload image and check for offensive content
- 🧠 OCR + ML detects harmful text (cyberbullying)
- 🖼️ Sightengine API flags visual threats (nudity, gore, weapons, drugs)
- ❌ Automatically deletes offensive images
- ✅ Accepts and shows clean images

## ⚙️ Tech Stack

- Python, Flask
- EasyOCR (Text extraction)
- Scikit-learn (Naive Bayes + TF-IDF)
- Sightengine API (Image moderation)

## Dataset Link
   https://www.kaggle.com/datasets/andrewmvd/cyberbullying-classification

## 🚀 How to Run

1. Clone this repo:
   
   git clone https://github.com/Rohit-Prakash-27/CivilityCheck.git
   cd civility-check

2. Create Virtual Environment and Install dependencies:

   create a virtual environment
   a. python -m venv venv
   b. venv\Scripts\activate
   pip install -r requirements.txt
   
4. Replace Sightengine API credentials in app.py:

   API_USER = 'your_user'
   API_SECRET = 'your_secret'

5. Run the app:
   
   python app.py

## Steps to Get Sightengine API Credentials

1. Go to the official website:
   https://sightengine.com/

2. Create a free account (if you haven’t):

   Click on "Sign Up"
   Enter your email and password, or use Google login

3. After logging in, you’ll be redirected to the Dashboard

4. In the dashboard:
   You'll see your API User and API Secret

5. Example format:

   API_USER: 1234567890
   API_SECRET: a1b2c3d4e5f6g7h8i9j0

There exists a sample image static/uploads/chill.png for testing...all sucessfull uploads are saved here...
