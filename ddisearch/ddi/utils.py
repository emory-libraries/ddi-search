# file ddisearch/ddi/utils.py
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

from datetime import datetime
from django.conf import settings
from ddisearch.ddi.models import CodeBook


def ddi_lastmodified(request, agency, id):
    """Get the last modification time for a DDI document in eXist by agency and id.
    Used to generate last-modified header for views based on a single EAD document.

    :param id: eadid
    :param preview: load document from preview collection; defaults to False
    :rtype: :class:`datetime.datetime`
    """
    # get document last modified by
    res = CodeBook.objects.filter(id__val=id, id__agency=agency).only('last_modified')
    if res.count():
        return exist_datetime_with_timezone(res[0].last_modified)

def ddi_etag(request, agency, id):
    """Generate a DDI Codebook document (specified by agency and id) by
    requesting a SHA-1 checksum of the entire DDI xml document from eXist.

    :param request:  http request
    :param agency:  agency code
    :param id:  id number
    :rtype: string
    """
    res = CodeBook.objects.filter(id__val=id, id__agency=agency).only('hash')
    # don't error if not found, but just let it fall through to view
    if res.count():
        return res[0].hash

def collection_lastmodified(request, *args, **kwargs):
    """Get the last modification time for the entire eXist collection.
    Used to generate last-modified header for views that are based on
    the entire collection.

    If no documents are found in eXist, no value is returned and django
    will not send a Last-Modified header.
    """
    # most recently modified document in the eXist collection
    res = CodeBook.objects.order_by('-last_modified').only('last_modified')
    if res.count():
        return exist_datetime_with_timezone(res[0].last_modified)


def exist_datetime_with_timezone(dt):
    """Convert an 'offset-naive' datetime object into an 'offset-aware' datetime
    using a configured timezone.

    The current version of xmlrpclib ignores timezones, which messes up dates
    (e.g., when used for last-modified header).  This function uses a configured
    timezone from django settings to convert a datetime to offset-aware.
    """
    tz = settings.EXISTDB_SERVER_TIMEZONE
    # use the exist time and configured timezone to create a timezone-aware datetime
    return datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute,
                    dt.second, dt.microsecond, tz)
