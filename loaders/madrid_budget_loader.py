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
            '13304': '13402',   # Planificación de la movilidad
            '13305': '13403',   # Instalaciones de gestión del tráfico
            '13401': '13510',   # SAMUR
            '13501': '13610',   # Bomberos
            '15201': '15210',   # Vivienda
            '15501': '15321',   # Vías públicas
            '15502': '15322',   # Otras actuaciones en vías públicas
            '15504': '15340',   # Infraestructuras públicas
            '16101': '16001',   # Ingeniería del agua
            '16201': '16210',   # Gestión ambiental
            '16202': '16230',   # Valdemingómez
            '17203': '17211',   # Sostenibilidad
            '17201': '17212',   # Control ambiental
            '23000': '23100',   # Gestión de familia
            '23202': '23101',   # Igualdad de oportunidades
            '23301': '23103',   # Mayores
            '24000': '24100',   # Dirección de empleo
            '31000': '31100',   # Dirección Madrid Salud
            '31320': '31101',   # Salubridad pública
            '31321': '31102',   # Adicciones
            '31401': '49300',   # Consumo
            '32101': '32301',   # Centros docentes
            '32401': '32601',   # Servicios de educación
            '33201': '33210',   # Bibliotecas
            '33404': '92402',   # Participación empresarial
            '33403': '33601',   # Patrimonio cultural
            '43110': '43301',   # Promoción económica
            '44101': '44110',   # Promoción del transporte
            '91100': '91230',   # Secretaría del pleno
            '91101': '91240',   # Grupos municipales
            '92701': '92202',   # Medios de comunicación
            '92301': '92310',   # Estadística
        }
        programme_mapping_2011 = {
            '13303': '13302',   # Aparcamientos
            '17102': '16601',   # Mobiliario urbano
            '23103': '23106',   # Servicios sociales
            '23104': '23106',   # Servicios sociales
            '23105': '23107',   # Inmigración
            '23201': '23202',   # Igualdad de oportunidades
            '23101': '23290',   # Cooperación internacional
            '91203': '91204',   # Área de portavoz
            '91204': '91203',   # Área de coordinación territorial
            '91205': '91204',   # Área de portavoz
            '92202': '92208',   # Relaciones con distritos
        }
        programme_mapping_2012 = {
            # old programme: new programme
            '33404': '33403',   # Patrimonio cultural y paisaje urbano
            '91203': '91204',   # Área de portavoz
            '91204': '91203',   # Área de coordinación territorial
            '91205': '91204',   # Área de portavoz
            '92202': '92208',   # Relaciones con distritos
        }
        programme_mapping_2013 = {
            # old programme: new programme
            '33404': '33403',   # Patrimonio cultural y paisaje urbano
            '91203': '91204',   # Área de portavoz
            '91205': '91204',   # Área de portavoz
            '91207': '91205',   # Área de participación ciudadana
        }
        programme_mapping_2015 = {
            # old programme: new programme
            '15341': '15340',   # Infraestructuras urbanas
            '23104': '23200',   # Planes de barrio
            '33404': '92402',   # Participación empresarial
        }

        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)
        year = re.search('municipio/(\d+)/', filename).group(1)
        if is_expense:
            fc_code = line[4]
            ec_code = line[8]
            ic_code = self.get_institution_code(line[0]) + line[2]
            amount = self._parse_amount(line[15 if is_actual else (10 if year=='2017' else 12)])

            # Ignore transfers to dependent organisations
            if ec_code[:-2]=='410' or ec_code[:-2]=='710':
                amount = 0

            # The department codes are not totally consistent across years. We are a bit
            # flexible with the precise names, but sometimes it's too much and needs fixing.
            if year == '2011' and (ic_code=='0013' or ic_code=='0014'):
                ic_code = ic_code+'b'

            # Some years require some amendments
            if year == '2011':
                fc_code = programme_mapping_2011.get(fc_code, fc_code)
            if year == '2012':
                fc_code = programme_mapping_2012.get(fc_code, fc_code)
            if year == '2013':
                fc_code = programme_mapping_2013.get(fc_code, fc_code)
            if year == '2015':
                fc_code = programme_mapping_2015.get(fc_code, fc_code)

            # For years before 2015 we check whether we need to amend the programme code
            if int(year) < 2015:
                fc_code = programme_mapping.get(fc_code, fc_code)

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': self._spanish_titlecase(line[9]),
                'amount': amount
            }

        else:
            ec_code = line[4]
            ic_code = self.get_institution_code(line[0]) + '00'
            amount = self._parse_amount(line[9 if is_actual else (6 if year=='2017' else 8)])

            # Ignore transfers from parent organisation
            if ec_code[:-2]=='400' or ec_code[:-2]=='700':
                amount = 0

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': self._spanish_titlecase(line[5]),
                'amount': amount
            }

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    def get_institution_code(self, madrid_code):
        institution_code = madrid_code if madrid_code!='001' else '000'
        return institution_code[2]
