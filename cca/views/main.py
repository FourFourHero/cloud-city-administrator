import logging

from django.contrib.admin.views.decorators import staff_member_required

from cca.views.response import *

logger = logging.getLogger(__name__)

def home(request):
    response_dict = success_dict()
    return render_template(request, response_dict, 'index.html')

