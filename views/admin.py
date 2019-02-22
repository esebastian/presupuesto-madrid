# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from budget_app.views.helpers import get_context
from coffin.shortcuts import render_to_response, redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME, THEME_REPO, GITHUB_TOKEN
from time import time

import datetime
import glob
import json
import os
import re
import requests
import shutil
import subprocess
import urllib


@never_cache
def admin(request):
    return redirect('admin-inflation')


@never_cache
def admin_general(request):
    context = get_context(request, title=_(u'Presupuesto general'))
    context["active_tab"] = "general"
    return render_to_response("admin/general.html", context)


@never_cache
def admin_execution(request):
    context = get_context(request, title=_(u'Ejecución mensual'))
    context["active_tab"] = "execution"
    return render_to_response("admin/execution.html", context)


@never_cache
def admin_inflation(request):
    context = get_context(request, title=_(u'Inflación'))
    context["active_tab"] = "inflation"
    return render_to_response("admin/inflation.html", context)


@never_cache
def admin_inflation_retrieve(request):
    inflation_url = "https://raw.githubusercontent.com/%s/master/data/inflacion.csv?%s" % (THEME_REPO, time())
    response = requests.get(inflation_url)
    return _csv_response(response.text)


@never_cache
def admin_inflation_save(request):
    content = request.POST.get("content", "")
    if not content:
        response = {"result": "error", "message": "Nada que guardar."}
        return _json_response(response, status=400)

    api_token = GITHUB_TOKEN
    api_url = "https://api.github.com/repos/%s/contents/data/inflacion.csv" % THEME_REPO

    headers = {"Authorization": "token %s" % api_token}

    # Get the file SHA
    api_response = requests.get(api_url, headers=headers)

    if not api_response.ok:
        response = {"result": "error", "message": "Se ha producido un error guardando los datos."}
        return _json_response(response, status=400)

    # Update the file
    current_sha = api_response.json()["sha"]

    payload = {
        "message": "Update inflation data\n\nChange performed on the admin console.",
        "content": content,
        "sha": current_sha
    }

    api_response = requests.put(api_url, headers=headers, data=json.dumps(payload))

    if not api_response.ok:
        response = {"result": "error", "message": "Los datos no se ha podido guardar."}
        return _json_response(response, status=400)

    response = {"result": "success", "message": "Los datos se han guardado correctamente."}
    return _json_response(response)


@never_cache
def admin_inflation_load(request):
    # Pull and load the data
    core_path = ROOT_PATH
    theme_path = os.path.join(ROOT_PATH, THEME)

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && git pull && " % theme_path
    cmd += "cd %s && python manage.py load_stats" % core_path

    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>Vamos a cargar los datos estadísticos.</p>"
        "<p>Ejecutando: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cmd, " ".join(subprocess_output))
    )
    response = {"result": "success", "message": message}
    return _json_response(response)


@never_cache
def admin_population(request):
    context = get_context(request, title=_(u'Población'))
    context["active_tab"] = "population"
    return render_to_response("admin/population.html", context)


@never_cache
def admin_population_retrieve(request):
    population_url = "https://raw.githubusercontent.com/%s/master/data/poblacion.csv?%s" % (THEME_REPO, time())
    response = requests.get(population_url)
    return _csv_response(response.text)


@never_cache
def admin_population_save(request):
    content = request.POST.get("content", "")
    if not content:
        response = {"result": "error", "message": "Nada que guardar."}
        return _json_response(response, status=400)

    api_token = GITHUB_TOKEN
    api_url = "https://api.github.com/repos/%scontents/data/poblacion.csv" % THEME_REPO

    headers = {"Authorization": "token %s" % api_token}

    # Get the file SHA
    api_response = requests.get(api_url, headers=headers)

    if not api_response.ok:
        response = {"result": "error", "message": "Se ha producido un error guardando los datos."}
        return _json_response(response, status=400)

    # Update the file
    current_sha = api_response.json()["sha"]

    payload = {
        "message": "Update population data\n\nChange performed on the admin console.",
        "content": content,
        "sha": current_sha
    }

    api_response = requests.put(api_url, headers=headers, data=json.dumps(payload))

    if not api_response.ok:
        response = {"result": "error", "message": "Los datos no se ha podido guardar."}
        return _json_response(response, status=400)

    response = {"result": "success", "message": "Los datos se han guardado correctamente."}
    return _json_response(response)


