from flask import Flask, render_template, request
import subprocess

app = Flask(__name__)
app.debug = False


@app.route('/')
def home():
    return render_template('index.html')  # Страница с поиском


@app.route('/about')
def about():
    return render_template('about.html')  # Страница "О нас"


@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    try:
        result = subprocess.check_output(['python3', 'final.py', query], text=True)
    except subprocess.CalledProcessError as e:
        result = f"Произошла ошибка при выполнении поиска: {e.output}"
    return render_template('result.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)
