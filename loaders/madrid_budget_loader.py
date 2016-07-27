# -*- coding: UTF-8 -*-
from budget_app.models import *
from budget_app.loaders import SimpleBudgetLoader
from decimal import *
import csv
import os
import re

class MadridBudgetLoader(SimpleBudgetLoader):

    def parse_item(self, filename, line):
        # Programme codes have changed in 2015, due to new laws. Since the application expects a code-programme
        # mapping to be constant over time, we are forced to amend budget data prior to 2015.
        programme_mapping = {
            # old programme: new programme
            '13304': '13402',   # PLANIFICACIÓN DE LA MOVILIDAD
            '13305': '13403',   # INSTALACIONES DE GESTIÓN DE LA MOVILIDAD
            '13401': '13510',   # SAMUR
            '13501': '13610',   # BOMBEROS
            '15201': '15210',   # PROMOCIÓN Y GESTIÓN DE VIVIENDA
            '15501': '15321',   # VÍAS PÚBLICAS
            '15502': '15322',   # OTRAS ACTUACIONES EN VÍAS PÚBLICAS
            '15504': '15340',   # INFRAESTRUCTURAS URBANAS
            '16101': '16001',   # INGENIERÍA DEL AGUA
            '16201': '16210',   # GESTIÓN AMBIENTAL URBANA
            '16202': '16230',   # PARQUE TECNOLÓGICO DE VALDEMINGÓMEZ
            '17201': '17212',   # CONTROL AMBIENTAL
            '23000': '23100',   # DIR.Y GEST.ADMVA.EQUIDAD, DCHOS. SOCIALES Y EMPLEO
            '23301': '23103',   # MAYORES Y ATENCIÓN SOCIAL
            '23202': '23101',   # IGUALDAD ENTRE MUJERES Y HOMBRES
            '24000': '24100',   # DIREC. Y GESTIÓN ADMTVA. AG. EMPLEO DE MADRID
            '31000': '31100',   # DIREC. Y GESTIÓN ADMTVA. MADRID SALUD
            '31320': '31101',   # SALUD PÚBLICA
            '31321': '31102',   # ADICCIONES
            '31401': '49300',   # CONSUMO
            '32401': '32601',   # SERVICIOS COMPLEMENTARIOS EDUCACIÓN
            '33201': '33210',   # BIBLIOTECAS PÚBLICAS Y PATRIMONIO BIBLIOGRÁFICO
            '33403': '33601',   # PATRIMONIO CULTURAL Y PAISAJE URBANO
            '43310': '43301',   # PROMOCIÓN ECONÓMICA Y DESARROLLO EMPRESARIAL
            '44101': '44110',   # PROMOCIÓN, CONTROL Y DESARROLLO DEL TRANSPORTE
            '91101': '91240',   # GRUPOS POLÍTICOS MUNICIPALES
            '92701': '92202',   # MEDIOS DE COMUNICACIÓN
            '92301': '92310',   # ESTADÍSTICA
        }
        programme_mapping_2015 = {
            # old programme: new programme
            '23104': '23200'    # Planes de barrio
        }

        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)
        if is_expense:
            fc_code = line[4]
            ec_code = line[8]
            ic_code = self.get_institution_code(line[0]) + line[2]

            # For years before 2015 we check whether we need to amend the programme code
            year = re.search('municipio/(\d+)/', filename).group(1)
            if int(year) < 2015:
                fc_code = programme_mapping.get(fc_code, fc_code)
            else:
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': line[9],
                'amount': self._parse_amount(line[15 if is_actual else 10])
            }

        else:
            ec_code = line[4]
            ic_code = self.get_institution_code(line[0]) + '00'
            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': line[5],
                'amount': self._parse_amount(line[9 if is_actual else 6])
            }

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    def get_institution_code(self, madrid_code):
        institution_code = madrid_code if madrid_code!='001' else '000'
        return institution_code[2]
