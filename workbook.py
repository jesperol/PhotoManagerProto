# %%
import io, os, json, pprint, requests, base64
from PIL import Image, ImageDraw
from google.cloud import vision
from IPython import display

# Rerun to reset filename and present dialog
image_file_name = ''
def select_image_file():
    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter.filedialog import askopenfilename

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(filetypes=(("Jpeg", "*.jpg"),)) # show an "Open" dialog box and return the path to the selected file
    return  filename or "marstrand.jpg"

# Damnit, FIX:
class glob: pass
db = glob()

# Also load azure cognitive services endpoint uri and our keys. as store in the same file... 
with open("photo-manager-proto.json") as f:
    db.creds = json.load(f)

# from ImageDraw.ImageColor.colormap, to draw with...
colors = ['red', 'green', 'blue', 'yellow', 'orange', 'peachpuff', 'purple']

if not image_file_name:
    image_file_name = select_image_file()

# Let's read some image data into a variable that can be used by succeding methods
with open(image_file_name, "rb") as image_file:
    db.image_data = image_file.read()

# Google Cloud Vision client seem to like the image data wrapped like this
# Needs a service account or something..
# Set this environment variable so tat google.cloud libs knows where to get credentials
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "photo-manager-proto.json" 
# db.vision_image = vision.Image(content=db.image_data)
# db.vision_client = vision.ImageAnnotatorClient()

# For making REST calls to azure cognitive services
# We pass binary image data in body...
def get_cognitive_data(url, params, body):
    with requests.post(f"{db.creds['cognitive_services_uri']}{url}", data=body, params=params, 
            headers={
                'Content-Type': 'application/octet-stream', 
                "Ocp-Apim-Subscription-Key": db.creds["cognitive_services_key1"]
            }) as request:
        return request.json() 

# %%
pillow_image = Image.open(io.BytesIO(db.image_data)).convert("RGBA")
pillow_image.thumbnail((512, 512))
display.display(pillow_image)

# %%
# Bashing my head agains the wall... again... and again... the python client lib code is a tad hard to navigate and grok...
# so had to give up trying to retreive a bearer token from it... perchance query param api-key would work
def ohmy():
    print("=== Google Cloud Vision REST annotate endpoint:")
    body = {
        "requests": [
            {
                "image": { "content": base64.b64encode(db.image_data).decode() }, 
                "features": [
                    {"type": "LABEL_DETECTION", "maxResults": 3},
                    {"type": "FACE_DETECTION", "maxResults": 3},
                    {"type": "OBJECT_LOCALIZATION", "maxResults": 3},
                    # {"type": "TEXT_DETECTION", "maxResults": 3, "model": "builtin/latest"},
                    {"type": "TYPE_UNSPECIFIED", "maxResults": 4},
                    {"type": "LANDMARK_DETECTION", "maxResults": 3},
                    {"type": "LOGO_DETECTION", "maxResults": 3},
                    {"type": "SAFE_SEARCH_DETECTION", "maxResults": 3},
                    # {"type": "IMAGE_PROPERTIES", "maxResults": 3},
                    # {"type": "CROP_HINTS", "maxResults": 3},
                    # {"type": "WEB_DETECTION", "maxResults": 3},
                    # {"type": "PRODUCT_SEARCH", "maxResults": 3},
                ],
            }
        ]
    }

    with requests.post(db.creds["vision_annotate_url"], params={"key": db.creds["vision_api_key"]}, json=body) as r:
        responses = r.json()
        for response in responses['responses']:
            for annotation in response['faceAnnotations']:
                del annotation['landmarks']
        pprint.pprint(responses, compact=True, width=120)
ohmy()      

# # %%
# print("=== Google Cloud Vision Labels:")
# response = db.vision_client.label_detection(image=db.vision_image)
# print(response)

# # %%
# print('=== Google Cloud Vision Safe search:')
# response = db.vision_client.safe_search_detection(image=db.vision_image)
# print(response)

# # %%
# print('=== Google Cloud Vision Landmarks:')
# response = db.vision_client.landmark_detection(image=db.vision_image)
# print(response)
# landmarks = response.landmark_annotations

# for landmark in landmarks:
    # print(landmark.description)
    # for location in landmark.locations:
        # lat_lng = location.lat_lng
        # print('Latitude {}'.format(lat_lng.latitude))
        # print('Longitude {}'.format(lat_lng.longitude))

# # %%
# print('=== Google Cloud Vision Face Detection:')
# response = db.vision_client.face_detection(image=db.vision_image)

# pillow_image = Image.open(io.BytesIO(db.image_data)).convert("RGBA")
# image_draw = ImageDraw.Draw(pillow_image)
# for i, face in enumerate(response.face_annotations):
    # vertices = (['({},{})'.format(vertex.x, vertex.y) for vertex in face.bounding_poly.vertices]) 
    # print(f'Face #{i}, bounds: {", ".join(vertices)}')
    # print(face)
    # xs = list(map(lambda v: v.x, face.bounding_poly.vertices))
    # ys = list(map(lambda v: v.y, face.bounding_poly.vertices))
    # image_draw.rectangle((min(xs), min(ys), max(xs), max(ys)), outline=colors[i%len(colors)], width=3)
        
# from IPython import display
# pillow_image.thumbnail((512, 512))
# display.display(pillow_image)

# # for mark in face.landmarks:
# #     print(f'{mark.type_}({mark.position.x},{mark.position.y},{mark.position.z})')

# %%
print("=== Azure Cognitive Services - Face API: Detect")

params = {
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'age,smile,facialHair,glasses,emotion,hair,makeup,accessories',
    'recognitionModel': 'recognition_04',
    'returnRecognitionModel': 'true',
    'detectionModel': 'detection_01',
    'faceIdTimeToLive': '86400',
}

faces = get_cognitive_data("/face/v1.0/detect", params, db.image_data)
# faceLandmarks pollutes the output of pprint, let's drep em'
# for face in faces:
#     del face['faceLandmarks']
# pprint.pprint(faces)

pillow_image = Image.open(io.BytesIO(db.image_data)).convert("RGBA")
image_draw = ImageDraw.Draw(pillow_image)

for i, face in enumerate(faces):
    face_rectangle = face["faceRectangle"]
    text = f"\nFace {i}\n\tLocation: {face_rectangle}\n\tAge: {face['faceAttributes']['age']}\n\tEmotions: {face['faceAttributes']['emotion']}"
    print(text)
    image_draw.rectangle((face_rectangle['left'], face_rectangle['top'], 
            face_rectangle['left']+face_rectangle['width'], face_rectangle['top']+face_rectangle['height']), outline=colors[i%len(colors)], width=3)
    # image_draw.multiline_text((face_rectangle['left'], face_rectangle['top']), text, font=ImageFont.truetype("tahoma.ttf", size=48))

from IPython import display
pillow_image.thumbnail((512, 512))
display.display(pillow_image)

# %%
print("=== Azure Cognitive Services - Vision API: Describe")

params = {
    'maxCandidates': '3',
    'language': 'en',
    'model-version': 'latest',
}

data = get_cognitive_data("/vision/v3.2/describe", params, db.image_data)
pprint.pprint(data)

# %%
print("=== Azsure Cognitive Services - Vision API: Analyze")

params = {
    "visualFeatures": "Categories,Adult,Tags,Brands,Color,Description,Faces,ImageType,Objects",
    "details": "Celebrities,Landmarks",
    "language": "en",
    "model-version": "latest"
}

data = get_cognitive_data("/vision/v3.2/analyze", params, db.image_data)
pprint.pprint(data)


