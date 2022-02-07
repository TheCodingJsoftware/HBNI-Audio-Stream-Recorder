from os import listdir
from os.path import isfile, join
from flask import send_file
from flask import Flask, render_template
from flask import current_app, url_for

app = Flask(__name__)
@app.route('/')
def upload_form():
    global dloads, recordingsDir, dloads_src
    recordingsDir = 'F:\\Code\\Python-Projects\\Hutterite-Church\\Recorder\\Recordings'
    downloadableRecordings = [f for f in listdir(recordingsDir) if isfile(join(recordingsDir, f))]
    return render_template('index.html', downloadableRecordings=downloadableRecordings)

@app.route("/downloadFile/<path>")
def downloadFile (path = None):
    print(path)
    path = path.split('\\')
    fileName = path[-1]
    path.pop(-1)
    path.append('Recordings')
    path.append(fileName)
    path = '\\'.join(path)

    return send_file(path, as_attachment=True)
if __name__ == "__main__":
    website_url = 'hbniaudioarchive.hbni.net:5000'
    # app.config['SERVER_NAME'] = website_url
    # with app.test_request_context():
    #     url = url_for('index', _external=True)
    app.run(host='10.0.0.217', port='5000', debug=False, threaded=True)