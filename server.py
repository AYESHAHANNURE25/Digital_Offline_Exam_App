from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import json
import os
import datetime

# Create an instance of the Flask class
app = Flask(__name__)

# Directory containing question JSON files
QUESTIONS_DIR = '.'
# Excel file for storing all exam results
EXCEL_FILE = 'all_exam_results.xlsx'


def get_question_papers():
    """Finds all question JSON files and returns their names."""
    papers = []
    # Check for the default file first
    if os.path.exists(os.path.join(QUESTIONS_DIR, 'questions.json')):
        papers.append({'id': 'default', 'name': 'Default Exam'})
    # Iterate through other files
    for filename in os.listdir(QUESTIONS_DIR):
        if filename.startswith('questions_') and filename.endswith('.json'):
            # Extract the paper_id, removing the "questions_" and ".json" parts
            paper_id = filename[len('questions_'):-len('.json')]
            papers.append({'id': paper_id, 'name': f"Class {paper_id.upper().replace('_', ' ')} Exam"})
    return papers


def load_questions_from_json(paper_id):
    """Loads questions from a specific JSON file."""
    if paper_id == 'default':
        filename = 'questions.json'
    else:
        filename = f'questions_{paper_id}.json'

    try:
        with open(os.path.join(QUESTIONS_DIR, filename), 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        print(f"Error: Question paper file '{filename}' not found.")
        return []

    return questions


@app.route('/', methods=['GET', 'POST'])
def login():
    """Handles the student login form and redirects to the exam."""
    question_papers = get_question_papers()

    # Print the papers found for debugging
    print("Found the following question papers:")
    for paper in question_papers:
        print(f" - {paper['name']} (ID: {paper['id']})")

    if request.method == 'POST':
        student_id = request.form.get('student_id')
        student_name = request.form.get('student_name')
        school_name = request.form.get('school_name')
        paper_id = request.form.get('paper_id')

        # If no paper is selected, default to the first one found
        if not paper_id and question_papers:
            paper_id = question_papers[0]['id']
        elif not paper_id:
            # If no papers are found at all, return an error message
            return "No exam papers found! Please add a 'questions.json' file or 'questions_*.json' files to the project directory."

        # Redirect to the exam page with student info and selected paper
        return redirect(url_for('exam', student_id=student_id, student_name=student_name, school_name=school_name,
                                paper_id=paper_id))

    return render_template('index.html', question_papers=question_papers)


@app.route('/exam')
def exam():
    """Fetches questions from the selected JSON file and displays the exam page."""
    paper_id = request.args.get('paper_id')

    # This will print the paper ID you selected and the questions it's trying to load
    print(f"Loading questions for paper_id: {paper_id}")
    questions = load_questions_from_json(paper_id)
    print(f"Found {len(questions)} questions.")

    # Get student info from the URL parameters
    student_id = request.args.get('student_id')
    student_name = request.args.get('student_name')
    school_name = request.args.get('school_name')

    # This will render the new exam.html page with the questions data
    return render_template('exam.html', questions=questions, student_id=student_id, student_name=student_name,
                           school_name=school_name, paper_id=paper_id)


@app.route('/submit_answers', methods=['POST'])
def submit_answers():
    """Processes and saves the student's answers to an Excel file."""

    # Create an empty dictionary to store the student's data
    student_data = {
        'student_id': request.form.get('student_id'),
        'student_name': request.form.get('student_name'),
        'school_name': request.form.get('school_name'),
        'paper_id': request.form.get('paper_id'),
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Iterate through form data to get answers
    for key, value in request.form.items():
        if key.startswith('answer_'):
            question_id = key.split('_')[1]
            student_data[f'answer_{question_id}'] = value

    # Check if the Excel file exists
    if os.path.exists(EXCEL_FILE):
        # If it exists, read the existing data and append the new data
        df = pd.read_excel(EXCEL_FILE)
        new_row = pd.DataFrame([student_data])
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        # If the file doesn't exist, create a new DataFrame
        df = pd.DataFrame([student_data])

    # Save the DataFrame to the Excel file
    try:
        df.to_excel(EXCEL_FILE, index=False)
        return "Answers submitted successfully and saved to Excel!"
    except Exception as e:
        return f"Error saving answers to Excel: {e}"


# Run the app if the script is executed directly
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
