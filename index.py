import cv2
from pyzbar import pyzbar
import numpy as np
import webbrowser
from tkinter import Tk, Button, Label, filedialog, Frame, messagebox
from PIL import Image, ImageTk

def preprocess_frame(frame):
    """Preprocess the frame to enhance barcode detection."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Apply Gaussian Blur to reduce noise
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)  # Simple binary threshold
    return thresh

def detect_and_decode(frame):
    """Detect and decode barcodes from the given frame."""
    barcodes = pyzbar.decode(frame)
    detected_barcodes = []

    for barcode in barcodes:
        barcode_data = barcode.data.decode("utf-8")
        (x, y, w, h) = barcode.rect
        
        # Draw a rectangle around the barcode
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Store the detected barcode data
        detected_barcodes.append(barcode_data)

    return detected_barcodes if detected_barcodes else None

def video_capture_mode():
    """Handle barcode detection using the webcam (video capture mode)."""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def capture_and_detect():
        ret, frame = cap.read()
        if not ret:
            label_status['text'] = "Error accessing webcam."
            return

        processed_frame = preprocess_frame(frame)
        decoded_data = detect_and_decode(processed_frame)

        # Show the processed frame with detected barcodes
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img_tk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = img_tk
        video_label.configure(image=img_tk)

        if decoded_data:
            label_status['text'] = f"Decoded: {', '.join(decoded_data)}"
            for data in decoded_data:
                if data.startswith("http"):
                    webbrowser.open(data)
        else:
            label_status['text'] = "No barcode detected."

        video_label.after(10, capture_and_detect)

    capture_and_detect()

def process_image(image_path):
    """Detect and decode barcode from a given image file."""
    image = cv2.imread(image_path)
    if image is None:
        messagebox.showerror("Error", f"Could not open image {image_path}")
        return

    label_status['text'] = f"Processing image: {image_path}"
    
    # Preprocess the image and decode the barcode
    processed_image = preprocess_frame(image)
    decoded_data = detect_and_decode(processed_image)

    if decoded_data:
        label_status['text'] = f"Decoded from Image: {', '.join(decoded_data)}"
        for data in decoded_data:
            if data.startswith("http"):
                webbrowser.open(data)
    else:
        label_status['text'] = "No barcode detected in the image."

    # Display the image with bounding boxes around barcodes
    img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    img_tk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = img_tk
    video_label.configure(image=img_tk)

def browse_file():
    """Open file dialog to select an image file."""
    image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if image_path:
        process_image(image_path)

# Create GUI with Tkinter
root = Tk()
root.title("Barcode Scanner")
root.geometry("900x700")
root.configure(bg="#f0f0f0")

# Create a main frame
main_frame = Frame(root, bg="#f0f0f0")
main_frame.pack(pady=20)

# Title Label
label_title = Label(main_frame, text="Barcode Scanner", font=("Arial", 24, "bold"), bg="#f0f0f0")
label_title.pack(pady=10)

# Status Label
label_status = Label(main_frame, text="Select an option to start barcode scanning.", font=("Arial", 14), fg="green", bg="#f0f0f0")
label_status.pack(pady=20)

# Video/image display area
video_label = Label(main_frame, bg="#f0f0f0")
video_label.pack(pady=10)

# Buttons for webcam mode or image upload
button_frame = Frame(main_frame, bg="#f0f0f0")
button_frame.pack(pady=20)

btn_webcam = Button(button_frame, text="Scan via Webcam", command=video_capture_mode, font=("Arial", 14), width=20, height=2, bg="#4CAF50", fg="white")
btn_webcam.grid(row=0, column=0, padx=10)

btn_browse = Button(button_frame, text="Browse Image", command=browse_file, font=("Arial", 14), width=20, height=2, bg="#2196F3", fg="white")
btn_browse.grid(row=0, column=1, padx=10)

# Quit button
btn_quit = Button(root, text="Quit", command=root.quit, font=("Arial", 12), width=10, bg="#f44336", fg="white")
btn_quit.pack(pady=20)

root.mainloop()