import cv2
import streamlit as st
import numpy as np
from PIL import Image
from io import BytesIO
import tempfile
import time
from moviepy.editor import TextClip, concatenate_videoclips

ASCII_CHARS = r"$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrift/|01{}[]?-+~<>i!lI;:,\"^`*. "

def pixel_2_ascii(image):
    num_cols = 140
    height, width = image.shape
    cell_width = width/num_cols
    cell_height = cell_width*2
    num_rows = int(height/cell_height)
    str = ""
    for i in range(num_rows):
        for j in range(num_cols):
            sub_image = image[int(i*cell_height):int((i+1)*cell_height),int(j*cell_width):int((j+1)*cell_width)]
            index = int(np.mean(sub_image) / 255 * (len(ASCII_CHARS) - 1))
            str += ASCII_CHARS[index]
        str += "\n"
    return str

def image_2_ascii(image):
    try:
        image = np.array(image.convert('L')) 
    except AttributeError:
        st.error("Error processing the image. Please upload a valid image file.")
        return ""
    return pixel_2_ascii(image)
    
def video_2_ascii(video_path):
    cam = cv2.VideoCapture(video_path)
    if not cam.isOpened():
        st.error("Video not found")
        return None

    fps = int(cam.get(cv2.CAP_PROP_FPS))
    width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ascii_clips = []

    frame_placeholder = st.empty()
    temp_output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (800, 600)) 

    while cam.isOpened():
        ret, frame = cam.read()
        if not ret:
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ascii_art = pixel_2_ascii(gray_frame)
        frame_placeholder.text(ascii_art)

        ascii_image = np.zeros((600, 800, 3), dtype=np.uint8)  
        y0, dy = 15, 15 
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.4
        color = (255, 255, 255)  
        for i, line in enumerate(ascii_art.splitlines()):
            y = y0 + i * dy
            cv2.putText(ascii_image, line, (5, y), font, font_scale, color, 1, cv2.LINE_AA)
        out.write(ascii_image)

    cam.release()
    out.release()

    return temp_output_path

    
def main():
    st.title("₊✩‧₊|Image vs Video to ASCII Art|₊✩‧₊")
    st.subheader('--(˶˃ ᵕ ˂˶)--|Choose type of art to convert|--(˶˃ ᵕ ˂˶)--')

    option = st.radio(
        'Choose type:',
        ('Image', 'Video')
    )

    if option == 'Image':
        image_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        if image_file is not None:
            image = Image.open(image_file)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            st.image(image, caption="Uploaded Image", use_column_width=True)
            ascii_art = image_2_ascii(image)
            if ascii_art:
                st.code(ascii_art, language="text")
                st.download_button("Download ASCII Art", ascii_art, file_name="ascii_image.txt")

    elif option == "Video":
        video_file = st.file_uploader("Upload a video", type=["mp4", "mov", "avi"])
        if video_file is not None:
            video_bytes = video_file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(video_bytes)
                video_path = temp_video.name

            ascii_video_path = video_2_ascii(video_path)
            if ascii_video_path:
                st.success("ASCII Video created successfully!")
                with open(ascii_video_path, "rb") as file:
                    st.download_button(
                        label="Download ASCII Video",
                        data=file,
                        file_name="ascii_video.mp4",
                        mime="video/mp4"
                    )
        
if __name__ == "__main__":
    main()   



    

