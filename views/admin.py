# -*- coding: UTF-8 -*-

from django.views.decorators.cache import never_cache
from coffin.shortcuts import render_to_response
from budget_app.views.helpers import *

# Don't forget: pip install beautifulsoup4
from bs4 import BeautifulSoup
import urllib

import os
import datetime
import glob

@never_cache
def admin(request):
  c = _get_context(request)

  c['output'] = glob.glob(ROOT_PATH+"/*.*")

  return render_to_response('admin/index.html', c)


@never_cache
def admin_download(request):
  c = _get_context(request)

  # Get input parameters
  source_path = request.GET.get('source_path', '')
  if ( source_path=='' ):   # FIXME: Temporary
    source_path = 'http://datos.madrid.es/sites/v/index.jsp?vgnextoid=af62db13cb659410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD'

  # Download the given page
  try:
    page = urllib.urlopen(source_path).read()
  except IOError, err:
    return _set_download_message(c, "IO ERROR: "+str(err))

  # Create the target folder
  temp_folder_path = _get_temp_folder()

  # Download the linked files
  doc = BeautifulSoup(page, "html.parser")
  files = doc.find_all('a', class_='ico-csv')
  _download_open_data_file(files[0], temp_folder_path, "ingresos.csv")
  _download_open_data_file(files[1], temp_folder_path, "gastos.csv")
  _download_open_data_file(files[2], temp_folder_path, "inversiones.csv")

  # Return
  message = "Ficheros descargados de %s.<br/>Disponibles en %s." % (source_path, temp_folder_path)
  return _set_download_message(c, message)


def _get_temp_folder():
  base_path = '/tmp/budget_app'
  if not os.path.exists(base_path):
    os.makedirs(base_path)

  temp_folder_path = os.path.join(base_path, str(datetime.datetime.now().isoformat()))
  if not os.path.exists(temp_folder_path):
    os.makedirs(temp_folder_path)

  return temp_folder_path

def _download_open_data_file(link, output_folder, output_name):
  file_href = 'http://datos.madrid.es'+link['href']
  urllib.urlretrieve(file_href, os.path.join(output_folder, output_name))

def _set_download_message(c, message):
  c['download_output'] = message
  return render_to_response('admin/response.json', c, content_type="application/json")

def _get_context(request):
  c = get_context(request)
  c['load_output'] = ''
  return c