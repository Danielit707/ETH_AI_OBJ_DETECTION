import mimetypes
import os
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
import httpx

API_URL = os.environ.get("DETECTION_API_URL", "http://127.0.0.1:8000").rstrip("/")


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.geometry("760x560")
    window.title("Adverse Weather Object Detection")

    title = ctk.CTkLabel(
        window,
        text="Adverse Weather Object Detection",
        font=("Arial", 26, "bold"),
    )
    title.pack(pady=(36, 8))
    description = ctk.CTkLabel(
        window,
        text=f"Select a road-scene image to detect objects using the API at {API_URL}",
        wraplength=680,
    )
    description.pack(pady=(0, 20))

    status = ctk.CTkLabel(window, text="Choose a JPEG, PNG, or WebP image.")
    status.pack(pady=8)
    results = ctk.CTkTextbox(window, width=680, height=330, wrap="word")
    results.pack(padx=32, pady=12, fill="both", expand=True)
    results.insert("1.0", "Detections will appear here.")
    results.configure(state="disabled")

    def show_results(text):
        results.configure(state="normal")
        results.delete("1.0", "end")
        results.insert("1.0", text)
        results.configure(state="disabled")

    def select_image():
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=(("Images", "*.jpg *.jpeg *.png *.webp"),),
        )
        if not file_path:
            return

        image_path = Path(file_path)
        content_type = mimetypes.guess_type(image_path.name)[0] or "application/octet-stream"
        status.configure(text=f"Running inference for {image_path.name}...")
        window.update_idletasks()

        try:
            with image_path.open("rb") as image_file:
                response = httpx.post(
                    f"{API_URL}/predict",
                    files={"image": (image_path.name, image_file, content_type)},
                    params={"image_size": 512},
                    timeout=180,
                )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            try:
                detail = error.response.json().get("detail", error.response.text)
            except ValueError:
                detail = error.response.text
            status.configure(text=f"Prediction failed (HTTP {error.response.status_code}).")
            show_results(str(detail))
            return
        except httpx.HTTPError as error:
            status.configure(text="Could not reach the inference API.")
            show_results(f"Check that the API is running at {API_URL}.\n\n{error}")
            return
        except OSError as error:
            status.configure(text="Could not read the selected image.")
            show_results(str(error))
            return

        prediction = response.json()
        detections = prediction["detections"]
        status.configure(
            text=(
                f"{len(detections)} detection(s) in "
                f"{prediction['width']}x{prediction['height']} image."
            )
        )
        if not detections:
            show_results("No objects detected above the confidence threshold.")
            return

        lines = []
        for detection in detections:
            box = detection["bbox"]
            lines.append(
                f"{detection['class_name']} — {detection['confidence']:.1%} confidence\n"
                f"  Bounding box: ({box['x1']:.1f}, {box['y1']:.1f}) to "
                f"({box['x2']:.1f}, {box['y2']:.1f})"
            )
        show_results("\n\n".join(lines))

    button = ctk.CTkButton(window, text="Choose image and detect", command=select_image)
    button.pack(pady=(0, 24))
    window.mainloop()


if __name__ == "__main__":
    main()
