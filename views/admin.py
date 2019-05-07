# -*- coding: UTF-8 -*-

from bs4 import BeautifulSoup
from coffin.shortcuts import render, redirect
from datetime import datetime
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from project.settings import ROOT_PATH, THEME_PATH, HTTPS_PROXY, HTTP_PROXY

import base64
import glob
import json
import os
import subprocess
import urllib


EXECUTION_URL = {
    2019: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=93bf1b7ba1939610VgnVCM2000001f4a900aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD",
    2018: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=b278b3e4a564c410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD",
    2017: "https://datos.madrid.es/sites/v/index.jsp?vgnextoid=b404f67f5b35b410VgnVCM2000000c205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD"
}

TEMP_BASE_PATH = "/tmp/budget_app"


class AdminException(Exception):
    pass


# Main
@never_cache
def admin(request):
    return redirect("admin-execution")


# General budget
@never_cache
def admin_general(request):
    context = {"title_prefix": _(u"Presupuesto general"), "active_tab": "general"}
    return render(request, "admin/general.html", context)


# Execution
@never_cache
def admin_execution(request):
    current_year = datetime.today().year
    previous_years = [year for year in range(2011, current_year)]

    context = {
        "title_prefix": _(u"Ejecución mensual"),
        "active_tab": "execution",
        "current_year": current_year,
        "previous_years": previous_years
    }

    return render(request, "admin/execution.html", context)


@never_cache
def admin_execution_retrieve(request):
    month = _get_month(request.GET)
    year = _get_year(request.GET)
    body, status = _retrieve_execution(month, year)
    return _json_response(body, status)


@never_cache
def admin_execution_review(request):
    body, status = _review_execution()
    return _json_response(body, status)


@never_cache
def admin_execution_load(request):
    body, status = _load_execution()
    return _json_response(body, status)


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


# Actions
def _retrieve_execution(month, year):
    data_url = _get_url(year)
    return _scrape(data_url, month, year)


def _review_execution():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()
    return _review(data_files_path)


def _load_execution():
    # Pick up the most recent downloaded files
    data_files_path = _get_most_recent_temp_folder()

    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay  ficheros que cargar.</p>"}
        status = 400
        return (body, status)

    # Copy downloaded files to the theme destination
    month, year = _arrange(data_files_path)

    cue = u"Vamos a cargar los datos disponibles en <b>%s</b> para %s" % (data_files_path, year)
    if month:
        cue = cue.replace(" para ", "para %s de " % month)

    management_commands = ("load_budget %s --language=es,en" % year, "load_investments %s --language=es,en" % year)
    return _execute(cue, *management_commands)


def _retrieve_inflation():
    return _retrieve("data/inflacion.csv")


def _retrieve_population():
    content, status = _retrieve("data/poblacion.csv")

    content = content.split("\n")

    # We assume a constant file format, newline terminated
    headers = ",".join(content[0].split(",")[2:])
    rows = content[1:-1]

    data = [headers]
    data.extend([",".join(row.split(",")[2:]) for row in rows if row.lstrip('"').startswith("1")])
    data.extend(content[-1:])

    data = "\n".join(data)

    return data, status


def _retrieve_glossary_es():
    return _retrieve("data/glosario_es.csv")


def _retrieve_glossary_en():
    return _retrieve("data/glosario_en.csv")


def _save_inflation(content):
    return _save("data/inflacion.csv", content, "Update inflation data")


def _save_population(content):
    content = content.split("\n")

    # We assume a constant file format, newline terminated
    headers = '"#Id","#Entidad",%s' % content[0]
    rows = content[1:-1]

    data = [headers]
    data.extend(['"1","Madrid",%s' % row for row in rows])
    data.extend(['"2","Madrid",%s' % row for row in rows])
    data.extend(content[-1:])

    data = "\n".join(data)

    return _save("data/poblacion.csv", data, "Update population data")


def _save_glossary_es(content):
    return _save("data/glosario_es.csv", content, "Update spanish glossary data")


def _save_glossary_en(content):
    return _save("data/glosario_en.csv", content, "Update english glossary data")


def _load_stats():
    return _execute(u"Vamos a cargar los datos estadísticos", "load_stats")


def _load_glossary_es():
    return _execute(u"Vamos a cargar los datos del glosario en español", "load_glossary --language=es")


def _load_glossary_en():
    return _execute(u"Vamos a cargar los datos del glosario en inglés", "load_glossary --language=en")


