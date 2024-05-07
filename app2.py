import streamlit as st
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import random
import json

# Function to analyze image using Sentisight AI API
def analyze_image(image):
    token = "your_token"  # Consider using environment variables for sensitive information
    project_id = "your_model_id"
    model = "your_model_name"
    headers = {"X-Auth-token": token, "Content-Type": "application/octet-stream"}
    
    # Make POST request to Sentisight API
    r = requests.post(f'https://platform.sentisight.ai/api/predict/{project_id}/{model}/', headers=headers, data=image)
    
    # Check response
    if r.status_code == 200:
        return r.json()
    else:
        return {"error": f"Error occurred with REST API. Status code: {r.status_code}, Error message: {r.text}"}

# Function to draw bounding boxes and labels on the image
def draw_boxes_on_image(image_bytes, boxes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        draw = ImageDraw.Draw(img)

        # Load a font
        font_size = max(10, int(img.size[1] / 35)) #Adjust font size
        font = ImageFont.load_default(font_size)

        # Assign random color to each class label
        class_colors = {}
        for box in boxes:
            class_name = box['label']
            if class_name not in class_colors:
                class_colors[class_name] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        for box in boxes:
            left = box['x0']
            top = box['y0']
            right = box['x1']
            bottom = box['y1']
            class_name = box['label']
            score = box['score']
            color = class_colors[class_name]
            draw.rectangle([left, top, right, bottom], outline=color, width=max(12, int(img.size[1] / 40)))
            
            # Get text size to determine the size of the background box
            text = f"{class_name}: {score:.2f}"

            # Draw background box
            #draw.rectangle([left + 5, top - 50, right, bottom - 50], fill="black")


            # Draw text
            draw.text((left+10, top), text, fill=(255, 255, 255), font=font)  # White color for text

        return img
    except Exception as e:
        st.error(f'Error opening image: {e}')
        return None

# Main Streamlit app
def main():
    st.title("Sentisight AI Image Analyzer")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        
        # Analyze image on button click
        if st.button("Analyze"):
            # Read the uploaded file as bytes
            image_bytes = uploaded_file.read()
            # Analyze image using Sentisight API
            result = analyze_image(image_bytes)
            #st.write(result)  # Display result
            
            # Display result or error
            if 'error' in result:
                st.error(result['error'])
            elif not result:
                st.warning("No predictions found in the result.")
            else:
                # Draw bounding boxes and labels on the image
                annotated_image = draw_boxes_on_image(image_bytes, result)
                if annotated_image is not None:
                    st.image(annotated_image, caption="Analyzed Image", use_column_width=True)
    
if __name__ == "__main__":
    main()
