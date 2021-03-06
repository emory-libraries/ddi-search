# file ddisearch/ddi/views.py
#
# Copyright 2014 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import logging
from django.shortcuts import render
from django.http import Http404, HttpResponse
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from django.views.decorators.http import condition
from urllib import urlencode
from eulexistdb.exceptions import DoesNotExist
from eulexistdb.query import XmlQuery

from ddisearch.ddi import forms
from ddisearch.ddi.models import CodeBook, DistinctKeywords, DistinctTopics
from ddisearch.ddi.utils import ddi_lastmodified, ddi_etag, collection_lastmodified


logger = logging.getLogger(__name__)


# NOTE: exist query time reporting is disabled for now; as of
# eulexistdb 0.20 it is not available, but leaving the lines commented out
# because it may be enabled again for future versions of eXist.
# In the meantime, it is recommended to use django-debug-toolbar instead.


@condition(last_modified_func=collection_lastmodified)
def site_index(request):
    'Site index page; currently just displays the search form.'
    # find all documents that are new within some arbitrary window
    # currently using 90 days
    new_since = datetime.date.today() - datetime.timedelta(days=30)
    new_resources = CodeBook.objects \
          .filter(document_version__date__gte=new_since.isoformat()) \
          .only('id', 'title', 'document_version') \
          .order_by('-document_version__date')  # newest first
    # should we limit the list at some point?
    return render(request, 'site_index.html',
        {'form': forms.KeywordSearch(), 'new_resources': new_resources,
        'new_since': new_since})


def _sort_results(results, sort):
    # sort codebook queryset by the specified sort option
    # used for both search and browse by keyword/topic

    # simple sort mapping
    sort_map = {'title': 'title', 'relevance': '-fulltext_score'}
    if sort in sort_map:
        results = results.order_by(sort_map[sort])
    elif sort.startswith('date'):
        # either date sorting requires a raw xpath
        # check which type to determine if results should be ascending or not
        if sort == 'date (recent)':
            # when sorting most recent, use latest date in the record
            asc = False
            xpath = CodeBook.last_date_xpath
        elif sort == 'date (oldest)':
            # when sorting oldest, use earliest date in the record
            asc = True
            xpath = CodeBook.first_date_xpath
        results = results.order_by_raw(xpath, ascending=asc)

    # return the sorted queryset
    return results


def search(request):
    '''Search all available DDI content by keyword, title, summary, or source
    with sorting by relevance (default), title, or date.'''

    form = forms.KeywordSearch(request.GET)

    # if form is not valid but we have request data, supply default
    # per-page and sort options in case that makes the request valid
    # (e.g., support simple location search from resource page)
    if not form.is_valid() and request.GET and \
      not all(f in request.GET for f in ['per_page', 'sort']):
        form_data = request.GET.copy()
        form_data.update({'per_page': form.fields['per_page'].initial,
            'sort': form.fields['sort'].initial})

        form = forms.KeywordSearch(form_data)

    context = {'form': form}

    # if the form is valid, process and generate search results;
    # if not, fall through and display the form with validation errors
    if form.is_valid():
        search_opts = form.cleaned_data
        per_page = form.cleaned_data['per_page']
        sort = form.cleaned_data['sort']

        # build query based on search terms here
        results = CodeBook.objects.all()

        if 'keyword' in search_opts and search_opts['keyword']:
            keywords = search_opts['keyword']
            results = results.filter(fulltext_terms=keywords)
                             # .or_filter(fulltext_terms=keywords,
                             #            boostfields__fulltext_terms=keywords,
                             #            highlight=False    # disable highlighting in search results list
                             #            )

        if 'title' in search_opts and search_opts['title']:
            results = results.filter(title__fulltext_terms=search_opts['title'])
        if 'summary' in search_opts and search_opts['summary']:
            results = results.filter(abstract__fulltext_terms=search_opts['summary'])
        if 'source' in search_opts and search_opts['source']:
            results = results.filter(authors__fulltext_terms=search_opts['source'])
        if 'location' in search_opts and search_opts['location']:
            results = results.filter(location__fulltext_terms=search_opts['location'])

        # date search
        if 'start_date' in search_opts and 'end_date' in search_opts:
            sdate = search_opts['start_date']
            edate = search_opts['end_date']
            # NOTE: needs to handle date format variation (YYYY, YYYY-MM, etc)

            # single date search: start and end date should be the same;
            # using same logic as range to match any dates within that year
            # if only one of start or end is specified, results in an open range
            # i.e. anything after start date or anything before end date
            if sdate is not None:
                # restrict by start date
                # YYYY will be before any date in that year, e.g. "2001" >= "2001-11"
                results = results.filter(time_periods__date__gte='%04d' % sdate)
            if edate is not None:
                # restrict by end date
                # convert to end of year to catch any date variants within that year
                # e.g. 2001-12-31 will always come after 2001-04, etc
                edate = "%04d-12-31" % edate
                results = results.filter(time_periods__date__lte=str(edate))

            # if no keyword search terms are present, default sort by relevance
            # is nonsensical; sort by most recent date first instead
            if form.all_search_terms == '' and sort == form.fields['sort'].initial:
                # since we're doing a date search, sort by most recent date first
                sort = 'date (recent)'
                # simplest way to update form data/display is to re-init
                # and override the defualt sort option specified in the GET params
                GET_data = request.GET.copy()
                GET_data['sort'] = sort
                form = forms.KeywordSearch(GET_data)
                # validate to make cleaned data available for generating pagination args
                form.is_valid()
                # update version of the form that will be passed to the template
                context['form'] = form

        # To make relevance scores more meaningful, run *all* search terms
        # from any field against the full text and boost fields
        # *IF* we are doing a fultext search (i.e., not a date-only query)
        if form.all_search_terms:
            results = results.or_filter(fulltext_terms=form.all_search_terms,
                                        boostfields__fulltext_terms=form.all_search_terms,
                                        highlight=False    # disable highlighting in search results list
                                        )
        # FIXME: redundancy in boost fields seems to generate very high relevance scores
        # see if we can avoid repeating filters (e.g. search by title then search again in boost fields)

        # only return fields needed to generate search results
        results = results.only('title', 'abstract', 'keywords', 'topics',
                               'authors', 'time_periods', 'fulltext_score',
                               'id')
        # sort the queryset based on the requested sort option
        results = _sort_results(results, sort)

        paginator = Paginator(results, per_page, orphans=5)

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

        url_args = form.cleaned_data
        # clear out blank fields
        # (in particular, without this numeric date fields come through as None)
        for k in list(url_args.keys()):
            if url_args[k] is None or url_args[k] == '':
                del url_args[k]
        url_params = urlencode(url_args)
        # url params for changing chunk size
        partial_args = url_args.copy()
        del partial_args['per_page']
        rechunk_params = urlencode(partial_args)
        # url params for changing sort
        partial_args = url_args.copy()
        del partial_args['sort']
        sort_params = urlencode(partial_args)

        context.update({'keywords': search_opts.get('keywords', ''),
            'results': results,
            # 'querytime': [results.object_list.queryTime()],
            'url_params': url_params,
            'per_page': int(per_page),
            'rechunk_params': rechunk_params,
            'per_page_options': forms.KeywordSearch.PER_PAGE_OPTIONS,
            'sort': sort,
            'sort_params': sort_params,
            'sort_options': forms.KeywordSearch.SORT_OPTIONS})

    # if form is not valid but *nothing* was submitted (i.e., new search)
    # don't consider the form to be invalid, but just display it
    elif not request.GET:
        # re-init as new form without any validation errors
        context['form'] = forms.KeywordSearch()

    return render(request, 'ddi/search.html', context)


