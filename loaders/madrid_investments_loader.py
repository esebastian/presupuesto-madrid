# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import InvestmentsLoader
import csv
import re

class MadridInvestmentsLoader(InvestmentsLoader):

    # An artifact of the in2csv conversion of the original XLS files is a trailing '.0', which we remove here
    def clean(self, s):
        return s.split('.')[0]

    def parse_item(self, filename, line):
        # Skip subtotal lines
        if line[0] in ['', '*']:
            return

        description = self._titlecase( line[4] )

        return {
            'is_expense': True,
            'area': self.clean(line[0]),
            'amount': self.parse_amount(line[5]),
            'description': description
        }


    # Parse a numerical amount, which can be in English format (for those CSVs generated
    # from XLS via in2csv) or Spanish.
    def parse_amount(self, amount):
        if ',' in amount:
            amount = amount.replace(',', '.')
        return self._read_english_number(amount)
