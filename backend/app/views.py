"""
These view functions and classes implement both standard GET routes and API endpoints.

GET routes produce largely empty HTML pages that expect a React component to attach to them and
handle most view concerns. You can supply a few pieces of data in the render function's context
argument to support this expectation.

Of particular use are the properties: page_metadata, component_props, and component_name:
page_metadata: these values will be included in the page's <head> element.
Currently, only the `title` property is used. component_props: these can be any properties you
wish to pass into your React components as its highest-level props.
component_name: this should reference the exact name of the React component
you intend to load onto the page.

Example:
context = {
    'page_metadata': {
        'title': 'Example ID page'
    },
    'component_props': {
        'id': example_id
    },
    'component_name': 'ExampleId'
}
"""
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.db.models import Count
from app.models import City, Evictions
from django.db.models.functions import TruncYear, TruncMonth


def index(request):
    """
    Home page
    """

    context = {
        'page_metadata': {
            'title': 'Home page'
        },
        'component_name': 'Home'
    }

    return render(request, 'index.html', context)


def get_cities(request):
    cities = City.objects.values_list('id', flat=True).order_by('id')
    return JsonResponse({"cities": list(cities)})


def get_evictions(request, city):
    """
    returns per city:
            {"evictions: {year: [list of counts per month}}
            Example:
            {"evictions":
                {"2020": [0, 0, 0, 1, 0, 0, 0, 0, 2, 2, 2, 13],
                "2021": [0, 4, 5, 9, 3, 4, 9, 5, 9, 1, 0, 0]}}
    """
    evictions = Evictions.objects.filter(city__id=city) \
        .annotate(year=TruncYear('file_date'), month=TruncMonth('file_date'), ) \
        .order_by('file_date__year', 'file_date__month') \
        .values('file_date__year', 'file_date__month') \
        .annotate(count=Count('pk'))

    formatted = {}
    for evictions_per_month in evictions:
        year = evictions_per_month['file_date__year']
        month = evictions_per_month['file_date__month']
        count = evictions_per_month['count']
        # if year exists
        if year in formatted:
            formatted[year][month - 1] = evictions_per_month[
                'count']
        # if year doesn't exist, add it, initialize 12 months as zeros in list
        else:
            formatted[year] = [0] * 12
    print('get evictions:::', formatted)
    return JsonResponse({"evictions": formatted})


def get_eviction_by_id(request, id):
    eviction = Evictions.objects.get(id=id)
    print('eviction', eviction)

    return JsonResponse({'id': eviction.id, 'file_date': eviction.file_date})
