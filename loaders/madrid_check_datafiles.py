# -*- coding: UTF-8 -*-

import os
import csv
import sys
import re

from decimal import *


# Read number in English format (123,456.78), and return as number of cents
def read_english_number(s):
    if (s.strip()==""):
        return 0

    return int(Decimal(s.replace(',', ''))*100)

# Parse a numerical amount, which can be in English format (for those CSVs generated
# from XLS via in2csv) or Spanish.
def parse_amount(amount):
    if ',' in amount:
        amount = amount.replace(',', '.')
    return read_english_number(amount)

def format_number(n):
  return '{:20,.2f}'.format(n)

def get_stats(path, is_expense):
  total_external = 0
  total_internal_transfer = 0

  filename = os.path.join(path, 'gastos.csv' if is_expense else 'ingresos.csv')
  reader = csv.reader(open(filename, 'rb'), delimiter=';')
  for index, line in enumerate(reader):
      if re.match("^#", line[0]):         # Ignore comments
          continue

      if re.match("^ *$", ''.join(line)): # Ignore empty lines
          continue

      if line[0] == 'Centro':             # Ignore header
          continue

      if is_expense:
          ec_code = line[8]
          amount = parse_amount(line[15])
      else:
          ec_code = line[4]
          amount = parse_amount(line[9])

      if ec_code[:-2] in ['410', '710', '400', '700']:
        total_internal_transfer+=amount
      else:
        total_external+=amount

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
print "  Ingresos: %s" % (format_number(incoming_revenues/100), )
print "  Gastos  : %s" % (format_number(outgoing_expenses/100), )
print " "
print "Eliminaciones"
print "  Ingresos: %s" % (format_number(internal_revenues/100), )
print "  Gastos  : %s" % (format_number(internal_expenses/100), )
