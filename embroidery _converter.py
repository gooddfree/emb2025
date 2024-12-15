from flask import Flask, request, jsonify, send_from_directory
from pyembroidery import *
from PIL import Image
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def convert_image_to_embroidery(input_image_path, output_file_path, format):
    image = Image.open(input_image_path).convert("L")  # Convert to grayscale
    image = image.resize((100, 100))  # Resize
    pattern = EmbPattern()

    width, height = image.size
    for y in range(height):
        for x in range(width):
            if image.getpixel((x, y)) < 128:
                pattern.add_stitch_absolute(STITCH, x, y)
    pattern.end()
    write(pattern, output_file_path)

@app.route("/convert", methods=["POST"])
def convert():
    if "image" not in request.files or "format" not in request.form:
        return jsonify({"success": False, "error": "Invalid request"}), 400

    file = request.files["image"]
    format = request.form["format"].lower()
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_filename = f"{os.path.splitext(file.filename)[0]}.{format}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    file.save(input_path)
    try:
        convert_image_to_embroidery(input_path, output_path, format)
        return jsonify({"success": True, "file_url": f"/outputs/{output_filename}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/outputs/<filename>")
def download_file(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True)