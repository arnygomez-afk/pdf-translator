from flask import Flask, request, render_template_string
import fitz  # PyMuPDF
import requests
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML template
HTML_TEMPLATE = """
<!doctype html>
<title>PDF Translator</title>
<h2>Sube un archivo PDF para traducir</h2>
<form method=post enctype=multipart/form-data>
  <input type=file name=pdf_file>
  <select name=target_lang>
    <option value="en">Inglés</option>
    <option value="es">Español</option>
    <option value="fr">Francés</option>
    <option value="de">Alemán</option>
    <option value="it">Italiano</option>
    <option value="pt">Portugués</option>
  </select>
  <input type=submit value=Traducir>
</form>
{% if translated_text %}
<h3>Texto traducido:</h3>
<pre>{{ translated_text }}</pre>
{% endif %}
"""

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def translate_text(text, target_lang):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "auto",
        "target": target_lang,
        "format": "text"
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["translatedText"]
    else:
        return "Error en la traducción."

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = None
    if request.method == "POST":
        file = request.files["pdf_file"]
        target_lang = request.form["target_lang"]
        if file and file.filename.endswith(".pdf"):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            original_text = extract_text_from_pdf(file_path)
            translated_text = translate_text(original_text, target_lang)
    return render_template_string(HTML_TEMPLATE, translated_text=translated_text)

if __name__ == "__main__":
    app.run(debug=True)
