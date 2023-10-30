"""
Extracts image features using DINOv2 
Model results are saved as a 
Resulting features (tesor) are saved as a csv file
"""

import torch
import pandas as pd
from transformers import AutoImageProcessor, AutoModel
from transformers.modeling_outputs import BaseModelOutputWithPooling 
from PIL import Image

# image_file = "dinov2/data/00002-page37-Im0.jpg"
image_file = "dinov2/data/image_CMYK_color.jpg"


image = Image.open(image_file)

processor = AutoImageProcessor.from_pretrained('facebook/dinov2-small')
model = AutoModel.from_pretrained('facebook/dinov2-small')

inputs = processor(images=image, return_tensors="pt") # returns tensor
# print(inputs)
outputs = model(**inputs)


print(type(outputs))
# print(outputs.to_tuple())

tensor = outputs.last_hidden_state

# remove dimensions of size 1, i.e. squeeze tensor
tensor_2d = torch.squeeze(tensor)

# convert to pandas dataframe
df = pd.DataFrame(tensor_2d.detach().numpy())

import pickle

# save model output to disk
pickle_filename = image_file.split('.')[0] + '.pickle'
with open(pickle_filename, 'wb') as f:
    pickle.dump(outputs, f)

import time
time.sleep(3)

# TODO: create a function to load pickle file

with open(pickle_filename, 'rb') as f:
    outputs2 = pickle.load(f)

print(type(outputs2))
print(outputs2)

# save full object (transformers output) to disk
csv_filename = image_file.split('.')[0] + '.csv'
# df.to_csv(csv_filename, sep=',', index=False, encoding='utf-8')


