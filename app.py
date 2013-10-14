# app.py

# import required libraries
import os
import ast
import requests
import json
from flask import Flask, render_template, request
import logging
from myconfig import *

# initialize Flask
app = Flask(__name__)

# return homepage if no parameters passed
@app.route('/')
def main_page():
	return render_template('index.html')

"""
Using ReKognition API for facial recognition
1. Add images to ReKognition (image + name)
2. Call image training procedure
3. Send image to ReKognition for recognition
4. Process result and allow/deny access to protected resources
"""

# add images to pool of authorized users
@app.route('/register', methods=['GET', 'POST'])
def train_images():
	# get vars
	name = request.form['name']
	urls_str = request.form['urls']
	urls = ast.literal_eval(urls_str)
	# add images to ReKognition (image + name)
	jobname = "face_add_[" + name + "]"
	i = len(urls)
	logging.warning(i)
	for url in urls:
		rk_add = {'api_key': rk_api_key, 'api_secret': rk_api_secret, 'jobs': jobname, 'urls': url}
		r = requests.post("http://rekognition.com/func/api/?", params = rk_add)
		logging.warning(r.text)
	# call image training procedure
	rk_train = {'api_key': rk_api_key, 'api_secret': rk_api_secret, 'jobs': 'face_train'}
	q = requests.post("http://rekognition.com/func/api/?", params = rk_train)
	return render_template('add.html')

# send image to ReKognition for recognition
@app.route('/login', methods=['GET', 'POST'])
def recognize_images():
	# get vars
	url_auth = request.form['url_auth']
	logging.warning('url_auth %s' % url_auth)
	rk_recognize = {'api_key': rk_api_key, 'api_secret': rk_api_secret, 'jobs': 'face_recognize', 'urls': url_auth}
	r = requests.post("http://rekognition.com/func/api/?", params = rk_recognize)
	# turn result into JSON object and parse
	raw_data = r.text
	data = json.loads(raw_data)
	confidence_str = data['face_detection'][0]['confidence']
	likeliness_str = data['face_detection'][0]['matches'][0]['score']
	likeliness = float(likeliness_str)
	confidence = float(confidence_str)
	logging.warning('%s likeliness that person is authorized' % likeliness)
	logging.warning('%s confidence in analysis' % confidence)
	# make sure confidence is reasonably high
	if confidence > 0.82:
		if likeliness > 0.65:
			return render_template('success.html')
		else:
			return render_template('failure.html')
	else:
		return render_template('failure.html')

# run app
if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

