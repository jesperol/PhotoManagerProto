# %%
# === Initializing...
import io, sys, json, pprint, requests, base64
from PIL import Image, ImageDraw, ImageOps
from IPython import display

# Rerun to reset filename and present dialog
image_file_name = ''
def select_image_file():
    from tkinter import Tk     # from tkinter import Tk for Python 3.x
    from tkinter.filedialog import askopenfilename

    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(filetypes=(("Jpeg", "*.jpg"),)) # show an "Open" dialog box and return the path to the selected file
    return filename or sys.exit(1)

# Damnit, FIX:
class Db: pass
db = Db()

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

db.pillow_image = Image.open(io.BytesIO(db.image_data)).convert("RGBA")

# For making REST calls to azure cognitive services
# We pass binary image data in body...
def get_cognitive_data(url, params, body):
    with requests.post("{0}{1}".format(db.creds['cognitive_services_uri'], url), data=body, params=params, 
            headers={
                'Content-Type': 'application/octet-stream', 
                "Ocp-Apim-Subscription-Key": db.creds["cognitive_services_key1"]
            }) as request:
        return request.json() 


# %%
# === Just display a scaled version of the image...
display.display(ImageOps.contain(ImageOps.exif_transpose(db.pillow_image), (512, 512)))


# %%
# === Google Cloud Vision REST annotate endpoint:

# Wants base64 encoded image data in requests.image.content...
body = {
    "requests": [
        {
            "image": { "content": base64.b64encode(db.image_data).decode() }, 
            "features": [
                # {"type": "LABEL_DETECTION"},
                {"type": "FACE_DETECTION", "model": "builtin/latest"},
                # {"type": "OBJECT_LOCALIZATION"},
                # {"type": "TEXT_DETECTION", "model": "builtin/latest"},
                {"type": "TYPE_UNSPECIFIED", "model": "builtin/latest"},
                {"type": "LANDMARK_DETECTION", "model": "builtin/latest"},
                {"type": "LOGO_DETECTION", "model": "builtin/latest"},
                {"type": "SAFE_SEARCH_DETECTION", "model": "builtin/latest"},
                # {"type": "IMAGE_PROPERTIES"},
                # {"type": "CROP_HINTS"},
                {"type": "WEB_DETECTION", "model": "builtin/latest"},
                {"type": "PRODUCT_SEARCH", "model": "builtin/latest"},
            ],
        }
    ]
}

params = { 
    # "fields": "responses(faceAnnotations,safeSearchAnnotation,webDetection(bestGuessLabels,webEntities))",
    "key": db.creds["vision_api_key"]
}

with requests.post(db.creds["vision_annotate_url"], params=params, json=body) as r:
    responses = r.json()
    for response in responses['responses']:
        for annotation in response['faceAnnotations']:
            del annotation['landmarks']
        del response['webDetection']['visuallySimilarImages']

pprint.pprint(responses, compact=True, width=120)

pillow_image_copy = db.pillow_image.copy()
image_draw = ImageDraw.Draw(pillow_image_copy)
for i, face in enumerate(responses['responses'][0]['faceAnnotations']):
    vertices = face['fdBoundingPoly']['vertices']
    try:
        image_draw.rectangle(xy=(vertices[0]['x'], vertices[0]['y'], vertices[2]['x'], vertices[2]['y']),
            outline=colors[i%len(colors)], width=5)
    except KeyError as e:
        print(e)

display.display(ImageOps.contain(pillow_image_copy, (1024, 1024)))


# %%
# === Azure Cognitive Services - Face API: Detect

params = {
    # Request parameters
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'true',
    'returnFaceAttributes': 'accessories,age,blur,emotion,exposure,facialhair,gender,glasses,hair,headpose,makeup,noise,occlusion,qualityforrecognition,smile',
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

# Detect endpoint will return transposed rectangle coordinates, so let's transpose the image before drawing 
pillow_image_copy = ImageOps.exif_transpose(db.pillow_image)
image_draw = ImageDraw.Draw(pillow_image_copy)

for i, face in enumerate(faces):
    face_rectangle = face["faceRectangle"]
    text = f"\nFace {i}\n\tLocation: {face_rectangle}\n\tAge: {face['faceAttributes']['age']}\n\tGlasses: {face['faceAttributes']['glasses']}\n\t"
    text += f"Gender: {face['faceAttributes']['gender']}\n\tEmotions: {face['faceAttributes']['emotion']}"
    print(text)
    image_draw.rectangle((face_rectangle['left'], face_rectangle['top'], 
            face_rectangle['left']+face_rectangle['width'], face_rectangle['top']+face_rectangle['height']), outline=colors[i%len(colors)], width=5)
    # image_draw.multiline_text((face_rectangle['left'], face_rectangle['top']), text, font=ImageFont.truetype("tahoma.ttf", size=48))

# Vision endpont does not return transposed face rectangles, so transpose after drawing
display.display(ImageOps.exif_transpose(ImageOps.contain(pillow_image_copy, (1024, 1024))))


# %%
# === Azure Cognitive Services - Vision API: Describe

params = {
    'language': 'en',
    'model-version': 'latest',
}

data = get_cognitive_data("/vision/v3.2/describe", params, db.image_data)
pprint.pprint(data)


# %%
# === Azure Cognitive Services - Vision API: Analyze

params = {
    "visualFeatures": "Categories,Adult,Tags,Brands,Color,Description,Faces,ImageType,Objects",
    "details": "Celebrities,Landmarks",
    "language": "en",
    "model-version": "latest"
}

data = get_cognitive_data("/vision/v3.2/analyze", params, db.image_data)
pprint.pprint(data)