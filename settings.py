# -*- coding: UTF-8 -*-

from django.conf.urls import patterns, url

MAIN_ENTITY_LEVEL = 'municipio'
MAIN_ENTITY_NAME = 'Madrid'

BUDGET_LOADER = 'MadridBudgetLoader'
PAYMENTS_LOADER = 'MadridPaymentsLoader'

FEATURED_PROGRAMMES = ['13610', '13510', '16301', '15321', '15210', '23103', '23102', '33401', '33210']

OVERVIEW_INCOME_NODES = [
                          {
                            'nodes': [['11', '113']],
                            'label.es': 'Impuesto sobre bienes inmuebles de naturaleza urbana',
                            'label.en': 'Impuesto sobre bienes inmuebles de naturaleza urbana',
                            'link_id': '11'
                          },
                          '42',
                          {
                            'nodes': [['11', '116']],
                            'label.es': 'Impuesto sobre incremento del valor de terrenos',
                            'label.en': 'Impuesto sobre incremento del valor de terrenos',
                            'link_id': '11'
                          },
                          {
                            'nodes': ['33'],
                            'label.es': 'Tasas por la utilización del dominio público',
                            'label.en': 'Tasas por la utilización del dominio público',
                            'link_id': '33'
                          },
                          {
                            'nodes': [['30', '303']],
                            'label.es': 'Servicio de tratamiento de residuos',
                            'label.en': 'Servicio de tratamiento de residuos',
                            'link_id': '30'
                          },
                        ]
OVERVIEW_EXPENSE_NODES = ['13', '16', '15', '23', '92', '17', '33', '34', '01']

# How aggresive should the Sankey diagram reorder the nodes. Default: 0.79 (Optional)
# Note: 0.5 usually leaves nodes ordered as defined. 0.95 sorts by size (decreasing).
OVERVIEW_RELAX_FACTOR = 0.5

# Show Payments section in menu & home options. Default: False.
# SHOW_PAYMENTS           = True

# Show Tax Receipt section in menu & home options. Default: False.
# SHOW_TAX_RECEIPT        = True

# Show Counties & Towns links in Policies section in menu & home options. Default: False.
# SHOW_COUNTIES_AND_TOWNS = False

# Show an extra tab with institutional breakdown. Default: True.
# SHOW_INSTITUTIONAL_TAB  = False

# Show an extra tab with funding breakdown (only applicable to some budgets). Default: False.
# SHOW_FUNDING_TAB = False

# Adjust inflation in amounts in Overview page. Default: True
# ADJUST_INFLATION_IN_OVERVIEW = False

# Show Subtotals panel in Overview. Default: False
SHOW_OVERVIEW_SUBTOTALS = True

# Calculate budget indicators (True), or show/hide the ones hardcoded in HTML (False). Default: True.
# CALCULATE_BUDGET_INDICATORS = False

# Show an extra column with actual revenues/expenses. Default: True.
# Warning: the execution data still gets shown in the summary chart and in downloads.
#SHOW_ACTUAL = True

# Include financial income/expenditures in overview and global policy breakdowns. Default: False.
INCLUDE_FINANCIAL_CHAPTERS_IN_BREAKDOWNS = True

# Search in entity names. Default: True.
SEARCH_ENTITIES = False

# Supported languages. Default: ('es', 'Castellano')
LANGUAGES = (
  ('es', 'Castellano'),
  ('en', 'English'),
)

# Setup Data Source Budget link
DATA_SOURCE_BUDGET      = 'http://datos.madrid.es/portal/site/egob/menuitem.c05c1f754a33a9fbe4b2e4b284f1a5a0/?vgnextoid=af62db13cb659410VgnVCM1000000b205a0aRCRD&vgnextchannel=374512b9ace9f310VgnVCM100000171f5a0aRCRD&vgnextfmt=default'

# Setup Data Source Population link
DATA_SOURCE_POPULATION  = 'http://www.ine.es/jaxiT3/Tabla.htm?t=2881&L=0'

# Setup Data Source Inflation link
DATA_SOURCE_INFLATION   = 'http://www.ine.es/jaxiT3/Tabla.htm?t=10019&L=0'

# Setup Main Entity Web Url
MAIN_ENTITY_WEB_URL     = 'http://www.madrid.es/'

# Setup Main Entity Legal Url (if empty we hide the link)
MAIN_ENTITY_LEGAL_URL   = 'http://www.madrid.es/portales/munimadrid/avisoLegal.html'

# External URL for Cookies Policy (if empty we use out template page/cookies.html)
COOKIES_URL             = 'http://www.madrid.es/portales/munimadrid/cookies.html'

# Allow overriding of default treemap color scheme
COLOR_SCALE = [ '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#e7969c', '#bcbd22', '#17becf' ]
