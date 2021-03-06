
# file ddisearch/geo/geonames.py
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

# simple client to interact with geonames api, since
# the geopy client is too limited and doesn't expose all OPTIONS:

import requests


class GeonamesException(Exception):
    pass


class GeonamesClient(object):
    '''Simple GeoNames.org client for searching and geocoding terms.

    :param username
    '''

    base_url = 'http://api.geonames.org'

    def __init__(self, username):
        self.username = username

    def geocode(self, query=None, name=None, name_equals=None,
                exactly_one=True, country_bias=None,
                country=None, feature_code=None,
                feature_class=None, admin_code1=None):
        '''Implements the `GeoNames.org search API`_.  Generally, you should
        supply (only) one of query, name, or name equals, but that is not strictly
        required (e.g., if you want to look up a state or region by country code and
        admin code).

        .. _GeoNames.org search API: http://www.geonames.org/export/geonames-search.html

        :param query: search over all attributes of a place
        :param name:  search by place name only
        :param name_equals:  search by exact place name
        :param exactly_one: return only the first match (defaults to true);
           if false, returns the full list of results
        :param country_bias: list matches from the specified country first;
           countries should be specified by two-letter codes
        :param country: only return matches from the country;
           countries should be specified by two-letter codes
        :param feature_code: restrict results to one or more GeoNames feature codes
        :param feature_class: restrict results to one or more GeoNames feature classes
        :param feature_class: restrict results by the specified admin code (generally
            should be used with country bias)
        '''
        api_url =  '%s/searchJSON' % self.base_url
        params = {'username': self.username, 'orderBy': 'relevance'}

        # query term (really only expect one of these)
        if query:
            params['query'] = query
        if name:
            params['name'] = name
        if name_equals:
            params['name_equals'] = name_equals

        if exactly_one:
            params['maxRows'] = 1
        if country_bias:
            params['countryBias'] = country_bias
        if country:
            params['country'] = country
        if admin_code1:
            params['adminCode1'] = admin_code1
        if feature_code:
            # TODO: check that this works correctly for list of params
            params['featureCode'] = feature_code
        if feature_class:
            params['featureClass'] = feature_class

        r = requests.get(api_url, params=params)
        result = r.json()
        if result['totalResultsCount']:
            if exactly_one:
                return GeonamesResult(result['geonames'][0])
            else:
                return [GeonamesResult(res) for res in result['geonames']]

    def get_by_id(self, geonames_id):
        '''Get information about a specific GeoNames ID.

        :param geonames_id: geonames identifier to lookup
        :returns: :class:`GeonamesResult`
        '''
        params = {'username': self.username, 'geonameId': geonames_id}
        api_url = '%s/getJSON' % self.base_url
        resp = requests.get(api_url, params=params)
        if resp.status_code != requests.codes.ok:
            raise GeonamesException('Error retrieving GeoNames %s: %s' % \
                                    (geonames_id, resp.content))
        # geonames returns 200 for not found, have to check contents
        data = resp.json()
        if 'status' in data and data['status']['value'] == 15:
            raise GeonamesException('Error retreving GeoNames %s: %s' % \
                            (geonames_id, data['status']['message']))
        return GeonamesResult(data)


class GeonamesResult(object):
    '''Simple result class for locations returned by geonames search,
    compatible with :mod:`geopy` results.'''

    def __init__(self, data):
        self.latitude = data['lat']
        self.longitude = data['lng']
        self.raw = data

    def __unicode__(self):
        return self.raw['name']

    def __repr__(self):
        return u'<GeonamesResult %s>' % unicode(self)


# sample result to use for tests

# {"totalResultsCount":5325,"geonames":[{"countryId":"2635167","adminCode1":"ENG","countryName":"United Kingdom","fclName":"city, village,...","countryCode":"GB","lng":"-0.12574","fcodeName":"capital of a political entity","toponymName":"London","fcl":"P","name":"London","fcode":"PPLC","geonameId":2643743,"lat":"51.50853","adminName1":"England","population":7556900},{"countryId":"2635167","adminCode1":"ENG","countryName":"United Kingdom","fclName":"city, village,...","countryCode":"GB","lng":"-0.09184","fcodeName":"seat of a third-order administrative division","toponymName":"City of London","fcl":"P","name":"City of London","fcode":"PPLA3","geonameId":2643741,"lat":"51.51279","adminName1":"England","population":7556900}]}