# Action helpers
def _scrape(url, month,  year):
    month = str(month)
    year = str(year)

    if not url:
        body = {"result": "error", "message": "<p>Nada que descargar.</p>"}
        status = 400
        return (body, status)

    try:
        # Read the given page
        page = _fetch(url)

        # Build the list of linked files
        files = _get_files(page)

        # Create the target folder
        temp_folder_path = _create_temp_folder()

        # We assume a constant page layout: ingresos, gastos, inversiones
        _download(files[0], temp_folder_path, "ingresos.csv")
        _download(files[1], temp_folder_path, "gastos.csv")
        _download(files[2], temp_folder_path, "inversiones.csv")

        _write_temp(temp_folder_path, ".budget_month", month)
        _write_temp(temp_folder_path, ".budget_year", year)

        # Keep track of the month of the data
        status = (month + "M" if month != "12" else "")  # 12M means the year is fully executed

        _write_temp(temp_folder_path, ".budget_status", status)

        message = (
            "<p>Los datos se han descargado correctamente.</p>"
            "<p>Puedes ver la página desde la que hemos hecho la descarga <a href='%s' target='_blank'>aquí</a>, "
            "y para tu referencia los ficheros han sido almacenados en <b>%s</b>.</p>" % (url, temp_folder_path)
        )
        body = {"result": "success", "message": message}
        status = 200
    except AdminException:
        message = (
            "<p>Se ha producido un error descargado los datos.</p>"
            "<p>Puedes ver la página desde la que hemos intentado hacer la descarga "
            "<a href='%s' target='_blank'>aquí</a>.</p>" % url
        )
        body = {"result": "error", "message": message}
        status = 500

    return (body, status)


def _review(data_files_path):
    if not data_files_path:
        body = {"result": "error", "message": "<p>No hay  ficheros que revisar.</p>"}
        status = 400
        return (body, status)

    # Execute a helper script to check the data files
    script_path = os.path.join(THEME_PATH, "loaders")

    cmd = "export PYTHONIOENCODING=utf-8 && "
    cmd += "cd %s && " % script_path
    cmd += "python madrid_check_datafiles.py %s" % data_files_path

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            u"<p>Se ha producido un error revisando los ficheros descargados: "
            "<pre>%s</pre></p>" % output
        )
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    message = (
        u"<p>Los ficheros descargados se han revisado correctamente: "
        "<pre>%s</pre></p>" % (output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


def _retrieve(file_path):
    try:
        body = _read(file_path)
        status = 200
        return (body, status)
    except AdminException as error:
        raise Exception(error)


def _save(file_path, content, commit_message):
    if not content:
        body = {"result": "error", "message": "<p>Nada que guardar.</p>"}
        status = 400
        return (body, status)

    try:
        _write(file_path, content)
        _commit(file_path, commit_message)

        body = {"result": "success", "message": "<p>Los datos se han guardado correctamente.</p>"}
        status = 200
    except AdminException:
        body = {"result": "error", "message": "<p>Se ha producido un error guardando los datos.</p>"}
        status = 500

    return (body, status)


def _execute(cue, *management_commands):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "export PYTHONIOENCODING=utf-8 "
        "&& cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset --hard origin/master "
        "&& cd %s"
    ) % (THEME_PATH, ROOT_PATH)

    for management_command in management_commands:
        cmd += "&& python manage.py %s " % management_command

    output, error = _execute_cmd(cmd)

    if error:
        message = (
            "<p>No se han podido ejecutar los comandos <code>%s</code>:"
            "<pre>%s</pre></p>"
        ) % (" && ".join(management_commands), output)
        body = {"result": "error", "message": message}
        status = 500
        return (body, status)

    # Touch project/wsgi.py so the app restarts
    _touch(os.path.join(ROOT_PATH, "project", "wsgi.py"))

    message = (
        u"<p>%s.</p>"
        "<p>Ejecutado: <pre>%s</pre></p>"
        "<p>Resultado: <pre>%s</pre></p>" % (cue, cmd, output)
    )
    body = {"result": "success", "message": message}
    status = 200
    return (body, status)


# Orchestration helpers
def _arrange(data_files_path):
    # Read the year and month of the budget data
    month = _read_temp(data_files_path, ".budget_month")
    year = _read_temp(data_files_path, ".budget_year")

    # Copy files around
    try:
        for language in ["es", "en"]:
            target_path = os.path.join(THEME_PATH, "data", language, "municipio", year)

            source = data_files_path
            destination = target_path

            _copy(source, destination, ".budget_status")
            _copy(source, destination, "gastos.csv")
            _copy(source, destination, "gastos.csv", "ejecucion_gastos.csv")
            _copy(source, destination, "ingresos.csv")
            _copy(source, destination, "ingresos.csv", "ejecucion_ingresos.csv")
            _copy(source, destination, "inversiones.csv")
            _copy(source, destination, "inversiones.csv", "ejecucion_inversiones.csv")

        data_path = os.path.join(THEME_PATH, "data")
        _commit(data_path, "Update %s execution data" % year)
    except AdminException as error:
        raise Exception(error)

    return (month, year)


# Network helpers
def _fetch(url):
    try:
        page = urllib.urlopen(url).read()
    except IOError as error:
        raise AdminException("Page at '%s' couldn't be fetched: %s" % (url, str(error)))

    return page


def _download(url, temp_folder_path, filename):
    file_path = os.path.join(temp_folder_path, filename)

    try:
        urllib.urlretrieve(url, file_path)
    except IOError as error:
        raise AdminException("File at '%s' couldn't be downloaded: %s" % (url, str(error)))


# Filesystem helpers
def _create_temp_folder():
    base_path = TEMP_BASE_PATH
    temp_folder_path = os.path.join(base_path, str(datetime.now().isoformat()))

    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)

    return temp_folder_path


