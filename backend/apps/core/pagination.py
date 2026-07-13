from django.core.paginator import EmptyPage, Paginator
from rest_framework.exceptions import ParseError
from rest_framework.pagination import BasePagination
from rest_framework.response import Response


class StandardResultsSetPagination(BasePagination):
    default_page = 1
    default_perpage = 10
    max_perpage = 50

    def paginate_queryset(self, queryset, request, view=None):
        self.request = request
        self.page_number = self._get_positive_int("page", self.default_page)
        self.perpage = self._get_positive_int("perpage", self.default_perpage)

        if self.perpage > self.max_perpage:
            raise ParseError(f"Vous ne pouvez pas demander plus de {self.max_perpage} éléments par page.")

        if hasattr(queryset, "ordered") and not queryset.ordered:
            queryset = queryset.order_by(queryset.model._meta.pk.name)

        self.paginator = Paginator(queryset, self.perpage)
        self.count = self.paginator.count
        self.total_pages = self.paginator.num_pages

        try:
            self.page = self.paginator.page(self.page_number)
            return list(self.page.object_list)
        except EmptyPage:
            return []

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "page": self.page_number,
                "perpage": self.perpage,
                "total_pages": self.total_pages,
                "results": data,
            }
        )

    def _get_positive_int(self, param_name, default):
        raw_value = self.request.query_params.get(param_name, default)

        try:
            value = int(raw_value)
        except (TypeError, ValueError):
            raise ParseError(f"Le paramètre {param_name} doit être un nombre entier.")

        if value <= 0:
            raise ParseError(f"Le paramètre {param_name} doit être supérieur à 0.")

        return value