@never_cache
def admin_population_load(request):
    # Pull and load the data
    core_path = ROOT_PATH
    theme_path = os.path.join(ROOT_PATH, THEME)

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && git pull && " % theme_path
    cmd += "cd %s && python manage.py load_stats" % core_path

    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>Vamos a cargar los datos estadísticos.</p>"
        "<p>Ejecutando: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cmd, " ".join(subprocess_output))
    )
    response = {"result": "success", "message": message}
    return _json_response(response)


@never_cache
def admin_payments(request):
    context = get_context(request, title=_(u'Pagos a terceros'))
    context["active_tab"] = "payments"
    return render_to_response("admin/payments.html", context)


@never_cache
def admin_glossary(request):
    return redirect('admin-glossary-es')


@never_cache
def admin_glossary_es(request):
    context = get_context(request, title=_(u'Glosario'))
    context["active_tab"] = "glossary"
    return render_to_response("admin/glossary_es.html", context)


@never_cache
def admin_glossary_es_retrieve(request):
    glossary_es_url = "https://raw.githubusercontent.com/%s/master/data/glosario_es.csv?%s" % (THEME_REPO, time())
    response = requests.get(glossary_es_url)
    return _csv_response(response.text)


@never_cache
def admin_glossary_es_save(request):
    content = request.POST.get("content", "")
    if not content:
        response = {"result": "error", "message": "Nada que guardar."}
        return _json_response(response, status=400)

    api_token = GITHUB_TOKEN
    api_url = "https://api.github.com/repos/%s/contents/data/glosario_es.csv" % THEME_REPO

    headers = {"Authorization": "token %s" % api_token}

    # Get the file SHA
    api_response = requests.get(api_url, headers=headers)

    if not api_response.ok:
        response = {"result": "error", "message": "Se ha producido un error guardando los datos."}
        return _json_response(response, status=400)

    # Update the file
    current_sha = api_response.json()["sha"]

    payload = {
        "message": "Update spanish glossary data\n\nChange performed on the admin console.",
        "content": content,
        "sha": current_sha
    }

    api_response = requests.put(api_url, headers=headers, data=json.dumps(payload))

    if not api_response.ok:
        response = {"result": "error", "message": "Los datos no se ha podido guardar."}
        return _json_response(response, status=400)

    response = {"result": "success", "message": "Los datos se han guardado correctamente."}
    return _json_response(response)


@never_cache
def admin_glossary_es_load(request):
    # Pull and load the data
    core_path = ROOT_PATH
    theme_path = os.path.join(ROOT_PATH, THEME)

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && git pull && " % theme_path
    cmd += "cd %s && python manage.py load_glossary --language=es" % core_path

    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>Vamos a cargar los datos del glosario en español.</p>"
        "<p>Ejecutando: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cmd, " ".join(subprocess_output))
    )
    response = {"result": "success", "message": message}
    return _json_response(response)


@never_cache
def admin_glossary_en(request):
    context = get_context(request, title=_(u'Glosario'))
    context["active_tab"] = "glossary"
    return render_to_response("admin/glossary_en.html", context)


@never_cache
def admin_glossary_en_retrieve(request):
    glossary_en_url = "https://raw.githubusercontent.com/%s/master/data/glosario_en.csv?%s" % (THEME_REPO, time())
    response = requests.get(glossary_en_url)
    return _csv_response(response.text)


@never_cache
def admin_glossary_en_save(request):
    content = request.POST.get("content", "")
    if not content:
        response = {"result": "error", "message": "Nada que guardar."}
        return _json_response(response, status=400)

    api_token = GITHUB_TOKEN
    api_url = "https://api.github.com/repos/%s/contents/data/glosario_en.csv" % THEME_REPO

    headers = {"Authorization": "token %s" % api_token}

    # Get the file SHA
    api_response = requests.get(api_url, headers=headers)

    if not api_response.ok:
        response = {"result": "error", "message": "Se ha producido un error guardando los datos."}
        return _json_response(response, status=400)

    # Update the file
    current_sha = api_response.json()["sha"]

    payload = {
        "message": "Update english glossary data\n\nChange performed on the admin console.",
        "content": content,
        "sha": current_sha
    }

    api_response = requests.put(api_url, headers=headers, data=json.dumps(payload))

    if not api_response.ok:
        response = {"result": "error", "message": "Los datos no se ha podido guardar."}
        return _json_response(response, status=400)

    response = {"result": "success", "message": "Los datos se han guardado correctamente."}
    return _json_response(response)


