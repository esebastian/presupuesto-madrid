# -*- coding: UTF-8 -*-

import datetime
import re

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

class MadridPaymentsLoader(PaymentsLoader):
  # Parse an input line into fields
  def parse_item(self, budget, line):
    # But what we want as area is the programme description
    policy_id = line[1][:2]
    policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

    # Some descriptions are missing in early years
    description = line[2].strip()
    if description=="":
      description="..."

    # And some payee names have some trailing punctuation marks: one or two instances of " ."
    payee = line[3].strip()
    payee = re.sub(r'( \.)+$', '', payee)

    # Get institutional code. See the budget_loader for more details on this process for Madrid.
    institution = self.get_institution_code(line[0][0:3])
    ic_code = institution + (line[0][3:6] if institution=='0' else '00')

    return {
      'area': policy,
      'fc_code': None,
      'ec_code': None,
      'ic_code': ic_code,
      'date': None,
      'payee': payee,
      'description': description + ' (' + str(budget.year) + ')',
      'amount': self._read_english_number(line[4])
    }

  # We expect the organization code to be one digit, but Madrid has a 3-digit code.
  # We can _almost_ pick the last digit, except for one case.
  def get_institution_code(self, madrid_code):
      institution_code = madrid_code if madrid_code!='001' else '000'
      return institution_code[2]
