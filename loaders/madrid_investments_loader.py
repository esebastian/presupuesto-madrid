# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import InvestmentsLoader
import csv
import re

class MadridInvestmentsLoader(InvestmentsLoader):

    # An artifact of the in2csv conversion of the original XLS files is a trailing '.0', which we remove here
    def clean(self, s):
        return s.split('.')[0]

    def parse_item(self, budget, line):
        # Skip empty/header/subtotal lines
        if line[0] in ['', '*', 'Fondo']:
            return

        # 2017 data is in a different format to previous years
        if budget.year < 2017:
            description = line[4]
            gc_code = line[0]
            amount = line[5]
        else:
            description = unicode(line[8], encoding='iso-8859-1').encode('utf8')
            gc_code = line[9]
            amount = line[28]

        return {
            'is_expense': True,
            'gc_code': self.clean(gc_code),
            'amount': self.parse_amount(amount),
            'description': self._titlecase(description)
        }


    # Parse a numerical amount, which can be in English format (for those CSVs generated
    # from XLS via in2csv) or Spanish.
    def parse_amount(self, amount):
        if ',' in amount:
            amount = amount.replace(',', '.')
        return self._read_english_number(amount)

    # Override default input delimiter
    def _get_delimiter(self):
        return ';'
