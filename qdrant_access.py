from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from qdrant_client.http import models

from qdrant_client import QdrantClient
from qdrant_client.http.models import (CollectionDescription, 
VectorParams, 
Distance, Filter, FieldCondition, Match, PointRequest, MatchValue)

import re
import requests

client = QdrantClient(host="sprakbankdb1.lx.nb.no", port=6333)


#collection_name = "images_1900_cos"

def fetch_meta(url):
    pattern = r"""([a-fA-F0-9]{32})|(URN:[^?/&\s'"]+)"""
    matches = re.findall(pattern, url)
    match = ""
    if matches != []:
        match = matches[0]
        if match[0] == '':
            match = match[1]
        else:
            match = match[0]
    i3f = requests.get(f"https://api.nb.no/catalog/v1/iiif/{match}/manifest")
    iiif = "{}"
    if i3f.status_code == 200:
        iiif = i3f.json()['metadata']
    else:
        print(i3f.status_code)
    return iiif, match
    
def find_similar_images_by_vector(client, vector=None, collection_name=None, num=20):
    """supply a vector e.g. from vector = iv.encode_image(image) from iv module"""
    hits = client.search(
       collection_name = collection_name,
       query_vector = vector,
       limit = num  # 
    )
    return [x.payload['url'] for x in hits]

def find_similar_words(client, search_word, collection_name=None, limit=10):
    """Search a word using a client"""
    payload_filter = Filter(
        must=[
            FieldCondition(
                key='word',  # Ensure this is the correct key name in your payload
                match={"value": search_word}         
            )
        ]
    )
    response = client.scroll(
    
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(key="word", match=models.MatchValue(value=search_word)),
            ]
        ),
        limit=1,
        with_payload=True,
        with_vectors=True,
    
        collection_name=collection_name,
        
    )
    r = response[0][0]
    #print(r)
    # Check if the word exists in the collection and fetch its vector
    if r:
        word_vector = r.vector
    
        # Step 2: Perform a similarity search with the fetched vector
        similar_words_response = client.search(
            collection_name=collection_name,
            query_vector=word_vector,
            #search_params=SearchParams(k=10),  # Adjust 'k' to change the number of similar words to find
            limit=limit  # Adjust limit to change the number of results returned
        )
    
        # Print the similar words found
        #print(similar_words_response)
        
        
        result = [(hit.payload['word'], hit.score) for hit in similar_words_response]
    else:
        result = []
    return result

def find_images_by_identifier(client, identifier, collection_name=None, key="url"):
    """key takes the values "urn" (page urn) or "url" completed access"""
    # Construct the filter for the search query
    payload_filter = Filter(
        must=[
            FieldCondition(
                key=key,  # Ensure this is the correct key name in your payload
                match={"value": identifier}         
            )
        ]
    )
    
    # Perform the search
    search_results = client.scroll(
        collection_name=collection_name,
        scroll_filter=payload_filter,
        limit=100  # Adjust the limit based on how many results you expect
    )
    
    # Output the results
    records, _ = search_results
    return [x.payload['url'] for x in records]

def show_collections(client):
    """List all the collections in qdrant database"""
    collections = client.get_collections()
    return [collection.name for collection in collections.collections]