@never_cache
def admin_glossary_en_load(request):
    # Pull and load the data
    core_path = ROOT_PATH
    theme_path = os.path.join(ROOT_PATH, THEME)

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && git pull && " % theme_path
    cmd += "cd %s && python manage.py load_glossary --language=en" % core_path

    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>Vamos a cargar los datos del glosario en inglés.</p>"
        "<p>Ejecutando: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cmd, " ".join(subprocess_output))
    )
    response = {"result": "success", "message": message}
    return _json_response(response)


@never_cache
def admin_save(request):
    response = _get_response(request)

    content = request.POST.get("content", "")
    if not content:
        return _set_download_message(response, "No content to save")

    file_path = request.GET.get("file_path", "")
    if not file_path:
        return _set_download_message(response, "No file path provided")

    api_token = GITHUB_TOKEN
    api_url = "https://api.github.com/repos/%s/contents/%s" % (THEME_REPO, file_path)

    headers = {"Authorization": "token %s" % api_token}

    api_response = requests.get(api_url, headers=headers)

    if not response.ok:
        return _set_download_message(response, "The file couldn't be saved")

    current_sha = api_response.json["sha"]

    payload = {
        "message": "File %s updated from admin console" % file_path,
        "content": content,
        "sha": current_sha
    }

    api_response = requests.put(api_url, headers=headers, data=json.dumps(payload))

    if not response.ok:
        return _set_download_message(response, "The file couldn't be saved")

    output = "Ficheros %s correctamente guardado." % file_path

    return _set_save_message(response, output)


@never_cache
def admin_download(request):
    response = _get_response(request)

    # Get input parameters
    source_path = request.GET.get("source_path", "")
    if source_path == "":
        # If no URL is given, we have the current annuality page as default
        source_path = "https://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=b278b3e4a564c410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default"

    # Download the given page
    try:
        page = urllib.urlopen(source_path).read()
    except IOError as err:
        return _set_download_message(response, "IO ERROR: " + str(err))

    # Create the target folder
    temp_folder_path = _get_temp_folder()

    # Download the linked files
    doc = BeautifulSoup(page, "html.parser")
    files = doc.find_all("a", class_="ico-csv")
    _download_open_data_file(files[0], temp_folder_path, "ingresos.csv")
    _download_open_data_file(files[1], temp_folder_path, "gastos.csv")
    _download_open_data_file(files[2], temp_folder_path, "inversiones.csv")

    # Find out which year we're working with
    title = doc.find("h3", class_="summary-title").text
    match = re.compile(r".*presupuestaria (\d+)$").match(title)
    year = match.group(1)
    _create_file(temp_folder_path, ".budget_year", year)

    # Keep track of the month of the data
    month = request.GET.get("month", "0")
    status = (
        month + "M" if month != "12" else ""
    )  # 12M means the year is fully executed
    _create_file(temp_folder_path, ".budget_status", status)

    # Return
    output = "Ficheros descargados de %s.<br/>Disponibles en %s." % (
        source_path,
        temp_folder_path,
    )
    return _set_download_message(response, output)


@never_cache
def admin_review(request):
    response = _get_response(request)

    # Pick up the most recent downloaded files
    data_files = _get_most_recent_files_in_temp_folder()

    # Execute a helper script to check the data files
    script_path = os.path.join(ROOT_PATH, THEME, "loaders")
    cmd = u"cd %s && export PYTHONIOENCODING=utf-8 && " % (script_path,)
    cmd += "python madrid_check_datafiles.py " + data_files
    subprocess_output = _execute_cmd(cmd)

    # Return
    output = (
        "Revisando los datos disponibles en %s.<br/>"
        "Resultado: <pre>%s</pre>" % (data_files, " ".join(subprocess_output))
    )
    return _set_review_message(response, output)


