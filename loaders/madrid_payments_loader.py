# -*- coding: UTF-8 -*-

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget
import datetime

class MadridPaymentsLoader(PaymentsLoader):
  # Parse an input line into fields
  def parse_item(self, budget, line):
    # But what we want as area is the programme description
    policy_id = line[0][:2]
    policy = Budget.objects.get_all_descriptions(budget.entity)['functional'][policy_id]

    return {
      'area': policy,
      'fc_code': None,
      'ec_code': None,
      'date': None,
      'contract_type': None,
      'payee': line[2].strip(),
      'description': line[1].strip(),
      'amount': self._read_english_number(line[3])
    }
