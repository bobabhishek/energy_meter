from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
from meter_reader import MeterReader
from data_handler import DataHandler

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

meter_reader = MeterReader()
data_handler = DataHandler()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract reading
            reading = meter_reader.extract_reading(filepath)

            # Generate metadata
            metadata = meter_reader.generate_metadata()

            # Save to CSV
            data_handler.save_reading(reading, metadata)

            return jsonify({
                'reading': reading,
                'metadata': metadata
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400


@app.route('/consumption')
def get_consumption():
    period = request.args.get('period', 'daily')
    start = request.args.get('start')
    end = request.args.get('end')
    try:
          result = data_handler.calculate_consumption(period, start, end)
          return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)


