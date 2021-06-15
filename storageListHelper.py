import requests

def list_all_files(bucket, path, token):
  url = 'https://storage.googleapis.com/storage/v1/b/{0}/o?prefix={1}'.format(bucket, path)
  headers = {"Authorization": "Firebase " + token}
  request_object = requests.get(url, headers=headers)
  request_dict = request_object.json()
  print(request_dict)