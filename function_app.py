import logging
import cv2
import numpy as np
import requests
import azure.functions as func

def detect_faces(image_bytes):
    # Load the Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    if face_cascade.empty():
        return "Haar cascade classifier could not be loaded."

    # Convert the image bytes into a NumPy array
    image_array = np.frombuffer(image_bytes, np.uint8)

    # Decode the image bytes into an OpenCV image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if image is None:
        return "Invalid image content or format."

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Return True if faces are detected, False otherwise
    return len(faces) > 0

app = func.FunctionApp()

@app.route(route="facedetection",auth_level=func.AuthLevel.ANONYMOUS)
def facedetection(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing HTTP request for face detection.")

    try:
        # Check if the request is GET and serve HTML
        if req.method == 'GET':
            html_form = """
                <html>
                    <head>
                        <style>
                            body {
                                font-family: Arial, sans-serif;
                                padding: 20px;
                                background-color:rgb(12, 245, 117);
                            }
                            .bottom-right {
                                position: absolute;
                                bottom: 10px;
                                right: 20px;
                                font-size: 18px;
                            }
                            .logo {
                                width: 100px;
                                height: 100px;
                            }
                            .header {
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            }
                            .content {
                                margin-top: 50px;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <img src="https://singularium.in/wp-content/uploads/2023/04/company_logo-150x150.png" alt="Logo" class="logo">
                            <div class="bottom-right">By: Anjani Kumar</div>
                        </div>
                        <h2>Face Detection System</h2>
                        <p>To test face detection, please open any image in a web browser, right-click, and copy the image address. Then, paste it below.</p>
                        <pre>https://t4.ftcdn.net/jpg/06/40/07/03/360_F_640070383_9LJ3eTRSvOiwKyrmBYgcjhSlckDnNcxl.jpg</pre>
                        <form method="POST" action="/api/facedetection">
                            <label for="image_url">Image URL:</label><br>
                            <input type="text" id="image_url" name="image_url" placeholder="Enter image URL here"><br><br>
                            <input type="submit" value="Submit">
                        </form>
                    </body>
                </html>
            """
            return func.HttpResponse(html_form, status_code=200, mimetype="text/html")

        # Process form submission
        if req.method == 'POST':
            image_url = req.form.get('image_url')
            if not image_url:
                return func.HttpResponse(
                    "Please provide an image URL.",
                    status_code=400
                )

            # Fetch the image from the provided URL
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return func.HttpResponse(
                    f"Unable to fetch the image from the provided URL: {image_url}",
                    status_code=400
                )

            # Detect faces in the fetched image
            contains_faces = detect_faces(response.content)

            # Return the result as HTML
            result = "Yes" if contains_faces else "No"
            result_html = f"""
                <html>
                    <head>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                padding: 20px;
                                background-color:rgb(12, 245, 117);
                            }}
                            .bottom-right {{
                                position: absolute;
                                bottom: 10px;
                                right: 20px;
                                font-size: 18px;
                            }}
                            .logo {{
                                width: 100px;
                                height: 100px;
                            }}
                            .header {{
                                display: flex;
                                align-items: center;
                                justify-content: center;
                            }}
                            .content {{
                                margin-top: 50px;
                            }}
                            .highlight {{
                                color: #000000;
                                font-weight: bold;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="header">
                            <img src="https://singularium.in/wp-content/uploads/2023/04/company_logo-150x150.png" alt="Logo" class="logo">
                            <div class="bottom-right"> By: Anjani Kumar</div>
                        </div>
                        <h2>Face Detection System: Result</h2>
                        <p>Image URL: {image_url}</p>
                        <p><span class="highlight">Contains Faces: {result}</span></p>
                        <a href="/api/facedetection">Try another image</a>
                    </body>
                </html>
            """
            return func.HttpResponse(result_html, status_code=200, mimetype="text/html")

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )