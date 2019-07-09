# -*- coding: UTF-8 -*-

import os
import csv
import sys
import re

from decimal import *


# Read number in English format (123,456.78), and return as number of cents
def read_english_number(s):
    if s.strip() == "":
        return 0

    return int(Decimal(s.replace(',', '')) * 100)


# Parse a numerical amount, which can be in English format (for those CSVs generated
# from XLS via in2csv) or Spanish.
def parse_amount(amount):
    amount = amount.strip()

    separators = re.sub(r"\d", "", amount)

    for sep in separators[:-1]:
        amount = amount.replace(sep, "")

    if separators:
        amount = amount.replace(separators[-1], ".")

    return read_english_number(amount)


def format_number(n):
    formatted_number = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1,", "%18.0f" % n)
    return formatted_number + " €"


def get_stats(path, is_expense):
    total_external = 0
    total_internal_transfer = 0

    filename = os.path.join(path, 'gastos.csv' if is_expense else 'ingresos.csv')
    reader = csv.reader(open(filename, 'rb'), delimiter=';')
    for index, line in enumerate(reader):
        if re.match("^#", line[0]):  # Ignore comments
            continue

        if re.match("^ *$", ''.join(line)):  # Ignore empty lines
            continue

        if line[0] == 'Centro':  # Ignore header
            continue

        if is_expense:
            ec_code = line[8]

            # Select the amount column to use based on whether we are importing execution
            # or budget data. In the latter case, sometimes we're dealing with the
            # amended budget, sometimes with the just approved one, in which case
            # there're less columns
            amount_column = 12 if len(line) > 11 else 10  # in case we're importing budget data
            amount_column = 15 if len(line) > 12 else amount_column  # in case we're importing execution data
            amount = parse_amount(line[amount_column])
        else:
            ec_code = line[4]

            # Select the column from which to read amounts. See similar comment above.
            amount_column = 8 if len(line) > 7 else 6  # in case we're importing budget data
            amount_column = 9 if len(line) > 8 else amount_column  # in case we're importing execution data
            amount = parse_amount(line[amount_column])

        if ec_code[:-2] in ['410', '710', '400', '700']:
            total_internal_transfer += amount
        else:
            total_external += amount

    return total_external, total_internal_transfer


# Get path to data files
if len(sys.argv) < 2:
    print "Por favor, indica la ruta de los ficheros a comprobar."
    sys.exit()

path = sys.argv[1]

# Open data files and get some basic stats
incoming_revenues, internal_revenues = get_stats(path, False)
outgoing_expenses, internal_expenses = get_stats(path, True)

print "Datos de ejecución (tras descontar eliminaciones)"
print "  Ingresos: %s" % format_number(incoming_revenues / 100)
print "  Gastos  : %s" % format_number(outgoing_expenses / 100)
print " "
print "Eliminaciones"
print "  Ingresos: %s" % format_number(internal_revenues / 100)
print "  Gastos  : %s" % format_number(internal_expenses / 100)
