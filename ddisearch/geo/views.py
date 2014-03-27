from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from ddisearch.ddi.models import CodeBook
from ddisearch.geo.models import Location, GeonamesContinent, GeonamesCountry


def resources_by_location(request, geonames_id=None, geo_coverage=None):
    # helper method to find DDI resources that explicitly reference
    # the specified place
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


def browse(request):
    # get a list of all continents represented by the data
    continent_codes = Location.objects.order_by('continent_code') \
                              .values('continent_code').distinct()
    codes = [loc['continent_code'] for loc in continent_codes
             if loc['continent_code'] is not None]
    places = GeonamesContinent.objects.filter(code__in=codes).order_by('name')

    # NOTE: could work, but may not always be represented directly
    # unless we force continents in during the load process
    # places = Location.objects.filter(feature_code='CONT').order_by('name')
    # find global resouces
    results = resources_by_location(request, geo_coverage='Global')

    return render(request, 'geo/browse.html',
                  {'places': places, 'results': results})

def browse_continent(request, continent):
    # get continent object so we can display name, etc
    cont = get_object_or_404(GeonamesContinent, code=continent)

    # TODO: possibly find list of country codes in the data and then
    # get country list from GeonamesCountry to ensure we don't miss things?
    country_codes = Location.objects.filter(continent_code=cont.code) \
                            .order_by('country_code') \
                            .values('country_code') \
                            .distinct()

    print country_codes.count()
    # find places in this continent
    codes = [loc['country_code'] for loc in country_codes
             if loc['country_code'] is not None]
    print codes
    places = GeonamesCountry.objects.filter(code__in=codes).order_by('name')

    # places = Location.objects.filter(continent_code=cont.code,
    #                                  feature_code__startswith='PCL') \
    #                          .order_by('name')

    print places.count()
    # TODO: probably need to filter by feature code to top-level items (countries?)

    # find resources that explicitly reference this place
    results = resources_by_location(request, geonames_id=cont.geonames_id)

    return render(request, 'geo/continent.html',
        {'continent': cont, 'places': places, 'results': results})

def browse_country(request, continent, country):
    # get continent object so we can display name, etc
    cont = get_object_or_404(GeonamesContinent, code=continent)
    # same for country
    country = get_object_or_404(GeonamesCountry, code=country)
    # find places in this continent

    places = Location.objects.filter(country_code=country.code, feature_code='ADM1') \
                             .order_by('name')

    # TODO: probably need to filter by feature code to appropriate country sublevel
    # TODO: check what ADM1 leaves out

    # find resources that explicitly reference this place
    results = resources_by_location(request, geonames_id=country.geonames_id)

    return render(request, 'geo/country.html',
        {'continent': cont, 'country': country, 'places': places,
         'results': results})

def browse_state(request, continent, country, state):
    # get continent object so we can display name, etc
    cont = get_object_or_404(GeonamesContinent, code=continent)
    # same for country
    country = get_object_or_404(GeonamesCountry, code=country)

    state = get_object_or_404(Location, state_code=state, feature_code='ADM1')
    # find places in this state
    places = Location.objects.filter(state_code=state.state_code).exclude(feature_code='ADM1')
    # TODO: feature code ?  maybe just group by at this point?

    # find resources that explicitly reference this place
    results = resources_by_location(request, geonames_id=state.geonames_id)

    return render(request, 'geo/state.html',
        {'continent': cont, 'country': country, 'state': state,
        'places': places, 'results': results})

def browse_substate(request, continent, country, state, geonames_id):
    # geographic location below state level
    # get continent object so we can display name, etc
    cont = get_object_or_404(GeonamesContinent, code=continent)
    # same for country
    country = get_object_or_404(GeonamesCountry, code=country)

    state = get_object_or_404(Location, state_code=state, feature_code='ADM1')

    location = get_object_or_404(Location, geonames_id=geonames_id)

    # find resources that explicitly reference this place
    results = resources_by_location(request, geonames_id=int(geonames_id))

    return render(request, 'geo/substate.html',
        {'continent': cont, 'country': country, 'state': state,
         'location': location, 'results': results})
