# -*- coding: UTF-8 -*-
from coffin.shortcuts import render_to_response
from budget_app.views.helpers import *

import glob

def admin(request, render_callback=None):
    # Get request context
    c = get_context(request, css_class='body-admin', title='')

    c['output'] = glob.glob(ROOT_PATH+"/*.*")

    return render_to_response('admin/index.html', c)
