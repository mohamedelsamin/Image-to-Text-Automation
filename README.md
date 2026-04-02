# Image to Text Automation (OCR + Desktop Automation)

A Python-based desktop automation system that extracts text from an image using OCR and automatically writes and saves the result into Notepad.

This project combines:
- Computer Vision (OCR)
- Text reconstruction using spatial logic
- Desktop GUI automation
- Window management

---

## Features

- Extracts text from images using EasyOCR
- Reconstructs text lines based on bounding box coordinates
- Automatically opens Notepad
- Simulates human typing
- Saves the output as a `.txt` file
- Prevents overwriting existing files (auto-increment naming)
- Closes unexpected popup windows during execution

---

## How It Works

The system follows this pipeline:

1. Load OCR model
2. Detect and recognize text from image
3. Sort detected words vertically (top → bottom)
4. Group words into lines using Y-distance threshold
5. Sort words horizontally inside each line (left → right)
6. Open Notepad automatically
7. Type extracted text
8. Save as `.txt` file in output directory

---

### Install dependencies:
```
pip install easyocr pyautogui pygetwindow
```
## Technologies Used
EasyOCR (Deep Learning OCR)
PyAutoGUI (Desktop Automation)
PyGetWindow (Window Management)
Python Pathlib (Modern File Handling)
