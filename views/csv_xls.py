# -*- coding: UTF-8 -*-

from budget_app.models import InflationStat, PopulationStat
from budget_app.views.helpers import get_context, get_main_entity
from budget_app.views.csv_xls import write_header, _generator

#
# STAT DATA
#
def write_inflation_stats(c, writer):
    inflation_data = InflationStat.objects.get_table()
    write_header(writer, [u'Año', u'Inflación'])
    for year in sorted(inflation_data):
        writer.writerow([year, inflation_data[year]['inflation']])

def inflation_stats(request, format):
    c = get_context(request)
    slug = get_main_entity(c).slug
    render_callback = _generator(u'inflacion-%s' % slug, format, write_inflation_stats)
    return render_callback.generate_response(c)

def write_population_stats(c, writer):
    entity = get_main_entity(c)
    population_data = PopulationStat.objects.get_entity_table(entity)
    write_header(writer, [u'Año', u'Población'])
    for year in sorted(population_data):
        writer.writerow([year, population_data[year]])

def population_stats(request, format):
    c = get_context(request)
    slug = get_main_entity(c).slug
    render_callback = _generator(u'poblacion-%s' % slug, format, write_population_stats)
    return render_callback.generate_response(c)
