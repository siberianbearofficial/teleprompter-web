from PIL import Image


image_path = 'static/images/avatar.jpeg'
image_size = (100, 100)


def crop_center(pil_img, crop_width: int, crop_height: int) -> Image:
  img_width, img_height = pil_img.size
  return pil_img.crop(((img_width - crop_width) // 2,
                        (img_height - crop_height) // 2,
                        (img_width + crop_width) // 2,
                        (img_height + crop_height) // 2))
 
 
def crop_max_square(pil_img):
  return crop_center(pil_img, min(pil_img.size), min(pil_img.size))
 

def crop():
  im = Image.open(image_path)
  im_new = crop_max_square(im)
  resize_image(im_new, image_size)


def resize_image(image, size):
    width, height = image.size 
    resized_image = image.resize(size)
    width, height = resized_image.size
    resized_image = resized_image.convert('RGB')
    resized_image.save(image_path, quality=95)


def downloadAvatar(storage, current_user):
  try:
    storage.child(current_user['localId']+'/avatar.jpeg').download('static/images/avatar.jpeg')
  except:
    print('Exception!')


def uploadAvatar(storage, current_user):
  try:
    storage.child(current_user['localId']+'/avatar.jpeg').put('static/images/avatar.jpeg', current_user['idToken'])
  except:
    print('Exception!')