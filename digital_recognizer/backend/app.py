import base64
from io import BytesIO
from PIL import Image
import numpy as np
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import cv2
from flask_cors import CORS
from flask_cors import cross_origin

app = Flask(__name__)

# Explicitly configure CORS
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Load model inside function to prevent startup delays
def load_model_on_demand():
    return load_model('9956.keras')

# Handle preflight OPTIONS request
@app.route('/predict', methods=['OPTIONS'])
def handle_options():
    response = jsonify({'message': 'CORS preflight OK'})
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    try:
        data = request.get_json()
        image_data = data['image']

        # Convert base64 to image
        img_str = image_data.split(',')[1]
        img_data = base64.b64decode(img_str)
        img = Image.open(BytesIO(img_data)).convert("L")
        img = img.resize((28, 28))  

        # Convert to NumPy and apply threshold
        img_array = np.array(img)
        _, img_array = cv2.threshold(img_array, 127, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Normalize and reshape
        img_array = img_array / 255.0
        img_array = img_array.reshape(1, 28, 28, 1)

        # Load model inside function
        model = load_model_on_demand()
        prediction = model.predict(img_array)
        predicted_class = int(np.argmax(prediction))

        return jsonify({'prediction': predicted_class})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

# Ensure CORS headers are always set
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response

if __name__ == '__main__':
    app.run(debug=True)
