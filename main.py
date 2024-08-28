from flask import Flask, request, jsonify
import os

from extract_questions_questionare import Questionnire
from qa import QA

app = Flask(__name__)

app.config['REPORTS_UPLOAD_FOLDER'] = 'reports'
app.config['QUESTIONNIRE_UPLOAD_FOLDER'] = 'questionnire'

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message': "Working"})


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success",'message': "ESG Survey Automation by team Ranunculus"})

@app.route('/esg_reports/upload', methods=['POST'])
def upload_reports_files():
    # Check if the POST request has the file part
    if 'files' not in request.files:
        return jsonify({'message': 'No file part'})

    # Get the list of uploaded files
    files = request.files.getlist('files')

    # Get the yearOfReport parameter from the request
    year_of_report = request.form.get('YearOfReport')

    if year_of_report is None:
        return jsonify({'message': 'YearOfReport parameter is missing'})
    
    upload_files(year_of_report,files,app.config['REPORTS_UPLOAD_FOLDER'])

    return jsonify({'message': 'Document uploaded successfully'})

@app.route('/esg_reports/retrieve', methods=['POST'])
def retrieve_files():
    # Get reportYear parameter from the request
    report_year = request.form.get('reportYear')

    if report_year is None:
        return jsonify({'message': 'reportYear parameter is missing'})

    # Create the path to the year-specific folder
    year_folder_path = os.path.join(app.config['REPORTS_UPLOAD_FOLDER'], report_year)

    # Check if the folder exists
    if not os.path.exists(year_folder_path):
        return jsonify({'message': f'No files found for the year {report_year}'})

    # Get the list of files in the folder
    files_in_year_folder = os.listdir(year_folder_path)

    return jsonify({'message': f'Files for the year {report_year}', 'files': files_in_year_folder})

@app.route('/questionnaire/generatefirstdraft/pdf', methods=['POST'])
def upload_questionnaire_files():
    # Check if the POST request has the file part
    if 'files' not in request.files:
        return jsonify({'message': 'No file part'})

    # Get the list of uploaded files
    files = request.files.getlist('files')

    # Get the generateReportforYear parameter from the request
    generateReportforYear = request.form.get('generateReportforYear')

    upload_files(generateReportforYear,files,app.config['QUESTIONNIRE_UPLOAD_FOLDER'])

    if generateReportforYear is None:
        return jsonify({'message': 'generateReportforYear parameter is missing'})
    
    answers=get_answers(generateReportforYear)

    return jsonify({'message': 'Document uploaded successfully',"answers": answers})


@app.route('/questionnaire/generatefirstdraft/generateAnswer', methods=['POST'])
def get_answer():
    inputQuestion = request.form.get('inputQuestion')
    reportYear = request.form.get('reportYear')

    
    if inputQuestion is None or reportYear is None:
        return jsonify({'message': 'generateReportforYear or reportYear parameter is missing'})
    
    qa=QA(reportYear)
    qa.init_chromadb(os.path.join(app.config['REPORTS_UPLOAD_FOLDER'], reportYear))
    citation,answer,metadata=qa.query(inputQuestion)
    output={"question": inputQuestion,"citation": citation, "answer": answer,"metadata": metadata}

    return jsonify({'output': output})



def upload_files(year,files,upload_folder):

    # Create the year-specific reports folder if it doesn't exist
    year_folder_path = os.path.join(upload_folder, str(year))
    if not os.path.exists(year_folder_path):
        os.makedirs(year_folder_path)
        
    # Save each uploaded file
    filenames = []
    for file in files:
        if file.filename != '':
            filename = os.path.join(year_folder_path, file.filename)
            file.save(filename)
            filenames.append(filename)

def get_answers(year):

    # Create the year-specific reports folder if it doesn't exist
    questions=[]
    year_folder_path = os.path.join(app.config['QUESTIONNIRE_UPLOAD_FOLDER'], str(year))
    for dirpath, dirnames, filenames in os.walk(year_folder_path):
            for file in filenames:
                questionnire=Questionnire()
                questions += questionnire.fetch_questions_from_pdf(os.path.join(dirpath, file))

    output=[]
    qa=QA(year)
    qa.init_chromadb(os.path.join(app.config['REPORTS_UPLOAD_FOLDER'], str(year)))

    for question in questions:
        question_split=question.split('Response options')
        final_question=question_split[0]
        response_options=""
        if(len(question_split)>1):
            response_options=question_split[1]

        citation,answer,metadata=qa.query(final_question,response_options)
        output.append({"question": final_question,"citation": citation, "answer": answer,"metadata": metadata})
        break

    return output


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)