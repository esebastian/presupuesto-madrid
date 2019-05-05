# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from coffin.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME_PATH, THEME_REPO, GITHUB_TOKEN

import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import urllib
import urllib2


@never_cache
def admin(request):
    return redirect("admin-inflation")


@never_cache
def admin_general(request):
    context = {"title_prefix": _(u"Presupuesto general"), "active_tab": "general"}
    return render(request, "admin/general.html", context)


@never_cache
def admin_execution(request):
    context = {"title_prefix": _(u"Ejecución mensual"), "active_tab": "execution"}
    return render(request, "admin/execution.html", context)


@never_cache
def admin_inflation(request):
    context = {"title_prefix": _(u"Inflación"), "active_tab": "inflation"}
    return render(request, "admin/inflation.html", context)


@never_cache
def admin_inflation_retrieve(request):
    body = _read("data/inflacion.csv")
    return _csv_response(body)


@never_cache
def admin_inflation_save(request):
    content = request.POST.get("content", "")
    body, status = _update("data/inflacion.csv", content, "Update inflation data")
    return _json_response(body, status)


@never_cache
def admin_inflation_load(request):
    body, status = _load_stats(u"Vamos a cargar los datos estadísticos")
    return _json_response(body, status)


@never_cache
def admin_population(request):
    context = {"title_prefix": _(u"Población"), "active_tab": "population"}
    return render(request, "admin/population.html", context)


@never_cache
def admin_population_retrieve(request):
    body = _read("data/poblacion.csv")
    return _csv_response(body)


@never_cache
def admin_population_save(request):
    content = request.POST.get("content", "")
    body, status = _update("data/poblacion.csv", content, "Update population data")
    return _json_response(body, status)


@never_cache
def admin_population_load(request):
    body, status = _load_stats(u"Vamos a cargar los datos estadísticos")
    return _json_response(body, status)


@never_cache
def admin_payments(request):
    context = {"title_prefix": _(u"Pagos a terceros"), "active_tab": "payments"}
    return render(request, "admin/payments.html", context)


@never_cache
def admin_glossary(request):
    return redirect("admin-glossary-es")


@never_cache
def admin_glossary_es(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return render(request, "admin/glossary_es.html", context)


@never_cache
def admin_glossary_es_retrieve(request):
    body = _read("data/glosario_es.csv")
    return _csv_response(body)


@never_cache
def admin_glossary_es_save(request):
    content = request.POST.get("content", "")
    body, status = _update(
        "data/glosario_es.csv", content, "Update spanish glossary data"
    )
    return _json_response(body, status)


@never_cache
def admin_glossary_es_load(request):
    body, status = _load_glossary_es(u"Vamos a cargar los datos del glosario en español")
    return _json_response(body, status)


@never_cache
def admin_glossary_en(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return render(request, "admin/glossary_en.html", context)


@never_cache
def admin_glossary_en_retrieve(request):
    body = _read("data/glosario_en.csv")
    return _csv_response(body)


@never_cache
def admin_glossary_en_save(request):
    content = request.POST.get("content", "")
    body, status = _update(
        "data/glosario_en.csv", content, "Update english glossary data"
    )
    return _json_response(body, status)


@never_cache
def admin_glossary_en_load(request):
    body, status = _load_glossary_en(u"Vamos a cargar los datos del glosario en inglés")
    return _json_response(body, status)


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
    script_path = os.path.join(THEME_PATH, "loaders")
    cmd = u"cd %s && export PYTHONIOENCODING=utf-8 && " % (script_path,)
    cmd += "python madrid_check_datafiles.py " + data_files
    subprocess_output = _execute_cmd(cmd)

    # Return
    output = (
        "Revisando los datos disponibles en %s.<br/>"
        "Resultado: <pre>%s</pre>" % (data_files, subprocess_output)
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
        "Resultado: <pre>%s</pre>" % (data_files, cmd, subprocess_output)
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
    target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)
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


def _touch_file(file_path):
    # The scripts/touch executable must be manually deployed and setuid'ed
    cmd = "cd %s && scripts/touch %s" % (THEME_PATH, file_path)

    _execute_cmd(cmd)


def _execute_cmd(cmd):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    subprocess_output = []

    p = subprocess.Popen(
        args=cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )

    for byte_line in iter(p.stdout.readline, ""):
        line = byte_line.decode("utf8", "backslashreplace").replace(r"\r", "")
        subprocess_output.append(line)

    return "".join(subprocess_output)


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


def _load_stats(cue):
    return _execute("load_stats", cue)


def _load_glossary_es(cue):
    return _execute("load_glossary --language=es", cue)


def _load_glossary_en(cue):
    return _execute("load_glossary --language=en", cue)


def _read(file_path):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/git fetch"
        "&& scripts/git show origin/master:%s "
    ) % (THEME_PATH, file_path)

    subprocess_output = _execute_cmd(cmd)

    return subprocess_output


def _update(file_path, content, message):
    if not content:
        body = {"result": "error", "message": "Nada que guardar."}
        status = 400
        return (body, status)

    url = "https://api.github.com/repos/%s/contents/%s" % (THEME_REPO, file_path)
    headers = {"Authorization": "token %s" % GITHUB_TOKEN}

    # Get the file SHA
    response = __get(url, headers=headers)

    if not response["status"] == 200:
        body = {
            "result": "error",
            "message": "Se ha producido un error guardando los datos.",
        }
        status = 400
        return (body, status)

    # Update the file
    current_sha = json.loads(response["body"])["sha"]

    payload = {
        "message": "%s\n\nChange performed on the admin console." % message,
        "content": content,
        "sha": current_sha,
    }

    response = __put(url, headers=headers, data=payload)

    if not response["status"] == 200:
        body = {"result": "error", "message": "Los datos no se ha podido guardar."}
        status = 400
        return (body, status)

    body = {"result": "success", "message": "Los datos se han guardado correctamente."}
    status = 200
    return (body, status)


def _execute(management_command, cue):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && scripts/git fetch && scripts/git reset --hard origin/master && " % THEME_PATH
    cmd += "cd %s && python manage.py %s" % (ROOT_PATH, management_command)

    subprocess_output = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>%s.</p>"
        "<p>Ejecutando: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cue, cmd, subprocess_output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


def __get(url, headers={}):
    # The scripts/curl executable must be manually deployed and setuid'ed
    cmd = "cd %s && scripts/curl -L" % THEME_PATH

    for header, value in headers.items():
        cmd += " -H %s: %s" % (header, value)

    cmd += " %s" % url

    subprocess_output = _execute_cmd(cmd)

    status = 200
    body = subprocess_output

    return {"body": body, "status": status}


def __put(url, headers={}, data={}):
    opener = urllib2.build_opener(urllib2.HTTPHandler)
    request = urllib2.Request(url, data=json.dumps(data))

    for header, value in headers.items():
        request.add_header(header, value)

    request.get_method = lambda: "PUT"

    response = opener.open(request)

    status = response.getcode()
    body = response.read()

    return {"body": body, "status": status}


def _json_response(data, status=200):
    return HttpResponse(
        json.dumps(data), content_type="application/json; charset=utf-8", status=status
    )


def _csv_response(data):
    return HttpResponse(data, content_type="text/csv; charset=utf-8")
