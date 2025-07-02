import os
import requests
import easyocr
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
                                                    
# Flask setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
app.secret_key = 'supersecretkey'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Sightengine credentials
API_USER = 'your_user'
API_SECRET = 'your_secret'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load and train text classifier
def train_model(dataset_path):
    data = pd.read_csv(dataset_path)
    data['cyberbullying_label'] = data['cyberbullying_type'].apply(lambda x: 0 if x == 'not_cyberbullying' else 1)
    cyberbullying = data[data['cyberbullying_label'] == 1]
    non_cyberbullying = data[data['cyberbullying_label'] == 0]
    cyberbullying_downsampled = resample(cyberbullying, replace=False, n_samples=len(non_cyberbullying), random_state=42)
    balanced_data = pd.concat([cyberbullying_downsampled, non_cyberbullying])
    texts = balanced_data['tweet_text']
    labels = balanced_data['cyberbullying_label']
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X = vectorizer.fit_transform(texts)
    X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)
    model = MultinomialNB()
    model.fit(X_train, y_train)
    return model, vectorizer

model, vectorizer = train_model("cyberbullying_tweets.csv")

def extract_text(image_path):
    reader = easyocr.Reader(['en'], gpu=False)
    result = reader.readtext(image_path, detail=0)
    return " ".join(result).strip()

def is_offensive_text(text, model, vectorizer):
    X_test = vectorizer.transform([text])
    prediction = model.predict(X_test)
    return prediction[0] == 1

def check_image_with_sightengine(image_path):
    url = "https://api.sightengine.com/1.0/check.json"
    payload = {
        'models': 'nudity,wad,offensive,gore',
        'api_user': API_USER,
        'api_secret': API_SECRET
    }
    with open(image_path, 'rb') as image_file:
        files = {'media': image_file}
        response = requests.post(url, data=payload, files=files)
    return response.json()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            extracted_text = extract_text(filepath)
            if extracted_text:
                if is_offensive_text(extracted_text, model, vectorizer):
                    os.remove(filepath)
                    flash('Offensive text detected in image. Upload rejected.', 'danger')
                    return redirect(request.url)
                else:
                    flash('Image accepted (based on text check)', 'success')
                    return render_template('index.html', uploaded=True, image_url=filepath, result="Clean (Text)")
            else:
                result = check_image_with_sightengine(filepath)
                reasons = []

                if result.get('nudity', {}).get('raw', 0) > 0.7:
                    reasons.append("Nudity")
                if result.get('weapon', 0) > 0.5:
                    reasons.append("Weapon")
                if result.get('drugs', 0) > 0.5:
                    reasons.append("Drugs")
                if result.get('gore', {}).get('prob', 0) > 0.5:
                    reasons.append("Gore")

                if reasons:
                    os.remove(filepath)
                    flash(f"Offensive content detected (Image check): {', '.join(reasons)}", 'danger')
                    return redirect(request.url)
                else:
                    flash('Image accepted (based on image check)', 'success')
                    return render_template('index.html', uploaded=True, image_url=filepath, result="Clean (Image)")
    
    return render_template('index.html', uploaded=False)
    
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  
    app.run(host='0.0.0.0', port=port, debug=False)



