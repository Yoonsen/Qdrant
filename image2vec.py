
from PIL import Image
#from image_embeddings.create_index import VectorDB
from pathlib import Path
import requests
import re
import json
import torch
import clip
import torch


# Load the model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)




def fetch_meta(url):
    pattern = r"([a-fA-F0-9]{32})|(URN:[^?&\s]+)"
    matches = re.findall(pattern, url)
    match = ""
    if matches != []:
        match = matches[0]
        if match[0] == '':
            match = match[1]
        else:
            match = match[0]
    i3f = requests.get(f"https://api.nb.no/catalog/v1/iiif/{match}/manifest?fields=metadata&profile=wwwnbno")
    iiif = "{}"
    if i3f.status_code == 200:
        iiif = i3f.json()['metadata']
    else:
        print(i3f.status_code, match, matches)
    return iiif


def encode_image(image):

    # Preprocess the image
    preprocessed_image = preprocess(image).unsqueeze(0).to(device)

    # Encode the image to get the feature vector
    with torch.no_grad():
        image_features = model.encode_image(preprocessed_image)
        
        # Normalize the feature vector
        image_features /= image_features.norm(dim=-1, keepdim=True)
    
    return image_features.cpu().numpy()
    
# Normalize feature vector
def normalize_feature_vector(feature_vector):
    norm = torch.norm(feature_vector, p=2, dim=-1, keepdim=True)
    normalized_feature_vector = feature_vector.div(norm)
    return normalized_feature_vector


def foto_url(nb_url):
    """Fetch the URN from url and return resolver address - in small"""
    new_url = re.findall('URN[^/"\'?&\s]+', nb_url)[0] 
    image_url = f"https://www.nb.no/services/image/resolver/{new_url}/full/!224,224/0/default.jpg"
    return image_url


# #def image2vec(image, clip_features = CLIPFeatureExtractor()):
#     if image.mode != 'RGB':
#         image = image.convert('RGB')
#     vec = clip_features(image)
#     return vec

def load_picture(url):
    """Load image using PIL"""
    r = requests.get(url, stream=True)
    res = "0"
    if r.status_code == 200:
        r.raw.decode_content=True
        res = r.raw
    return {'status':r.status_code, 'result':res, 'url':url}