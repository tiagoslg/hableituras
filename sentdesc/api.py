import sys
import json
 
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.core.serializers.json import DjangoJSONEncoder
 
import myapp.models
 
class JSONResponse(HttpResponse):
    """
    Return a JSON serialized HTTP response
    """
    def __init__(self, request, data, status=200):
        # pass DjangoJSONEncoder to handle Decimal fields
        json_data = json.dumps(data, cls=DjangoJSONEncoder)
        super(JSONResponse, self).__init__(
            content=json_data,
            content_type='application/json',
            status=status,
        )
 
class JSONViewMixin(object):
    """
    Return JSON data. Add to a class-based view.
    """
    def json_response(self, data, status=200):
        return JSONResponse(self.request, data, status=status)
 
# API
 
# define a map from json column name to model field name
# this would be better placed in the model
col_name_map = {'name': 'name',
                'supplier': 'supplier__name', # can do foreign key look ups
                'price': 'price',
               }
class MyAPI(JSONViewMixin, View):
    "Return the JSON representation of the objects"
    def get(self, request, *args, **kwargs):
        class_name = kwargs.get('cls_name')
        params = request.GET
        # make this api general enough to handle different classes
        klass = getattr(sys.modules['myapp.models'], class_name)
 
        # TODO: this only pays attention to the first sorting column
        sort_col_num = params.get('iSortCol_0', 0)
        # default to value column
        sort_col_name = params.get('mDataProp_{0}'.format(sort_col_num), 'value')
        search_text = params.get('sSearch', '').lower()
        sort_dir = params.get('sSortDir_0', 'asc')
        start_num = int(params.get('iDisplayStart', 0))
        num = int(params.get('iDisplayLength', 25))
        obj_list = klass.objects.all()
        sort_dir_prefix = (sort_dir=='desc' and '-' or '')
        if sort_col_name in col_name_map:
            sort_col = col_name_map[sort_col_name]
            obj_list = obj_list.order_by('{0}{1}'.format(sort_dir_prefix, sort_col))
 
        filtered_obj_list = obj_list
        if search_text:
            filtered_obj_list = obj_list.filter_on_search(search_text)
 
        d = {"iTotalRecords": obj_list.count(),                # num records before applying any filters
            "iTotalDisplayRecords": filtered_obj_list.count(), # num records after applying filters
            "sEcho":params.get('sEcho',1),                     # unaltered from query
            "aaData": [obj.as_dict() for obj in filtered_obj_list[start_num:(start_num+num)]] # the data
        }
 
        return self.json_response(d)