@never_cache
def admin_load(request):
    response = _get_response(request)

    # Pick up the most recent downloaded files
    data_files = _get_most_recent_files_in_temp_folder()

    # Read the year of the budget data
    year = _read_file(data_files, ".budget_year")

    # Copy downloaded files to the theme destination
    _copy_downloaded_files_to_theme(data_files, year, "es")
    _copy_downloaded_files_to_theme(data_files, year, "en")

    # Load the data
    cmd = u"cd %s && export PYTHONIOENCODING=utf-8 && " % (ROOT_PATH,)
    cmd += "python manage.py load_budget " + year + " --language=es,en && "
    cmd += "python manage.py load_investments " + year + " --language=es,en"
    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    output = (
        "Vamos a cargar los datos disponibles en %s.<br/>"
        "Ejecutando: <pre>%s</pre>"
        "Resultado: <pre>%s</pre>" % (data_files, cmd, " ".join(subprocess_output))
    )
    return _set_load_message(response, output)


def _get_temp_base_path():
    return "/tmp/budget_app"


def _get_temp_folder():
    base_path = _get_temp_base_path()
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    temp_folder_path = os.path.join(base_path, str(datetime.datetime.now().isoformat()))
    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)

    return temp_folder_path


def _get_most_recent_files_in_temp_folder():
    return sorted(glob.glob(_get_temp_base_path() + "/*.*"))[-1]


def _download_open_data_file(link, output_folder, output_name):
    file_href = "http://datos.madrid.es" + link["href"]
    urllib.urlretrieve(file_href, os.path.join(output_folder, output_name))


def _copy_downloaded_files_to_theme(data_files, year, language):
    target_path = os.path.join(
        ROOT_PATH, THEME, "data", language, "municipio", year
    )
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    shutil.copy(
        os.path.join(data_files, ".budget_status"),
        os.path.join(target_path, ".budget_status"),
    )
    shutil.copy(
        os.path.join(data_files, "gastos.csv"), os.path.join(target_path, "gastos.csv")
    )
    shutil.copy(
        os.path.join(data_files, "gastos.csv"),
        os.path.join(target_path, "ejecucion_gastos.csv"),
    )
    shutil.copy(
        os.path.join(data_files, "ingresos.csv"),
        os.path.join(target_path, "ingresos.csv"),
    )
    shutil.copy(
        os.path.join(data_files, "ingresos.csv"),
        os.path.join(target_path, "ejecucion_ingresos.csv"),
    )
    shutil.copy(
        os.path.join(data_files, "inversiones.csv"),
        os.path.join(target_path, "inversiones.csv"),
    )
    shutil.copy(
        os.path.join(data_files, "inversiones.csv"),
        os.path.join(target_path, "ejecucion_inversiones.csv"),
    )


def _create_file(output_folder, output_name, content):
    with open(os.path.join(output_folder, output_name), "w") as file:
        file.write(content)


def _read_file(output_folder, output_name):
    with open(os.path.join(output_folder, output_name), "r") as file:
        return file.read()


def _touch_file(fname, times=None):
    # Taken from https://stackoverflow.com/a/1160227
    with open(fname, "a"):
        os.utime(fname, times)


def _execute_cmd(cmd):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    subprocess_output = []

    p = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )

    for byte_line in iter(p.stdout.readline, ""):
        line = byte_line.decode("utf8", errors="backslashreplace").replace(r"\r", "")
        subprocess_output.append(line)

    return subprocess_output


def _set_save_message(response, message):
    response["save_output"] = message
    # How to return JSON, see https://stackoverflow.com/a/2428119
    return HttpResponse(json.dumps(response), content_type="application/json")


def _set_download_message(response, message):
    response["download_output"] = message
    # How to return JSON, see https://stackoverflow.com/a/2428119
    return HttpResponse(json.dumps(response), content_type="application/json")


def _set_review_message(response, message):
    response["review_output"] = message
    return HttpResponse(json.dumps(response), content_type="application/json")


def _set_load_message(response, message):
    response["load_output"] = message
    return HttpResponse(json.dumps(response), content_type="application/json")


def _get_response(request):
    return {"download_output": "", "review_output": "", "load_output": ""}


def _json_response(data, status=200):
    return HttpResponse(json.dumps(data), content_type="application/json; charset=utf-8", status=status)


def _csv_response(data):
    return HttpResponse(data, content_type="text/csv; charset=utf-8")
