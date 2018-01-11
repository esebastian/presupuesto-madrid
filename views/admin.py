# -*- coding: UTF-8 -*-

from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from coffin.shortcuts import render_to_response
from budget_app.views.helpers import *

# Don't forget: pip install beautifulsoup4
from bs4 import BeautifulSoup
import urllib

import os
import datetime
import subprocess
import glob
import re

@never_cache
def admin(request):
  return render_to_response('admin/index.html', get_context(request))


@never_cache
def admin_download(request):
  response = _get_response(request)

  # Get input parameters
  source_path = request.GET.get('source_path', '')
  if ( source_path=='' ):
    # If no URL is given, we have the 2017 page as default, at least for now
    source_path = 'http://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=b278b3e4a564c410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default'

  # Download the given page
  try:
    page = urllib.urlopen(source_path).read()
  except IOError, err:
    return _set_download_message(response, "IO ERROR: "+str(err))

  # Create the target folder
  temp_folder_path = _get_temp_folder()

  # Download the linked files
  doc = BeautifulSoup(page, "html.parser")
  files = doc.find_all('a', class_='ico-csv')
  _download_open_data_file(files[0], temp_folder_path, "ingresos.csv")
  _download_open_data_file(files[1], temp_folder_path, "gastos.csv")
  _download_open_data_file(files[2], temp_folder_path, "inversiones.csv")

  # Find out which year we're working with
  title = doc.find('h3', class_='summary-title').text
  match = re.compile('.*presupuestaria (\d+)$').match(title)
  year = match.group(1)
  _create_file(temp_folder_path, '.budget_year', year)

  # Keep track of the month of the data
  month = request.GET.get('month', '0')
  _create_file(temp_folder_path, '.budget_status', 'M'+month)

  # Return
  output = "Ficheros descargados de %s.<br/>Disponibles en %s." % (source_path, temp_folder_path)
  return _set_download_message(response, output)


@never_cache
def admin_load(request):
  response = _get_response(request)

  files = sorted(glob.glob(_get_temp_base_path()+"/*.*"))

  # FIXME: Copy files from temp location

  # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
  # FIXME: Year is hardcoded
  cmd = u"cd %s && export PYTHONIOENCODING=utf-8 && " \
          "python manage.py load_budget 2017 --language=es,en && " \
          "python manage.py load_investments 2017 --language=es,en" % (ROOT_PATH, )
  subprocess_output = []
  p = subprocess.Popen(args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  for byte_line in iter(p.stdout.readline, ''):
    line = byte_line.decode('utf8', errors='backslashreplace').replace('\r', '')
    subprocess_output.append(line)

  output = "Vamos a cargar los datos disponibles en %s.<br/>" \
            "Ejecutando: <pre>%s</pre>" \
            "Resultado: <pre>%s</pre>" % (files[-1], cmd, " ".join(subprocess_output))
  return _set_load_message(response, output)


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

def _create_file(output_folder, output_name, content):
  file = open(os.path.join(output_folder, output_name), "w")
  file.write(content)
  file.close()

def _set_download_message(response, message):
  response['download_output'] = message
  # How to return JSON, see https://stackoverflow.com/a/2428119
  return HttpResponse(json.dumps(response), content_type="application/json")

def _set_load_message(response, message):
  response['load_output'] = message
  return HttpResponse(json.dumps(response), content_type="application/json")

def _get_response(request):
  return {
    'download_output': '',
    'load_output': ''
  }