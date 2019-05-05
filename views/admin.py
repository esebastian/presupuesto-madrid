# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from coffin.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME_PATH

import base64
import datetime
import glob
import json
import os
import re
import shutil
import subprocess
import urllib


class AdminException(Exception):
    pass


# Main
@never_cache
def admin(request):
    return redirect("admin-inflation")


# General budget
@never_cache
def admin_general(request):
    context = {"title_prefix": _(u"Presupuesto general"), "active_tab": "general"}
    return render(request, "admin/general.html", context)


# Execution budget
@never_cache
def admin_execution(request):
    context = {"title_prefix": _(u"Ejecución mensual"), "active_tab": "execution"}
    return render(request, "admin/execution.html", context)


# Inflation
@never_cache
def admin_inflation(request):
    context = {"title_prefix": _(u"Inflación"), "active_tab": "inflation"}
    return render(request, "admin/inflation.html", context)


@never_cache
def admin_inflation_retrieve(request):
    body, status = _retrieve_inflation()
    return _csv_response(body, status)


@never_cache
def admin_inflation_save(request):
    content = _get_content(request.POST)
    body, status = _save_inflation(content)
    return _json_response(body, status)


@never_cache
def admin_inflation_load(request):
    body, status = _load_stats()
    return _json_response(body, status)


# Population
@never_cache
def admin_population(request):
    context = {"title_prefix": _(u"Población"), "active_tab": "population"}
    return render(request, "admin/population.html", context)


@never_cache
def admin_population_retrieve(request):
    body, status = _retrieve_population()
    return _csv_response(body, status)


@never_cache
def admin_population_save(request):
    content = _get_content(request.POST)
    body, status = _save_population(content)
    return _json_response(body, status)


@never_cache
def admin_population_load(request):
    body, status = _load_stats()
    return _json_response(body, status)


# Investments
@never_cache
def admin_investments(request):
    context = {"title_prefix": _(u"Inversiones"), "active_tab": "investments"}
    return render(request, "admin/investments.html", context)


# Third party payments
@never_cache
def admin_payments(request):
    context = {"title_prefix": _(u"Pagos a terceros"), "active_tab": "payments"}
    return render(request, "admin/payments.html", context)


# Glossary
@never_cache
def admin_glossary(request):
    return redirect("admin-glossary-es")


@never_cache
def admin_glossary_es(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return render(request, "admin/glossary_es.html", context)


@never_cache
def admin_glossary_es_retrieve(request):
    body, status = _retrieve_glossary_es()
    return _csv_response(body, status)


@never_cache
def admin_glossary_es_save(request):
    content = _get_content(request.POST)
    body, status = _save_glossary_es(content)
    return _json_response(body, status)


@never_cache
def admin_glossary_es_load(request):
    body, status = _load_glossary_es()
    return _json_response(body, status)


@never_cache
def admin_glossary_en(request):
    context = {"title_prefix": _(u"Glosario"), "active_tab": "glossary"}
    return render(request, "admin/glossary_en.html", context)


@never_cache
def admin_glossary_en_retrieve(request):
    body, status = _retrieve_glossary_en()
    return _csv_response(body, status)


@never_cache
def admin_glossary_en_save(request):
    content = _get_content(request.POST)
    body, status = _save_glossary_en(content)
    return _json_response(body, status)


@never_cache
def admin_glossary_en_load(request):
    body, status = _load_glossary_en()
    return _json_response(body, status)


# Old controllers
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
    subprocess_output, _ = _execute_cmd(cmd)

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
    subprocess_output, _ = _execute_cmd(cmd)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    output = (
        "Vamos a cargar los datos disponibles en %s.<br/>"
        "Ejecutando: <pre>%s</pre>"
        "Resultado: <pre>%s</pre>" % (data_files, cmd, subprocess_output)
    )
    return _set_load_message(response, output)


# Old helpers
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


# Actions
def _retrieve_inflation():
    return _retrieve("data/inflacion.csv")


def _retrieve_population():
    return _retrieve("data/poblacion.csv")


def _retrieve_glossary_es():
    return _retrieve("data/glosario_es.csv")


def _retrieve_glossary_en():
    return _retrieve("data/glosario_en.csv")


def _save_inflation(content):
    return _save("data/inflacion.csv", content, "Update inflation data")


def _save_population(content):
    return _save("data/poblacion.csv", content, "Update population data")


def _save_glossary_es(content):
    return _save("data/glosario_es.csv", content, "Update spanish glossary data")


def _save_glossary_en(content):
    return _save("data/glosario_en.csv", content, "Update english glossary data")


def _load_stats():
    return _execute("load_stats", u"Vamos a cargar los datos estadísticos")


def _load_glossary_es():
    return _execute("load_glossary --language=es", u"Vamos a cargar los datos del glosario en español")


def _load_glossary_en():
    return _execute("load_glossary --language=en", u"Vamos a cargar los datos del glosario en inglés")


# Action helpers
def _retrieve(file_path):
    try:
        body = _read(file_path)
        status = 200
        return (body, status)
    except AdminException as error:
        raise Exception(error)


def _save(file_path, content, commit_message):
    if not content:
        body = {"result": "error", "message": "Nada que guardar."}
        status = 400
        return (body, status)

    try:
        _write(file_path, content)
        _commit(file_path, commit_message)

        body = {"result": "success", "message": "Los datos se han guardado correctamente."}
        status = 200
    except AdminException:
        body = {"result": "error", "message": "Se ha producido un error guardando los datos."}
        status = 500

    return (body, status)


def _execute(management_command, cue):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && scripts/git fetch && scripts/git reset --hard origin/master && " % THEME_PATH
    cmd += "cd %s && python manage.py %s" % (ROOT_PATH, management_command)

    output, error = _execute_cmd(cmd)

    if error:
        message = "No se ha podido ejecutar el comando '%s'." % management_command
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    # Touch project/wsgi.py so the app restarts
    _touch_file(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>%s.</p>"
        "<p>Ejecutado: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cue, cmd, output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


# Filesystem helpers
def _touch_file(file_path):
    # The scripts/touch executable must be manually deployed and setuid'ed
    cmd = "cd %s && scripts/touch %s" % (THEME_PATH, file_path)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File '%s' couldn't be touched" % file_path)


def _read(file_path):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/git fetch "
        "&& scripts/git show origin/master:%s"
    ) % (THEME_PATH, file_path)

    output, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be read." % file_path)

    return output


def _write(file_path, content):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    # The scripts/cat executable must be manually deployed and setuid'ed
    cmd = (
        "export PYTHONIOENCODING=utf-8 "
        "&& cd %s "
        "&& cat <<EOF | scripts/tee %s\n"
        "%s"
        "\nEOF"
    ) % (THEME_PATH, file_path, content)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be written." % file_path)


def _commit(file_path, commit_message):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset origin/master "
        "&& scripts/git add %s "
        "&& scripts/git commit -m \"%s\n\nChange performed on the admin console.\" "
        "&& scripts/git push"
    ) % (THEME_PATH, file_path, commit_message)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be commited." % file_path)


# Utility helpers
def _get_content(params):
    content = params.get("content", "")
    return base64.b64decode(content)


def _execute_cmd(cmd):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)

    output, _ = process.communicate()
    return_code = process.poll()

    output = output.decode("utf8", "backslashreplace")
    error = return_code != 0

    return (output, error)


def _json_response(data, status=200):
    return HttpResponse(json.dumps(data), content_type="application/json; charset=utf-8", status=status)


def _csv_response(data, status=200):
    return HttpResponse(data, content_type="text/csv; charset=utf-8", status=status)
