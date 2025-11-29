import os
import csv
import shutil
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CSV_FILE = 'submissions.csv'

def get_submissions():
    submissions = []
    if os.path.exists('submissions.csv'):
        with open('submissions.csv', 'r') as file:
            reader = csv.DictReader(file)
            submissions = list(reader)
    return submissions

@app.route('/')
def index():
    data = get_submissions()
    return render_template('index.html', submissions=data)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        roll_no = request.form['roll_no']
        project_title = request.form['project_title']
        
        # 1. Get List of Files (Folder Upload)
        files = request.files.getlist('project_files')
        
        filename_to_save = ""
        
        if files:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Create a unique folder name for this student
            submission_folder_name = f"{name}_{roll_no}_{timestamp}"
            submission_path = os.path.join(app.config['UPLOAD_FOLDER'], submission_folder_name)
            
            # Create the directory
            os.makedirs(submission_path, exist_ok=True)

            # Save all files inside that directory
            for file in files:
                if file.filename:
                    # Maintain internal folder structure
                    file_path = os.path.join(submission_path, file.filename)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)

            # 2. Convert the folder to a ZIP file
            shutil.make_archive(submission_path, 'zip', submission_path)
            
            # 3. Clean up: Remove the raw folder, keep only the .zip
            shutil.rmtree(submission_path)
            
            # The final file is the folder name + .zip
            filename_to_save = f"{submission_folder_name}.zip"

        # Save to CSV
        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='') as csvfile:
            fieldnames = ['Timestamp', 'Name', 'Roll No', 'Title', 'Filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
                
            writer.writerow({
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'Name': name,
                'Roll No': roll_no,
                'Title': project_title,
                'Filename': filename_to_save
            })
            
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)