def _read_temp(temp_folder_path, filename):
    file_path = os.path.join(temp_folder_path, filename)

    with open(file_path, "r") as file:
        return file.read()


def _write_temp(temp_folder_path, filename, content):
    file_path = os.path.join(temp_folder_path, filename)

    with open(file_path, "w") as file:
        file.write(content)


def _touch(file_path):
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
        "EOF"
    ) % (THEME_PATH, file_path, content)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be written." % file_path)


def _copy(source_path, destination_path, source_filename, destination_filename=None):
    if not destination_filename:
        destination_filename = source_filename

    source = os.path.join(source_path, source_filename)
    destination = os.path.join(destination_path, destination_filename)

    if not os.path.exists(destination_path):
        os.makedirs(destination_path)

    # The scripts/cp executable must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/cp -f %s %s"
    ) % (THEME_PATH, source, destination)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("File %s couldn't be copied." % source_filename)


def _commit(path, commit_message):
    # The scripts/git and scripts/git-* executables must be manually deployed and setuid'ed
    cmd = (
        "cd %s "
        "&& scripts/git fetch "
        "&& scripts/git reset origin/master "
        "&& scripts/git add %s "
        "&& scripts/git commit -m \"%s\n\nChange performed on the admin console.\" "
        "&& scripts/git push"
    ) % (THEME_PATH, path, commit_message)

    _, error = _execute_cmd(cmd)

    if error:
        raise AdminException("Path %s couldn't be commited." % path)


# Utility helpers
def _get_content(params):
    content = params.get("content", "")
    return base64.b64decode(content)


def _get_month(params):
    return int(params.get("month", "0"))


def _get_year(params):
    current_year = datetime.today().year
    return int(params.get("year", current_year))


def _get_url(year):
    url = None

    if (year <= 2019 and year >= 2018):
        url = EXECUTION_URL[year]

    if year <= 2017 and year >= 2011:
        url = EXECUTION_URL[2017]

    return url


def _get_files(page):
    doc = BeautifulSoup(page, "html.parser")
    links = doc.find_all("a", class_="ico-csv")

    base_url = "https://datos.madrid.es"
    return [base_url + link["href"] for link in links]


def _get_most_recent_temp_folder():
    temp_folder = None

    temp_folders = sorted(glob.glob("%s/*.*" % TEMP_BASE_PATH))

    if temp_folders:
        temp_folder = temp_folders[-1]

    return temp_folder


def _execute_cmd(cmd):
    # IO encoding is a nightmare. See https://stackoverflow.com/a/4027726
    env = os.environ.copy()

    if HTTP_PROXY:
        env["http_proxy"] = HTTP_PROXY

    if HTTPS_PROXY:
        env["https_proxy"] = HTTPS_PROXY

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=env, universal_newlines=True)

    output, _ = process.communicate()
    return_code = process.poll()

    output = output.decode("utf8", "backslashreplace")
    error = return_code != 0

    return (output, error)


def _json_response(data, status=200):
    return HttpResponse(json.dumps(data), content_type="application/json; charset=utf-8", status=status)


def _csv_response(data, status=200):
    return HttpResponse(data, content_type="text/csv; charset=utf-8", status=status)
