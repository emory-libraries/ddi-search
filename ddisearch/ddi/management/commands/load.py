# file ddisearch/ddi/management/commands/load.py
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

import logging
import os
from optparse import make_option
import re
import sys
import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from progressbar import ProgressBar, Bar, Percentage, ETA, SimpleProgress

from eulexistdb.db import ExistDB, ExistDBException
from eulxml.xmlmap import load_xmlobject_from_file

from ddisearch.ddi.models import CodeBook, Topic
from ddisearch.ddi.topics import topic_mappings, conditional_topics
from ddisearch.geo.utils import CodebookGeocoder

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<filename filename filename ...>'
    help = '''Loads XML files into the configured eXist collection.
The local copy will be *removed* after it is successfully loaded.'''

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', '-n',
            dest='dryrun',
            action='store_true',
            help='''Report on what would be done, but don't delete any files'''
        ),
    )

    v_normal = 1
    def handle(self, *files, **options):
        verbosity = int(options.get('verbosity', self.v_normal))

        # check for required settings
        if not hasattr(settings, 'EXISTDB_ROOT_COLLECTION') or \
           not settings.EXISTDB_ROOT_COLLECTION:
            raise CommandError("EXISTDB_ROOT_COLLECTION setting is missing")
            return

        self.db = ExistDB()
        self.cbgeocoder = CodebookGeocoder()

        # initalize progress bar
        pbar = None
        total = len(files)
        # init progress bar if processing enough files, running on a terminal
        if total >= 10 and os.isatty(sys.stderr.fileno()):
            widgets = [Percentage(), ' (', SimpleProgress(), ')',
                       Bar(), ETA()]
            pbar = ProgressBar(widgets=widgets, maxval=total).start()

        errored = 0
        loaded = 0
        for f in files:
            success = False

            if pbar:
                pbar.update(errored + loaded)

            try:
                # full path location where file will be loaded in exist db collection
                dbpath = settings.EXISTDB_ROOT_COLLECTION + "/" + os.path.basename(f)
                # TODO: any error checking? validation?

                start = time.time()
                cb = load_xmlobject_from_file(f, CodeBook)
                logger.debug('%s loaded as xml in %f sec' % (f, time.time() - start))

                start = time.time()
                self.prep(cb)
                logger.debug('%s prepped in %f sec' % (f, time.time() - start))
                # load to eXist from string since DDI documents aren't that large,
                # rather than reloading the file
                if not options.get('dryrun', False):
                    start = time.time()
                    success = self.db.load(cb.serialize(pretty=True), dbpath, overwrite=True)
                    logger.debug('%s loaded to eXist in %f sec' % (f, time.time() - start))

            except IOError as e:
                self.stdout.write("Error opening %s: %s" % (f, e))
                errored += 1

            except ExistDBException as e:
                self.stdout.write("Error: failed to load %s to eXist" % f)
                self.stdout.write(e.message())
                errored += 1

            if not options.get('dryrun', False) and success:
                loaded += 1
                if verbosity > self.v_normal:
                    self.stdout.write("Loaded %s as %s" % (f, dbpath))

                try:
                    os.remove(f)
                except OSError as e:
                    self.stdout.write('Error removing %s: %s' % (f, e))

        if pbar:
           pbar.finish()

        # output a summary of what was done if more than one file was processed
        if verbosity >= self.v_normal:
            if loaded > 1:
                self.stdout.write("%d document%s loaded" % \
                                  (loaded, 's' if loaded != 1 else ''))
            if errored > 1:
                self.stdout.write("%d document%s with errors" % \
                                  (errored, 's' if errored != 1 else ''))

    topic_id = re.compile('^(?P<org>[A-Z]+)[ .](?P<id>[IVX]+(\.[A-Z](\.[0-9]+(\.[a-z]+)?)?)?)')


    def prep(self, cb):
        # do any prep work or cleanup that needs to be done
        # before loading to exist
        self.local_topics(cb)
        self.clean_dates(cb)
        self.cbgeocoder.code_locations(cb)

    def icpsr_topic_id(self, topic):
        # generate icpsr topic id in the format needed for lookup in our
        # topic dictionary; returns None if not an ICPSR topic
        m = self.topic_id.match(topic)
        if m:
            match_info = m.groupdict()
            if match_info['org'] == 'ICPSR':
                return '%(org)s.%(id)s' % match_info

    def local_topics(self, cb):
        # convert ICPSR topics to local topics
        for t in cb.topics:
            topic_id = self.icpsr_topic_id(t.val)
            if topic_id is not None:
                new_topic = topic_mappings.get(topic_id, None)
                if new_topic:
                    cb.topics.append(Topic(val=new_topic,
                        vocab='local'))

                # conditional topics if the geographic coverage is global
                if topic_id in conditional_topics['global'] and \
                  'Global' in [unicode(gc) for gc in cb.geo_coverage]:
                    cb.topics.append(Topic(val=conditional_topics['global'][topic_id],
                                           vocab='local'))

    def clean_dates(self, cb):
        # clean up dates so we can search consistently on 4-digit years
        # or more; dates should be YYYY, YYYY-MM, or YYYY-MM-DD
        prev_date = None
        for d in cb.time_periods:
            # special case: two-digit date as second date in a cycle
            # interpret as month on the year that starts the cycle
            if d.event == 'end' and d.cycle == prev_date.cycle and \
                    len(d.date) == 2:
               d.date = '%04d-%02d' % (int(prev_date.date), int(d.date))

            elif len(d.date) < 4:
                d.date = '%04d' % int(d.date)

            # store current date as previous date for next loop, in case
            # we need to clean up an end date in a cycle
            prev_date = d


