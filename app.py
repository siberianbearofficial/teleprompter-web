from flask import Flask, render_template, url_for
import pyrebase

app = Flask(
	__name__,
	template_folder='templates',
	static_folder='static'
)

config = {
  'apiKey': "AIzaSyA3ZYaV-3uJmusX3-nfV71CT5pbjyLqbtY",
  'authDomain': "teleprompterandroidjava.firebaseapp.com",
  'databaseURL': "https://teleprompterandroidjava-default-rtdb.europe-west1.firebasedatabase.app",
  'projectId': "teleprompterandroidjava",
  'storageBucket': "teleprompterandroidjava.appspot.com",
  'messagingSenderId': "300471537841",
  'appId': "1:300471537841:web:de99d6f9e4316faeddd290",
  'measurementId': "G-Y3RVRFQ01W"
}

firebase = pyrebase.initialize_app(config)


@app.route('/')
@app.route('/home')
def index():
  return render_template('index.html')


@app.route('/about')
def about():
  return 'About page'

@app.route('/login', methods=['POST', 'GET'])
def login():
  return "Successful!"


@app.route('/user/<string:name>/<int:id>')
def user(name, id):
  return "User name: " + name + ", user id: " + str(id)


if __name__ == "__main__":
  app.run(
    host='0.0.0.0',
    port=8080,
    debug=True
  )