from flask import Flask, request, jsonify
import joblib, re, json

app = Flask(__name__)

# Load your trained model and vectorizer
try: 
    model = joblib.load("model.joblib")
    vectorizer = joblib.load("vectorizer.joblib")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading the model: {e}")

# Clean text data
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]','',text)  #remove non-alphabetical characters
    return text

# Optionally, perform a quick test prediction to verify
test_review = "This is the best review in the world."
test_review_clean = clean_text(test_review)
test_review_vector = vectorizer.transform([test_review_clean])
test_prediction = model.predict(test_review_vector)
print(f"Test prediction: {test_prediction}")

@app.route('/health')
def health_check():
    return 'Service is up', 200

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    review = data['text']
    review_clean = clean_text(review)
    review_vector = vectorizer.transform([review_clean])
    
    # Sentiment
    prediction = model.predict(review_vector)[0].argmax()

    if prediction==0:
        result = {"sentiment": "negative", "review": review}
    elif prediction==1:
        result = {"sentiment": "positive", "review": review}
    else:
        result = {"sentiment": "neutral", "review": review}
    return jsonify(result)

@app.route("/predictjson", methods=["POST"])
def predict_json():
    # Check if 'json' part is present in the request
    #if 'json' not in request.files:
    #    return jsonify({"error":"Missing JSON file"}), 400
    data = request.get_json(force=True)
    reviews = data.get("reviews",[])
    results = []

    for review_data in reviews:
        review = review_data.get("text", "")
        review_clean = clean_text(review)
        review_vector = vectorizer.transform([review_clean])
        
        # Sentiment
        prediction = model.predict(review_vector)[0].argmax()

        if prediction==0:
            result = {"sentiment": "negative", "review": review}
        elif prediction==1:
            result = {"sentiment": "positive", "review": review}
        else:
            result = {"sentiment": "neutral", "review": review}

        results.append(result)
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
