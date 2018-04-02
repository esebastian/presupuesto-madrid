# -*- coding: UTF-8 -*-

import datetime
import re

from budget_app.loaders import PaymentsLoader
from budget_app.models import Budget

class MadridPaymentsLoader(PaymentsLoader):
  # Parse an input line into fields
  def parse_item(self, budget, line):
    # The institutional structure of the City of Madrid has changed quite a lot along the
    # years, es In order to show the evolution of a given section we need to keep codes
    # consistent.
    institutional_mapping = {
        '0085': '0027',     # EQUIDAD, DERECHOS SOCIALES Y EMPLEO
        '0033': '0037',     # COORDINACIÓN TERRITORIAL Y ASOCIACIONES
        '0041': '0047',     # PORTAVOZ, COORD. JUNTA GOB. Y RELAC. CON EL PLENO
        '0025': '0057',     # ECONOMÍA Y HACIENDA
        '0032': '0067',     # SALUD, SEGURIDAD Y EMERGENCIAS
        '0071': '0077',     # PARTICIPACIÓN CIUDADANA, TRANSP. Y GOB. ABIERTO
        '0035': '0087',     # DESARROLLO URBANO SOSTENIBLE
        '0015': '0097',     # MEDIO AMBIENTE Y MOVILIDAD
        '0065': '0098',     # CULTURA Y DEPORTES
    }

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

    # Apply institutional mapping to make codes consistent across years
    if budget.year <= 2015:
        ic_code = institutional_mapping.get(ic_code, ic_code)

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
