from flask import Flask, render_template, request, send_from_directory, url_for
import pandas as pd
import os
from datetime import datetime
import pytz

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        
        est = pytz.timezone("US/Eastern")
        today_str = datetime.now(est).strftime("%Y%m%d_%H%M%S")
        
        input_filename = f"input_{today_str}.csv"
        input_file_path = os.path.join(UPLOAD_FOLDER, input_filename)
        uploaded_file.save(input_file_path)

        output_file_name = f"it_true-up_{today_str}.csv"
        output_file_path = os.path.join(UPLOAD_FOLDER, output_file_name)

        # Logic from it_true-up.py
        df = pd.read_csv(input_file_path)
        df['Created At'] = pd.to_datetime(df['Created At'], utc=True).dt.tz_convert('US/Eastern')

        df = df.groupby(by='Email', as_index=False).agg({
            'First Name': 'first',
            'Last Name': 'first',
            'Address': 'first',
            'City': 'first',
            'Employer': 'first',
            'Occupation': 'first',
            'Mobile': 'first',
            'Source Code': 'first',
            'Source Url': 'first',
            'State': 'first',
            'Utm Campaign': 'first',
            'Utm Medium': 'first',
            'Utm Source': 'first',
            'Utm Term': 'first',
            'Zip': 'first',
            'Created At': 'max'
        })

        df.rename(columns={
            'Email': 'email',
            'First Name': 'firstName',
            'Last Name': 'lastName',
            'Address': 'address',
            'City': 'city',
            'Mobile': 'phoneNumber',
            'Source Url': 'Source URL',
            'State': 'state',
            'Utm Campaign': 'UTM Campaign',
            'Utm Medium': 'UTM Medium',
            'Utm Source': 'UTM Source',
            'Utm Term': 'UTM Term',
            'Zip': 'zip',
            'Created At': 'Donation_date'
        }, inplace=True)

        df.to_csv(output_file_path, index=False)

        download_url = url_for("download_file", filename=output_file_name)
        return render_template("index.html", status="ready", download_url=download_url)

    return render_template("index.html", status=None)

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
