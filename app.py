from flask import Flask, render_template, request, send_file, make_response, flash, redirect, url_for
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from werkzeug.utils import secure_filename
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def images_to_pdf(img_paths):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)

    x, y = 100, 700
    for img_path in img_paths:
        try:
            img = Image.open(img_path)
        except UnidentifiedImageError as e:
            # Handle the error if the image file cannot be identified
            print(f"Error opening image: {img_path} - {str(e)}")
            continue
        except Exception as e:
            # Handle other possible exceptions
            print(f"Error processing image: {img_path} - {str(e)}")
            continue

        c.drawImage(img_path, x, y, width=400, height=300)
        y -= 350

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return "No image part in the form!"
        
        image_files = request.files.getlist('image')
        if not image_files:
            return "No selected images!"
        
        img_paths = []  # Initialize the list to store valid image file paths
        for image_file in image_files:
            if image_file.filename == '':
                continue

            try:
                img = Image.open(image_file)
            except UnidentifiedImageError as e:
                flash(f"Error processing file {image_file.filename}: {str(e)}", 'error')
                continue
            except Exception as e:
                flash(f"Error processing file {image_file.filename}: {str(e)}", 'error')
                continue
            
            filename = secure_filename(image_file.filename)
            filename = f"{int(time.time())}_{filename}"  # Add timestamp to make filename unique
            
            # Check if the 'static' folder exists, create it if missing
            if not os.path.exists('static'):
                os.makedirs('static')
            
            img_path = os.path.join('static', filename)
            print(f"Saving file to: {img_path}")

            try:
                image_file.save(img_path)
                img_paths.append(img_path)
            except Exception as e:
                flash(f"Error saving file {image_file.filename}: {str(e)}", 'error')
        
        if img_paths:
            pdf_buffer = images_to_pdf(img_paths)

            # Set the Content-Disposition header
            response = make_response(pdf_buffer)
            response.headers['Content-Disposition'] = 'attachment; filename=output.pdf'
            response.headers['Content-Type'] = 'application/pdf'
            
            return response

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
