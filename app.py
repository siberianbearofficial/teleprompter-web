from flask import Flask, render_template, url_for, request, redirect, flash
import pyrebase
import os
from avatar import crop, downloadAvatar, uploadAvatar

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

app.config['SECRET_KEY'] = config['apiKey']

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


userId = ''
current_user = dict()


def sign_out():
  # Удаляем предыдущий аватар, если он еще сохранен
  try:
    os.remove('static/images/avatar.jpeg')
  except:
    print('Can\'t remove avatar')
  global userId
  global current_user
  userId = ''
  current_user = dict()


sign_out()


@app.route('/home')
def home():
  return redirect('/')


@app.route('/sign-out')
def signout():
  sign_out()
  return redirect('/')


@app.route('/')
def index():
  name = ''
  global current_user
  global userId
  if current_user != dict():
    userId = current_user['localId']
    print('Signed in')
  if userId != '':
    print('Trying to get name...')
    name = db.child("users").child(userId).child('name').get().val()
    if os.path.exists('static/images/avatar.jpeg'):
      return render_template('index.html', name='Здравствуй, {0}!'.format(name), downloaded=True)
    else:
      return render_template('index.html', name='Здравствуй, {0}!'.format(name), downloaded=False)
  else:
    return redirect('/login')


@app.route('/about')
def about():
  return 'About page'


@app.route('/files-list')
def filesList():
  if current_user != dict() and userId != '':
    return render_template('test.html', user_id=userId)
  else:
    return redirect('/')


@app.route('/create', methods=["GET", "POST"])
def create():
  if current_user != dict() and userId != '':
    if request.method == 'POST':
      editor = request.form['editor']
      if request.form['title'] != '':
        fileName = request.form['title'] + '.html'
      else:
        return render_template('edit.html', content=editor, title="", notitle=True)
      file = open('static/files/' + fileName, 'w')
      file.write(editor)
      file.close()
      fullFileName = userId + '/files/' + fileName
      storage.child(fullFileName).put('static/files/' + fileName)
      os.remove('static/files/' + fileName)
      flash('Изменения сохранены!')
      return render_template('edit.html', content=editor, title=fileName[:fileName.rfind('.')], notitle=False)
    else:
      # Для тестов: zVElAdFPEiUd3FwL2Y08snmk2wZ2/TestForServer.html
      return render_template('edit.html', content="", title="", notitle=True)
  else:
    return redirect('/')


@app.route('/edit/<string:localId>/<string:fileName>', methods=['POST', 'GET'])
def edit(localId, fileName):
  if current_user != dict() and userId != '':
    if request.method == 'POST':
      editor = request.form['editor']
      fileName = request.form['title'] + '.html'
      file = open('static/files/' + fileName, 'w')
      file.write(editor)
      file.close()
      fullFileName = localId + '/files/' + fileName
      storage.child(fullFileName).put('static/files/' + fileName)
      os.remove('static/files/' + fileName)
      flash('Изменения сохранены!')
      return render_template('edit.html', content=editor, title=fileName[:fileName.rfind('.')], notitle=False)
    else:
      if localId == userId:
        # Если id пользователя (который вошел на сайт под своим логином и паролем) совпадает с id пользователя, загрузившего документ (то есть, пользователь хочет просмотреть свой документ, а не чужой), то все нормально, можно открывать страницу редактирования
        # Для тестов: zVElAdFPEiUd3FwL2Y08snmk2wZ2/TestForServer.html
        print('We are ready to download a file!')
        print(localId)
        print(fileName)
        fullFileName = localId + '/files/' + fileName
        storage.child(fullFileName).download('static/files/' + fileName)
        file = open('static/files/' + fileName)
        content = file.read()
        file.close()
        os.remove('static/files/' + fileName)
        return render_template('edit.html', content=content, title=fileName[:fileName.rfind('.')], notitle=False)
      else:
        return render_template('exception.html')
  else:
    return redirect('/')

@app.route('/settings', methods=['POST', 'GET'])
def settings():
  if current_user != dict() and userId != '':
    if request.method == 'POST':
      # Сохранение настроек
      textColor = request.form['textColor']
      textSize = request.form['textSize']
      bgColor = request.form['bgColor']
      speed = request.form['speed']

      try:
        dbPath = 'users/' + userId + '/settings/'
        settingsDict = {
          "textColor": textColor,
          "textSize": textSize,
          "bgColor": bgColor,
          "speed": speed
        }
        db.child(dbPath).set(settingsDict)

        flash('Изменения сохранены!')
        return redirect('/settings')
      except:
        return render_template('exception.html') 
    else:
      # Получение настроек
      textColor = 0
      textSize = 16
      bgColor = 0
      speed = 60

      dbPath = 'users/' + userId + '/settings/'
      textSize = db.child(dbPath + 'textSize').get(current_user['idToken']).val()
      textColor = db.child(dbPath + 'textColor').get(current_user['idToken']).val()
      speed = db.child(dbPath + 'speed').get(current_user['idToken']).val()
      bgColor = db.child(dbPath + 'bgColor').get(current_user['idToken']).val()
      
      return render_template('settings.html', bgColor=bgColor, textColor=textColor, textSize=textSize, speed=speed)
  else:
    return redirect('/')

@app.route('/login', methods=['POST', 'GET'])
def login():
  global current_user
  global userId
  if current_user == dict() or userId == '':
    if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      print(email, password)
      try:
        current_user = auth.sign_in_with_email_and_password(email, password)
        userId = current_user['localId']
        downloadAvatar(storage, current_user)
        return redirect('/')
      except:
        return render_template('exception.html')
    else:
      return render_template('login.html')
  else:
    sign_out()
    return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  global current_user
  global userId
  if current_user == dict() or userId == '':
    if request.method == 'POST':
      email = request.form['email']
      password = request.form['password']
      name = request.form['name']
      print(email, password, name)
      try:
        current_user = auth.create_user_with_email_and_password(email, password)
        userId = current_user['localId']
        print(userId)

        # Сохраняем имя
        db.child('users/'+userId+'/name').set(name)
        db.child('users/'+userId+'/email').set(email)
        return redirect('/')
      except:
        return render_template('exception.html')
    else:
      return render_template('signup.html')
  else:
    sign_out()
    return redirect('/signup')


@app.route('/save-avatar', methods=['POST'])
def saveavatar():
  avatarFile = request.files['avatarFile']
  avatarFile.save('static/images/avatar.jpeg')
  crop()
  uploadAvatar(storage, current_user)
  return redirect('/')


@app.route('/profile', methods=['POST', 'GET'])
def profile():
  if current_user != dict() and userId != '':
    if request.method == 'POST':
      # Сохранение имени
      name = request.form['name']
      try:
        dbPath = 'users/' + userId + '/name'
        db.child(dbPath).set(name)
        flash('Изменения сохранены!')
        return redirect('/profile')
      except:
        return render_template('exception.html') 
    else:
      # Получение настроек
      dbPath = 'users/' + userId + '/name'
      name = db.child(dbPath).get().val()
      if os.path.exists('static/images/avatar.jpeg'):
        return render_template('profile.html', name=name, downloaded=True)
      else:
        return render_template('profile.html', name=name, downloaded=False)
  else:
    return redirect('/')


if __name__ == "__main__":
  app.run(
    host='0.0.0.0',
    port=8080,
    debug=True
  )