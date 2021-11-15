#%%
import io
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "photo-manager-proto-97c81b37f3da.json" 

from google.cloud import vision

client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
# file_name = os.path.abspath('samples/snippets/detect/resources/wakeupcat.jpg')
file_path = os.path.abspath('christer.jpg')

# Loads the image into memory
with io.open(file_path, 'rb') as image_file:
    image_content = image_file.read()

image = vision.Image(content=image_content)

#%%

#%%
print('=== Landmarks:')
response = client.landmark_detection(image=image)
landmarks = response.landmark_annotations

for landmark in landmarks:
    print(landmark.description)
    for location in landmark.locations:
        lat_lng = location.lat_lng
        print('Latitude {}'.format(lat_lng.latitude))
        print('Longitude {}'.format(lat_lng.longitude))


#%%
print("=== Faces:")
response = client.face_detection(image=image)
faces = response.face_annotations

for face in faces:
    print(face)

    vertices = for vertex in face.bounding_poly.vertices])
    print('face bounds: {}'.format(','.join(vertices)))
# %%
