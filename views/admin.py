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
  output = "Ficheros descargados de %s.<br/>Disponibles en %s." % (source_path, temp_folder_path)
  return _set_download_message(c, output)


@never_cache
def admin_load(request):
  c = _get_context(request)

  files = sorted(glob.glob(_get_temp_base_path()+"/*.*"))
  output = "Vamos a cargar los datos disponibles en %s." % (files[-1], )
  return _set_load_message(c, output)


def _get_temp_base_path():
  return '/tmp/budget_app'

def _get_temp_folder():
  base_path = _get_temp_base_path()
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

def _set_load_message(c, message):
  c['load_output'] = message
  return render_to_response('admin/response.json', c, content_type="application/json")

def _get_context(request):
  c = get_context(request)
  c['download_output'] = ''
  c['load_output'] = ''
  return c