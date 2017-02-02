from django.shortcuts import render
from django.http import HttpResponseBadRequest
from .crawler import crawl_mysnu
from graduate_adventure_sampler.settings import USERDATA_DIR
import os
import pickle
import hashlib
from datetime import datetime


def get_user_information(request):
    if request.method == 'GET':
        return render(request, 'index.html', {'error': False})

    if request.method != 'POST':
        return HttpResponseBadRequest()

    username = request.POST['username']
    password = request.POST['password']

    crawl_result = crawl_mysnu(username, password)

    if crawl_result is None:
        return render(request, 'index.html', {'error': True})

    date = datetime.now().strftime('%Y%m%d%H%M%S')
    hash_object = hashlib.sha256()
    hash_object.update(username.encode())
    file_path = os.path.join(USERDATA_DIR, date + '_' + hash_object.hexdigest()[:6] + '.pickle')

    with open(file_path, 'wb') as f:
        pickle.dump(crawl_result, f, protocol=pickle.HIGHEST_PROTOCOL)

    return render(request, 'result.html', {})
