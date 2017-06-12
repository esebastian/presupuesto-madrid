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

        # Skip first line
        if line[0] == 'Centro':
            return

        is_expense = (filename.find('gastos.csv')!=-1)
        is_actual = (filename.find('/ejecucion_')!=-1)
        year = re.search('municipio/(\d+)/', filename).group(1)
        if is_expense:
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            fc_code = line[4].zfill(5)
            ec_code = line[8]
            amount = self.parse_amount(line[15 if is_actual else 12])

            # Ignore transfers to dependent organisations
            if ec_code[:-2] in ['410', '710', '400', '700']:
                amount = 0

            # Get institutional code. We ignore sections in autonomous bodies,
            # since they get assigned to different sections in main body but that's
            # not relevant.
            # Note: in the most recent 2016 data the leading zeros were missing,
            # so add them back using zfill.
            institution = self.get_institution_code(line[0].zfill(3))
            ic_code = institution + (line[2].zfill(3) if institution=='0' else '00')

            # Apply institutional mapping to make codes consistent across years
            if int(year) <= 2015:
                ic_code = institutional_mapping.get(ic_code, ic_code)

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

            # The input files are encoded in ISO-8859-1, since we want to work with the files
            # as they're published in the original open data portal. All the text fields are
            # ignored, as we use the codes instead, but the description one.
            description = self._spanish_titlecase( line[9].decode("iso-8859-1").encode("utf-8") )

            return {
                'is_expense': True,
                'is_actual': is_actual,
                'fc_code': fc_code,
                'ec_code': ec_code[:-2],        # First three digits (everything but last two)
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

        else:
            ec_code = line[4]
            ic_code = self.get_institution_code(line[0].zfill(3)) + '00'
            amount = self.parse_amount(line[9 if is_actual else 8])

            # Ignore transfers from parent organisation
            if ec_code[:-2] in ['410', '710', '400', '700']:
                amount = 0

            # See note above
            description = self._spanish_titlecase( line[5].decode("iso-8859-1").encode("utf-8") )

            return {
                'is_expense': False,
                'is_actual': is_actual,
                'ec_code': ec_code[:-2],        # First three digits
                'ic_code': ic_code,
                'item_number': ec_code[-2:],    # Last two digits
                'description': description,
                'amount': amount
            }

    # We expect the organization code to be one digit, but Madrid has a 3-digit code.
    # We can _almost_ pick the last digit, except for one case.
    def get_institution_code(self, madrid_code):
        institution_code = madrid_code if madrid_code!='001' else '000'
        return institution_code[2]

    # Parse a numerical amount, which can be in English format (for those CSVs generated
    # from XLS via in2csv) or Spanish.
    def parse_amount(self, amount):
        if ',' in amount:
            amount = amount.replace(',', '.')
        return self._parse_amount(amount)

    def _get_delimiter(self):
        return ';'
