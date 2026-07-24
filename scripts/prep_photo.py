import cv2
import numpy as np
from PIL import Image
from rembg import remove, new_session
import os

def prep_photo():
    input_path = 'source-photo.jpg'
    output_path = 'source-prepped.png'

    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found in root directory!")
        return

    print("Stripping background with lightweight u2netp model...")
    session = new_session("u2netp")
    
    with open(input_path, 'rb') as i:
        input_data = i.read()
        output_data = remove(input_data, session=session)
        
    with open('source-no-bg.png', 'wb') as o:
        o.write(output_data)

    # Open with PIL for cropping
    img_pil = Image.open('source-no-bg.png').convert('RGBA')
    w, h = img_pil.size
    min_dim = min(w, h)
    
    # Center crop
    left = (w - min_dim) // 2
    top = (h - min_dim) // 2
    right = left + min_dim
    bottom = top + min_dim
    
    cropped = img_pil.crop((left, top, right, bottom))
    resized = cropped.resize((460, 460), Image.Resampling.LANCZOS)
    
    # Convert background transparent pixels to black before CLAHE
    background = Image.new('RGBA', resized.size, (0, 0, 0, 255))
    alpha_composite = Image.alpha_composite(background, resized).convert('L')
    
    # Convert to OpenCV image for CLAHE
    gray = np.array(alpha_composite)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    cv2.imwrite(output_path, enhanced)
    if os.path.exists('source-no-bg.png'):
        os.remove('source-no-bg.png')
    print("source-prepped.png successfully generated with background removal & CLAHE.")

if __name__ == "__main__":
    prep_photo()