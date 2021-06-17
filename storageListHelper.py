import requests
from oauth2client.service_account import ServiceAccountCredentials

def list_all_files(path, config, current_user):
  print('We are near...')
  # scopes = ['https://www.googleapis.com/auth/firebase.database', 'https://www.googleapis.com/auth/userinfo.email', "https://www.googleapis.com/auth/cloud-platform"]
  # service_account_type = type(config["serviceAccount"])
  # if service_account_type is str:
  #   credentials = ServiceAccountCredentials.from_json_keyfile_name(config["serviceAccount"], scopes)
  # else:
  #   credentials = ServiceAccountCredentials.from_json_keyfile_dict(config["serviceAccount"], scopes)
  url = 'https://storage.googleapis.com/storage/v1/b/{0}/o?prefix={1}&key={2}'.format(config['storageBucket'], path, config['apiKey'])
  # access_token = credentials.get_access_token().access_token
  access_token = current_user['idToken']
  headers = {
    'Authorization': 'Bearer [{0}]'.format(access_token),
    'Accept': 'application/json'
  }
  request_object = requests.get(url, headers=headers)
  request_dict = request_object.json()
  print(request_dict)