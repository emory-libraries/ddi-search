from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from ddisearch.ddi.models import CodeBook
from ddisearch.geo.models import Location, GeonamesContinent, GeonamesCountry


def resources_by_location(request, geonames_id=None, geo_coverage=None):
    '''Helper method to find DDI resources that explicitly reference
    the specified place. Expects one and only one of geonames_id or
    geo_coverage to be specified.

    :param geonames_id: numeric geonames identifier
    :param geo_coverage: geographic name
    '''
    resources = CodeBook.objects.all()
    if geonames_id is not None:
        resources = resources.filter(geo_coverage__id='geonames:%d' % geonames_id)
    if geo_coverage is not None:
        resources = resources.filter(geo_coverage=geo_coverage)

    per_page = 10  # for now
    paginator = Paginator(resources, per_page, orphans=5)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1
    # If page request (9999) is out of range, deliver last page of results.
    try:
        results = paginator.page(page)
    except (EmptyPage, InvalidPage):
        page = paginator.num_pages
        results = paginator.page(paginator.num_pages)

    return results


def browse(request, continent=None, country=None, state=None,
    geonames_id=None):
    '''Browse records and available locations by geography.  Displays
    content for the lowest level specified, any sub locations, and
    a list of resources for the current location.  If no locations are
    specified, displays a list of continents and resources with global
    coverage.

    :param continent: 2-letter continent code
    :param country: 2-letter country code
    :param state: 2-3 letter or number state code
    :param geonames_id: geonames identifier for a location smaller than
        a state (e.g., a city or county)
    '''
    # if no continent specified, get a list of all continents
    # that are represented by the data
    current_place = None
    places = None
    hierarchy = []
    resource_filter = {}

    # if continent is not set, display top-level geography browse page;
    # list of continents, global resources
    if continent is None:
        codes = Location.objects.order_by('continent_code') \
                                .values_list('continent_code', flat=True) \
                                .distinct()
        places = GeonamesContinent.objects.filter(code__in=codes).order_by('name')

    # find continent if set
    if continent is not None:
        # get continent object so we can display name, etc
        cont = get_object_or_404(GeonamesContinent, code=continent)
        # TODO: possibly find list of country codes in the data and then
        # get country list from GeonamesCountry to ensure we don't miss things?
        # set as current place
        current_place = cont
        # add to breadcrumb hirearchy
        hierarchy.append(cont)

        # if country is not set, browse the continent
        if country is None:
            country_codes = Location.objects.filter(continent_code=cont.code) \
                                    .order_by('country_code') \
                                    .values('country_code') \
                                    .distinct()

            # find places in this continent
            codes = [loc['country_code'] for loc in country_codes
                     if loc['country_code'] is not None]
            places = GeonamesCountry.objects.filter(code__in=codes).order_by('name')

    # find country if set
    if country is not None:
        country = get_object_or_404(GeonamesCountry, code=country,
            continent=continent)
        hierarchy.append(country)
        current_place = country

        # if state is not set, browse the country
        if state is None:
            places = Location.objects.filter(country_code=country.code, feature_code='ADM1') \
                                     .order_by('name')

    # find state if set
    if state is not None:
        state = get_object_or_404(Location, state_code=state, feature_code='ADM1',
            continent_code=continent, country_code=country.code)

        hierarchy.append(state)
        current_place = state

        # if no sub-state location is specified, browse the state
        if geonames_id is None:
            places = Location.objects.filter(state_code=state.state_code) \
                                     .exclude(feature_code='ADM1')

    # if geonames id is specified, browse by sub-state city or region
    if geonames_id is not None:
        location = get_object_or_404(Location, geonames_id=geonames_id,
            continent_code=continent, country_code=country.code)
        hierarchy.append(location)
        current_place = location

    # find resources that explicitly reference the current place
    if current_place is None:
        results = resources_by_location(request, geo_coverage='Global')
    else:
        results = resources_by_location(request,
                                        geonames_id=current_place.geonames_id)

    return render(request, 'geo/browse.html',
                  {'places': places, 'results': results,
                  'current_place': current_place, 'hierarchy': hierarchy})

