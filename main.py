import time
import subprocess
from pathlib import Path

import easyocr
import pyautogui
import pygetwindow as gw

# ========= CONFIGURATION =========

# Languages for EasyOCR (e.g. ['en'] for English, ['en', 'ar'] for English + Arabic)
OCR_LANGUAGES = ["en"]

# Folder containing input images
IMAGE_PATH = Path("img.png")

# Folder where you want Notepad to save .txt files
OUTPUT_DIR = Path("output")

# ========= SETUP =========

pyautogui.PAUSE = 0.02
pyautogui.FAILSAFE = True

# EasyOCR reader (lazy init on first use)
_reader = None


def get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)
    return _reader


# ========= OCR FUNCTIONS =========

def ocr_image(image_path: Path) -> str:
    reader = get_reader()
    result = reader.readtext(str(image_path))

    # ترتيب حسب الموقع الرأسي
    result = sorted(result, key=lambda x: x[0][0][1])

    lines = []
    current_line = []
    last_y = None

    y_threshold = 15  # المسافة التي نعتبرها نفس السطر

    for bbox, text, conf in result:
        y = bbox[0][1]

        if last_y is None:
            current_line.append((bbox[0][0], text))
            last_y = y
            continue

        if abs(y - last_y) < y_threshold:
            current_line.append((bbox[0][0], text))
        else:
            current_line = sorted(current_line, key=lambda x: x[0])
            lines.append(" ".join([t[1] for t in current_line]))

            current_line = [(bbox[0][0], text)]

        last_y = y

    # إضافة آخر سطر
    if current_line:
        current_line = sorted(current_line, key=lambda x: x[0])
        lines.append(" ".join([t[1] for t in current_line]))

    return "\n".join(lines)


# ========= WINDOW / NOTEPAD HELPERS =========

def close_unexpected_window(allowed_keywords=("Notepad", "Save As")):
    """Close any active window that isn't Notepad or its Save dialog."""
    try:
        win = gw.getActiveWindow()
    except Exception:
        return

    if not win:
        return

    title = win.title or ""
    if not any(keyword in title for keyword in allowed_keywords):
        pyautogui.hotkey("alt", "f4")
        time.sleep(0.4)


def get_or_launch_notepad():
    windows = [w for w in gw.getWindowsWithTitle("Notepad") if w.visible]

    if not windows:
        subprocess.Popen(["notepad.exe"])

        for _ in range(50):
            time.sleep(0.2)
            windows = [w for w in gw.getWindowsWithTitle("Notepad") if w.visible]
            if windows:
                break

    if not windows:
        raise RuntimeError("Could not find or launch Notepad.")

    win = windows[0]

    try:
        win.activate()
        time.sleep(0.3)
        win.maximize()
    except Exception:
        pass

    return win


def ensure_notepad_foreground(notepad_window):
    """Keep Notepad in focus; close unexpected popups."""
    close_unexpected_window()
    try:
        if not notepad_window.isActive:
            notepad_window.activate()
            time.sleep(0.2)
    except Exception:
        pass


# ========= TYPING & SAVING =========

def human_type(text: str, notepad_window):
    ensure_notepad_foreground(notepad_window)
    pyautogui.write(text, interval=0.01)

def save_notepad_to_file(notepad_window, target_path: Path):
    """Ctrl+S then type full path in Save dialog."""
    ensure_notepad_foreground(notepad_window)
    abs_path = str(target_path.resolve())

    pyautogui.hotkey("ctrl", "s")
    time.sleep(0.7)
    close_unexpected_window()
    time.sleep(0.3)
    pyautogui.typewrite(abs_path)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(1.0)


# ========= MAIN LOGIC =========


def get_unique_path(base_path: Path) -> Path:
    """
    If base_path exists, return a new path with a numeric suffix.
    Example: note.txt -> note_1.txt, note_2.txt, ...
    """
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    parent = base_path.parent

    counter = 1
    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def process_image(image_path: Path):
    print(f"Processing image: {image_path}")

    text = ocr_image(image_path)
    if not text:
        print("No text detected, skipping.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    base_txt = OUTPUT_DIR / f"{image_path.stem}.txt"
    target_txt = get_unique_path(base_txt)

    notepad_win = get_or_launch_notepad()

    ensure_notepad_foreground(notepad_win)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.2)
    pyautogui.press("backspace")
    time.sleep(0.2)

    human_type(text, notepad_win)
    save_notepad_to_file(notepad_win, target_txt)

    try:
        notepad_win.close()
    except Exception:
        pass
    time.sleep(0.5)

    print(f"Saved to: {target_txt}")


def main():
    if not IMAGE_PATH.exists():
        print("Image not found.")
        return

    print("Starting. Don't use mouse/keyboard until finished.")
    time.sleep(3)

    process_image(IMAGE_PATH)

    print("Done.")


if __name__ == "__main__":
    main()
