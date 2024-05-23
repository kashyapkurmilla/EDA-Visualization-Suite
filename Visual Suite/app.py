from flask import Flask,redirect, render_template, render_template_string, request, session,url_for
import pandas as pd
import io
 
app = Flask(__name__)
app.secret_key = "sessionkey1"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        df = pd.read_csv(file)
        session['preview_df'] = df.head(5).to_html(index=False) 
        session['csv_data'] = df.to_html(index=False)
        return render_template('index.html', tables=[session['preview_df']])
    else:
        return redirect(request.url)
    

@app.route('/data_viz')
def data_viz():
        if 'preview_df' in session:
            preview_html = session['csv_data']
            return render_template('data_viz.html', tables=[preview_html])
        else:
            return redirect(url_for('index'))

if __name__  == "__main__":
    app.run(debug=True)