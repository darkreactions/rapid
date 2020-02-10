import json
import os

image_list = os.listdir('./data/images')
data = {'image_list': image_list}
json.dump(data, open('./data/image_list.json', 'w'))
