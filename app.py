from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import SelectField, FileField, SubmitField
from wtforms.validators import DataRequired
import pandas as pd
import secrets
import re
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

CATEGORY_CONFIG = {
    'Cemetery': {'age_of_owner': [r'\d+', '2 years']},

    'Allotment': {'age_of_owner': [r'\d+', '34'],
                  'date_of_birth': [r'\d\d/\d\d/\d\d', '19/03/87'],
                  'type_of_allotment': [r'(Community|Private)', 'Community or Private'],
                  'size_of_allotment': ['\d{3}', '300'],
                  'duration_of_time_occupied': [r'\d\syears', '3 years'],
                  'amount_paid_per_month': ['\d+', '30'],
                  'amount_paid_in_total': [r'\d+', '190']
                  }
    # Add more categories and their column requirements here
}


class FileUploadForm(FlaskForm):
    category = SelectField('Category', choices=['Cemetery', 'Allotment'],
                           validators=[DataRequired()])
    file = FileField('CSV File', validators=[DataRequired()])
    submit = SubmitField('Validate')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileUploadForm()
    if form.validate_on_submit():
        category = form.category.data
        file = request.files['file']
        if file.filename == '':
            return 'No file selected. Please choose a CSV file.'
        if category == '':
            return 'No category selected. Please choose a category.'

        # Check if the file is a CSV file
        _, file_ext = os.path.splitext(file.filename)
        if file_ext.lower() != '.csv':
            return render_template('validation_result.html', not_csv=True)

        data = pd.read_csv(file)
        issue_messages = []

        for column_name, column_data in data.items():
            if column_name not in CATEGORY_CONFIG[form.category.data.title()]:
                return render_template('validation_result.html', invalid_column=column_name)

            regex, correct_example_format = CATEGORY_CONFIG[form.category.data.title()][column_name]
            for row_data_point in column_data:
                print(row_data_point)
                if not bool(re.fullmatch(regex, str(row_data_point))):
                    issue_messages.append(f'Your invalid data point: {row_data_point}. Valid data point example: {correct_example_format}')
                    print('Invalid data point')

        if not issue_messages:
            return render_template('validation_result.html')
        return render_template('validation_result.html', issues=issue_messages, total_issues=len(issue_messages))

    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
