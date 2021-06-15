from flask import Flask, render_template, url_for, request, redirect, flash
import pyrebase
import os
import storageListHelper as slh

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

userId = ''
current_user = dict()

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
storage = firebase.storage()


@app.route('/')
@app.route('/home')
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
    name = 'Здравствуй, ' + name + '!'

    # Выгружаем список файлов
    storagePath = userId + '/files'
    slh.list_all_files(config['storageBucket'], storagePath, config['apiKey'])

    return render_template('index.html', name=name)
  else:
    return render_template('index_guest.html')


@app.route('/about')
def about():
  return 'About page'

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
      return render_template('edit.html', content=editor, title=fileName[:fileName.rfind('.')])
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
        return render_template('edit.html', content=content, title=fileName[:fileName.rfind('.')])
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
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    print(email, password)
    try:
      global current_user
      current_user = auth.sign_in_with_email_and_password(email, password)
      global userId
      userId = current_user['localId']
      print(userId)
      return redirect('/')
    except:
      return render_template('exception.html')
  else:
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']
    print(email, password, name)
    try:
      global current_user
      current_user = auth.create_user_with_email_and_password(email, password)
      global userId
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
      return render_template('profile.html', name=name)
  else:
    return redirect('/')


if __name__ == "__main__":
  app.run(
    host='0.0.0.0',
    port=8080,
    debug=True
  )