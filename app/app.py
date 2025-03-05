from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from flask_cors import CORS
from ai_service import query_ai
import os
import shutil
import zipfile

# Define directories
GENERATED_SCRIPTS_DIR = os.path.abspath("generated_scripts")
FRONTEND_DIR = os.path.abspath("frontend")

# Ensure the scripts directory exists
os.makedirs(GENERATED_SCRIPTS_DIR, exist_ok=True)

# Initialize Flask app
app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIR, "static"), 
            template_folder=os.path.join(FRONTEND_DIR, "templates"))
CORS(app)  # Enable CORS for frontend communication

# Serve the frontend
@app.route('/')
def index():
    return render_template("index.html")

# Route to generate a script based on user input
@app.route('/generate', methods=['POST'])
def generate_script():
    data = request.json
    stack = data.get("stack")
    description = data.get("description")

    if not stack or not description:
        return jsonify({"error": "Missing required parameters"}), 400

    project_name = description.replace(" ", "_").lower()
    project_path = os.path.join(GENERATED_SCRIPTS_DIR, project_name)

    os.makedirs(project_path, exist_ok=True)

    # Call AI service to generate script
    ai_response = query_ai(description, stack)

    if not ai_response.get("files"):
        return jsonify({"error": "AI failed to generate a script."}), 500

    # Save generated files
    for file in ai_response["files"]:
        file_path = os.path.join(project_path, file["name"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file["content"])

    return jsonify({
        "message": "Script generated successfully! Click below to download.",
        "project_name": project_name
    })

# Route to download a single script
@app.route('/generated_scripts/<path:filename>')
def download_script(filename):
    return send_from_directory(GENERATED_SCRIPTS_DIR, filename, as_attachment=True)

# Route to download all scripts as a ZIP file
@app.route('/download/<project_name>')
def download_project_zip(project_name):
    project_path = os.path.join(GENERATED_SCRIPTS_DIR, project_name)
    
    if not os.path.exists(project_path):
        return jsonify({"error": "Project not found."}), 404
    
    zip_filename = f"{project_name}.zip"
    zip_path = os.path.join(GENERATED_SCRIPTS_DIR, zip_filename)

    # Create ZIP file
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, GENERATED_SCRIPTS_DIR))
    
    return send_file(zip_path, as_attachment=True)

@app.route("/generate", methods=["POST"])
def generate_script_v2():  # <-- Renamed function
    # Your function logic here
    data = request.json
    script_name = data.get("script_name", "script.py")
    script_content = data.get("script_content", "")

    # Define file path
    file_path = os.path.join("generated_scripts", script_name)

    # Save script
    os.makedirs("generated_scripts", exist_ok=True)
    with open(file_path, "w") as f:
        f.write(script_content)

    return jsonify({"message": "Script generated successfully!", "file_path": file_path})

if __name__ == "__main__":
    app.run(debug=True, port=5000)