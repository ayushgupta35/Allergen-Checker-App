import nltk
from textblob import TextBlob
import re
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import cv2
import pytesseract
from pytesseract import Output
import base64
from io import BytesIO
from PIL import Image
import xml.etree.ElementTree as ET

# Initialize Flask application
app = Flask(__name__)

# Configuration for directories to store uploaded and processed images
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['PROCESSED_FOLDER'] = './processed'

# Ensure the necessary directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

# Allergen file path
ALLERGEN_FILE = 'allergens.xml'

def load_allergens():
    """
    Load the list of allergens from an XML file.
    
    :return: List of allergens loaded from the XML file.
    """
    tree = ET.parse(ALLERGEN_FILE)
    root = tree.getroot()
    return [allergen.text for allergen in root.findall('allergen')]

def save_allergen(new_allergen):
    """
    Add a new allergen to the XML file.
    
    :param new_allergen: The allergen to be added to the XML file.
    """
    tree = ET.parse(ALLERGEN_FILE)
    root = tree.getroot()
    allergen_element = ET.SubElement(root, 'allergen')
    allergen_element.text = new_allergen.lower()
    tree.write(ALLERGEN_FILE)

def remove_allergen(allergen_to_remove):
    """
    Remove an allergen from the XML file.
    
    :param allergen_to_remove: The allergen to be removed from the XML file.
    """
    tree = ET.parse(ALLERGEN_FILE)
    root = tree.getroot()
    for allergen in root.findall('allergen'):
        if allergen.text == allergen_to_remove.lower():
            root.remove(allergen)
            tree.write(ALLERGEN_FILE)
            break

# Load initial list of allergens
allergens = load_allergens()

@app.route('/')
def index():
    """
    Render the index page with options to upload an image or use the camera.
    
    :return: Rendered HTML page for the index.
    """
    return render_template('index.html')

@app.route('/manage_allergens', methods=['GET', 'POST'])
def manage_allergens():
    """
    Handle the management of allergens, allowing users to add or remove allergens.
    
    :return: Rendered HTML page for managing allergens.
    """
    message = ''
    if request.method == 'POST':
        action = request.form.get('action')
        allergen = request.form.get('allergen').strip().lower()

        # Handle addition of new allergen
        if action == 'add':
            allergens = load_allergens()
            if allergen in allergens:
                message = f'Allergen "{allergen}" already exists!'
            else:
                save_allergen(allergen)
                message = f'Allergen "{allergen}" added successfully.'
        # Handle removal of existing allergen
        elif action == 'remove':
            remove_allergen(allergen)
            message = f'Allergen "{allergen}" removed successfully.'

        return redirect(url_for('manage_allergens'))

    allergens = load_allergens()
    return render_template('manage_allergens.html', allergens=allergens, message=message)

@app.route('/upload', methods=['GET'])
def upload_page():
    """
    Render the image upload page.
    
    :return: Rendered HTML page for uploading images.
    """
    return render_template('upload.html')

@app.route('/capture', methods=['GET'])
def capture_page():
    """
    Render the camera capture page for capturing an image.
    
    :return: Rendered HTML page for camera capture.
    """
    return render_template('capture.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    """
    Handle the image file upload, save the file, and redirect to the processing page.
    
    :return: Redirect to the image processing page or upload page if upload fails.
    """
    if 'file' not in request.files:
        return redirect(url_for('upload_page'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('upload_page'))

    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('process_upload', filename=file.filename))

@app.route('/process_upload/<filename>')
def process_upload(filename):
    """
    Process an uploaded image file and display the results.
    
    :param filename: Name of the uploaded image file.
    :return: Rendered HTML page showing the processed image and extracted information.
    """
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    processed_filepath, extracted_text, found_allergens = process_image(filepath)
    return render_template('results.html', filename=os.path.basename(processed_filepath), image_text=extracted_text, found_allergens=found_allergens)

@app.route('/process_capture', methods=['POST'])
def process_capture():
    """
    Process an image captured using the camera and display the results.
    
    :return: Rendered HTML page showing the processed image and extracted information.
    """
    image_data = request.form['image_data']
    image_data = image_data.split(",")[1]
    image_data = base64.b64decode(image_data)
    image = Image.open(BytesIO(image_data))
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'captured_image.png')
    image.save(filepath)

    processed_filepath, extracted_text, found_allergens = process_image(filepath)
    return render_template('results.html', filename=os.path.basename(processed_filepath), image_text=extracted_text, found_allergens=found_allergens)

@app.route('/processed/<filename>')
def serve_processed_image(filename):
    """
    Serve the processed image from the processed directory.
    
    :param filename: Name of the processed image file.
    :return: Processed image file served from the directory.
    """
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

# Download the nltk corpus for word validation
nltk.download('words')

def is_valid_word(word):
    """
    Check if a given word exists in the NLTK words corpus.
    
    :param word: The word to validate.
    :return: Boolean indicating if the word is valid.
    """
    words = set(nltk.corpus.words.words())
    return word in words

def normalize_text(text):
    """
    Normalize the extracted text, correct spelling, and clean up unnecessary symbols.
    
    :param text: The text extracted from the image.
    :return: Normalized and cleaned text.
    """
    # Remove unwanted symbols
    text = re.sub(r'[+@—_]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[.,]+', '.', text).strip()

    # Spell check and correct the text
    corrected_text = []
    blob = TextBlob(text)
    for word in blob.words:
        corrected_word = str(TextBlob(word).correct())
        if is_valid_word(corrected_word.lower()):
            corrected_text.append(corrected_word)
        else:
            corrected_text.append(word)

    # Return cleaned text
    cleaned_text = ' '.join(corrected_text)
    return cleaned_text

def process_image(filepath):
    """
    Process the image for text extraction, allergen detection, and visual highlighting.
    
    :param filepath: The path to the image file to be processed.
    :return: Tuple containing the processed file path, extracted text, and list of detected allergens.
    """
    # Read the image using OpenCV
    image = cv2.imread(filepath)
    
    # Extract text from the image using Tesseract OCR (forced to English)
    extracted_text = pytesseract.image_to_string(image, lang='eng').lower()
    
    # Normalize the extracted text
    extracted_text = normalize_text(extracted_text)

    # Find allergens within the extracted text
    found_allergens = set()
    for allergen in allergens:
        if allergen in extracted_text:
            found_allergens.add(allergen)

    # Highlight detected allergens within the image
    d = pytesseract.image_to_data(image, lang='eng', output_type=Output.DICT)
    n_boxes = len(d['text'])

    for i in range(n_boxes):
        word = d['text'][i].strip().lower()
        for allergen in found_allergens:
            if allergen in word and int(d['conf'][i]) > 40:
                (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Save the processed image with allergen highlights
    processed_filename = os.path.basename(filepath)
    processed_filepath = os.path.join(app.config['PROCESSED_FOLDER'], processed_filename)
    cv2.imwrite(processed_filepath, image)

    # Return the processed file path, extracted text, and detected allergens
    return processed_filepath, extracted_text.strip(), list(found_allergens)

# Run the Flask application in debug mode
if __name__ == '__main__':
    app.run(debug=True)