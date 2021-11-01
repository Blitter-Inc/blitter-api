from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class ObjectMapPageNumberPagination(PageNumberPagination):

    def get_paginated_response(self, data):
        res = {}
        res['count'] = self.page.paginator.count
        res['page'] = self.page.number
        res['next'] = self.get_next_link()
        res['previous'] = self.get_previous_link()
        res['ordering'] = self.request.GET.get('ordering', '')
        res['ordered_sequence'] = [obj['id'] for obj in data]
        res['object_map'] = {obj['id']: obj for obj in data}
        return Response(res)
