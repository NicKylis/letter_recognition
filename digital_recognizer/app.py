import base64
from io import BytesIO
from PIL import Image
import numpy as np
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import cv2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load your trained model
model = load_model('9956.keras')

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the JSON data from the request
        data = request.get_json()
        image_data = data['image']

        # Convert the base64 string to image
        img_str = image_data.split(',')[1]  # Strip the metadata part
        img_data = base64.b64decode(img_str)

        # Use PIL to open the image and convert to grayscale
        img = Image.open(BytesIO(img_data)).convert("L")
        img = img.resize((28, 28))  # Resize to 28x28 for MNIST model

        # Convert to NumPy array and apply OpenCV threshold
        img_array = np.array(img)
        _, img_array = cv2.threshold(img_array, 127, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Normalize and reshape image to match model input
        img_array = img_array / 255.0
        img_array = img_array.reshape(1, 28, 28, 1)

        # Predict using the model
        prediction = model.predict(img_array)
        predicted_class = int(np.argmax(prediction))

        # Return prediction as JSON
        return jsonify({'prediction': predicted_class})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
