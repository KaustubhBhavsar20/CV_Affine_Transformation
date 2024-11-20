from flask import Flask, render_template, request, redirect, url_for
import cv2
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = 'static/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Affine Transformations Functions

def translate_image(image, tx, ty):
    rows, cols = image.shape[:2]
    M = np.float32([[1, 0, tx], [0, 1, ty]])  # Translation matrix
    translated = cv2.warpAffine(image, M, (cols, rows))
    return translated

def scale_image(image, fx, fy):
    rows, cols = image.shape[:2]
    M = np.float32([[fx, 0, 0], [0, fy, 0]])  # Scaling matrix
    scaled = cv2.warpAffine(image, M, (cols, rows))
    return scaled

def rotate_image(image, angle):
    rows, cols = image.shape[:2]
    M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)  # Rotation matrix
    rotated = cv2.warpAffine(image, M, (cols, rows))
    return rotated

def shear_image(image, shear_factor):
    rows, cols = image.shape[:2]
    M = np.float32([[1, shear_factor, 0], [0, 1, 0]])  # Shear matrix
    sheared = cv2.warpAffine(image, M, (cols, rows))
    return sheared

# Additional Transformations

def reflect_image(image, axis='horizontal'):
    if axis == 'horizontal':
        reflected = cv2.flip(image, 1)  # Flip horizontally
    elif axis == 'vertical':
        reflected = cv2.flip(image, 0)  # Flip vertically
    return reflected

def perspective_transform(image):
    rows, cols = image.shape[:2]
    pts1 = np.float32([[50, 50], [cols-50, 50], [50, rows-50], [cols-50, rows-50]])  # Points before transformation
    pts2 = np.float32([[10, 100], [cols-10, 100], [100, rows-10], [cols-100, rows-10]])  # Points after transformation
    M = cv2.getPerspectiveTransform(pts1, pts2)
    perspective = cv2.warpPerspective(image, M, (cols, rows))
    return perspective

def affine_rotate_with_center(image, angle, center=(0, 0)):
    rows, cols = image.shape[:2]
    if center == (0, 0):
        center = (cols / 2, rows / 2)
    M = cv2.getRotationMatrix2D(center, angle, 1)  # Rotation matrix with arbitrary center
    rotated = cv2.warpAffine(image, M, (cols, rows))
    return rotated

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
            file.save(filename)

            # Read the uploaded image
            image = cv2.imread(filename)

            # Apply all transformations
            translated_image = translate_image(image, 50, 50)
            scaled_image = scale_image(image, 1.2, 1.2)
            rotated_image = rotate_image(image, 45)
            sheared_image = shear_image(image, 0.5)
            reflected_image = reflect_image(image, 'horizontal')  # You can also try 'vertical'
            perspective_image = perspective_transform(image)
            affine_rotated_image = affine_rotate_with_center(image, 45, center=(100, 100))

            # Save transformed images
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'translated_image.jpg'), translated_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'scaled_image.jpg'), scaled_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_image.jpg'), rotated_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'sheared_image.jpg'), sheared_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'reflected_image.jpg'), reflected_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'perspective_image.jpg'), perspective_image)
            cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'], 'affine_rotated_image.jpg'), affine_rotated_image)

            return render_template('index.html', filename='uploaded_image.jpg', 
                                   translated='translated_image.jpg', 
                                   scaled='scaled_image.jpg', 
                                   rotated='rotated_image.jpg', 
                                   sheared='sheared_image.jpg',
                                   reflected='reflected_image.jpg',
                                   perspective='perspective_image.jpg',
                                   affine_rotated='affine_rotated_image.jpg')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
