from flask import Flask,request,render_template,redirect,url_for,session

app = Flask(__name__)
app.secret_key = 'your_my_secret_keysy' 
@app.route('/')
def main():
    return render_template('inicio.html')

if __name__ == "__main__":
    app.run(debug=True)
