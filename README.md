
# AllergyGuard App

## Overview

**AllergyGuard** is a web application designed to help users detect allergens in food products by analyzing images of ingredient labels. Users can upload images or capture them directly using their device's camera. The app then processes the image, extracts the text, and highlights any detected allergens. The list of allergens can be managed dynamically, allowing users to add or remove allergens as needed.

This project was built using Python's Flask framework for the backend, and OpenCV, PyTesseract, and NLTK for image processing and text extraction.

## Features

- **Upload Image**: Users can upload an image of an ingredient label for allergen detection.
- **Capture Image**: Users can capture an image using their camera, which will be processed for allergens.
- **Allergen Detection**: The app highlights allergens found in the text extracted from the uploaded or captured image.
- **Manage Allergens**: Users can add new allergens or remove existing ones from the allergen list.
- **Processed Image**: The app displays the processed image with allergens highlighted, and it also shows the extracted text.

## Technologies Used

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: OpenCV, PyTesseract (OCR)
- **Natural Language Processing**: NLTK, TextBlob
- **File Handling**: Base64, XML

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package installer)

### Libraries/Modules

You need to install the following Python libraries:

```bash
pip install flask opencv-python pytesseract textblob nltk pillow
```

You also need to download NLTK's word corpus:

```bash
python -m nltk.downloader words
```

### Setting up PyTesseract

Make sure you have Tesseract-OCR installed on your machine. You can find the installation instructions for your platform [here](https://github.com/tesseract-ocr/tesseract).

After installation, ensure Tesseract's executable is added to your system's PATH.

### Directory Structure

The directory structure of the project is as follows:

```
AllergyGuard/
│
├── app.py                 # Main Flask application
├── templates/             # HTML templates
│   ├── capture.html
│   ├── index.html
│   ├── manage_allergens.html
│   ├── results.html
│   └── upload.html
│
├── static/                # Static assets (CSS, images)
│   └── style.css
│
├── uploads/               # Directory for uploaded images (auto-created)
├── processed/             # Directory for processed images (auto-created)
├── allergens.xml          # Allergen data stored in XML format
└── README.md              # This README file
```

## Usage

### Running the Application

1. **Clone the repository** and navigate to the project directory:

```bash
git clone https://github.com/yourusername/AllergyGuard.git
cd AllergyGuard
```

2. **Start the Flask server**:

```bash
python app.py
```

3. **Access the application** by opening your web browser and navigating to:

```
http://127.0.0.1:5000/
```

### Features Walkthrough

- **Home Page**: Choose whether to upload an image or capture one using your device’s camera. You can also manage the allergens from here.
  
- **Upload Image**: Allows you to upload an image of a product’s ingredient label for allergen detection.
  
- **Capture Image**: Lets you capture an image via the camera, which is then processed for allergens.
  
- **Manage Allergens**: Enables you to add new allergens to the list or remove existing ones.
  
- **Results Page**: Displays the extracted text from the image and highlights any detected allergens. The processed image with highlighted allergens is also shown.

## Allergen Management

All allergens are stored in an `allergens.xml` file, which is located in the root directory of the project. This XML file is used to persist and manage the list of allergens.

### Adding an Allergen

- Go to the **Manage Allergens** page.
- Enter the new allergen in the input field and click the "Add Allergen" button.

### Removing an Allergen

- On the **Manage Allergens** page, click the "×" button next to the allergen you wish to remove.

## Image Processing

The application uses PyTesseract to extract text from the uploaded or captured images. It then searches for any allergens present in the extracted text, highlighting them in the processed image.

- **Normalization**: Extracted text is normalized to correct spelling and remove unwanted symbols before searching for allergens.
- **Allergen Highlighting**: If any allergens are detected in the text, they are highlighted in the processed image using OpenCV.

## Troubleshooting

1. **Tesseract Not Found**: Ensure that Tesseract is installed on your machine and added to your system's PATH.
2. **Flask App Not Running**: Check if Python and Flask are properly installed. Make sure no other processes are using port 5000.
3. **Camera Not Working**: Ensure that your browser has permission to access your camera.

---

Enjoy using AllergyGuard, and stay safe from allergens!