@condition(etag_func=ddi_etag, last_modified_func=ddi_lastmodified)
def resource(request, agency, id):
    '''Display a single DDI document with all relevant details.  Uses
    id number and agency to identify a single document; returns a 404
    if no record matching the specified agency and id is found.

    :param agency: agency identifier (from document title statement)
    :param id: id number (from title statement)
    '''
    try:
        res = CodeBook.objects.get(id__val=id, id__agency=agency)
    except DoesNotExist:
        raise Http404

    return render(request, 'ddi/resource.html', {'resource': res})


@condition(etag_func=ddi_etag, last_modified_func=ddi_lastmodified)
def resource_xml(request, agency, id):
    '''Display the raw DDI XML for a single document; returns a 404
    if no record matching the specified agency and id is found.

    :param agency: agency identifier (from document title statement)
    :param id: id number (from title statement)
    '''
    try:
        # include document name so we can preset for download,
        # to preserve filename if reloaded
        res = CodeBook.objects.all() \
                      .also('document_name') \
                      .get(id__val=id, id__agency=agency)
    except DoesNotExist:
        raise Http404

    xml = res.serialize(pretty=True)
    response = HttpResponse(xml, content_type='application/xml')
    response['Content-Disposition'] = 'filename="%s"' % res.document_name
    return response


@condition(last_modified_func=collection_lastmodified)
def browse_terms(request, mode):
    '''Browse list of distinct keywords or topics (depending on the
    specified mode), or browse documents by keyword or topic if a term
    is specified as a request parameter.

    .. Note::

      Browse by keyword is **deprecated** because there are so many
      keywords that it is not useful.

    :param mode: keywords or topics
    '''

    fltr = mode.rstrip('s')
    term = request.GET.get(fltr, None)
    label = mode.title()
    context = {'mode': mode, 'fltr': fltr, 'term': term, 'label': label}

    url_args = {}
    if term:
        label = label.rstrip('s')
        # url params to preserve when jumping to another page
        url_args[fltr] = term

    if term is not None:
        form = forms.BrowseTerms(request.GET)
        context['form'] = form

        # validation required before accessing cleaned data
        if form.is_valid():
            per_page = form.cleaned_data['per_page']
            sort = form.cleaned_data['sort']
        else:
            # if not valid, init as new and use defaults
            form = forms.SearchOptions()
            per_page = form.fields['per_page'].initial
            sort = form.fields['sort'].initial

        # add sort & per page to url args for use with pagination
        url_args.update({'per_page': per_page, 'sort': sort})

        if mode == 'keywords':
            search_field = 'keywords__fulltext_terms'
            # force search term to lower case to help with case-insensitivity
            term = term.lower()
        elif mode == 'topics':
            # make sure to only browse against *local* topics
            search_field = 'local_topics__fulltext_terms'

        results = CodeBook.objects \
            .filter(**{search_field: XmlQuery(term=term)}) \
            .only('title', 'abstract', 'keywords', 'topics',
                  'authors', 'time_periods', 'id')

        # sort the queryset based on the requested sort option
        results = _sort_results(results, sort)

    else:
        per_page = 50

        if mode == 'keywords':
            results = DistinctKeywords.objects.all().distinct() \
                                      .order_by_raw(DistinctKeywords.text_xpath)

            # NOTE: returns a list of string, not xml objects

        elif mode == 'topics':
            results = DistinctTopics.objects.all() \
                                    .also_raw(count=DistinctTopics.count_xpath,
                                              text=DistinctTopics.text_xpath) \
                                    .order_by_raw(DistinctTopics.text_xpath)

    paginator = Paginator(results, per_page, orphans=5)

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

    context.update({'results': results, 'url_params': urlencode(url_args)})
                    # 'querytime': [results.object_list.queryTime()]})

    return render(request, 'ddi/browse_terms.html', context)
