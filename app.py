from flask import Flask, request, jsonify, Response

#-------- Modules -------#


import json
import sys


import qdrant_access as qd

app = Flask(__name__)

@app.route('/images')
def get_pages(methods = ['GET']):
    search = request.args.get('search', "luftsprang")
    hits = request.args.get('hits', 20)
    res = qd.search_images_fulltext(search, hits)
    
    return jsonify(res)

@app.route('/sim_images')
def get_images(methods = ['GET']):
    search = request.args.get('image_url')
    hits = request.args.get('limit', 20)
    collection_name = request.args.get('collection_name', "images_1900_cos")
    res = qd.find_similar_images(qd.client, search, collection_name=collection_name, limit = hits)
    
    return jsonify(res)

@app.route('/sim_words')
def get_words(methods = ['GET']):
    search = request.args.get('word')
    hits = request.args.get('limit', 20)
    collection_name = request.args.get('collection_name', "vss_1850_cos")
    res = qd.find_similar_words(qd.client, search, collection_name=collection_name, limit = hits)
    
    return jsonify(res)

@app.route('/collections')
def get_collections(methods = ['GET']):
    res = qd.show_collections(qd.client)
    
    return Response(res, mimetype='text/plain')

