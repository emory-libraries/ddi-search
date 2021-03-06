# file ddisearch/ddi/topics.py
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

# mapping from ICPSR topic headings to more general local topics
# provided by Rob O'Reilly

# use variables for the topic strings to ensure they are exactly the same throughout
CENSUS_AND_DEMOGRAPHY = 'Census and Demography'
SOCIAL_INDICATORS = 'Social Indicators'
INTERNATIONAL_RELATIONS = 'International Relations'
ECON_AND_FINANCIAL = 'Economic and Financial'
INTL_POLIT_ECON = 'International Political Economy'
EDUCATION = 'Education'
ELECTIONS = 'Elections and Electoral Politics'
ENVIRONMENT = 'Environment'
GOVERNANCE = 'Governance and Institutional Quality'
HEALTH = 'Health'
COURTS_CRIMINAL_JUSTICE = 'Courts, Criminal Justice and Violence'
PUBLIC_OPINION = 'Public Opinion'
SOCIAL_INDICATORS = 'Social Indicators'

# NOTE: ICPSR topic ids without a corresponding topic will not be
# given a local topic, and will not be displayed in the site topic browse

topic_mappings = {
    'ICPSR.I': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.a': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.b': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.c': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.d': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.e': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.1.f': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.2': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.3': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.A.4': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.I.B': CENSUS_AND_DEMOGRAPHY,

    'ICPSR.II': SOCIAL_INDICATORS,
    'ICPSR.II.A': SOCIAL_INDICATORS,
    'ICPSR.II.A.1': SOCIAL_INDICATORS,
    'ICPSR.II.A.2': SOCIAL_INDICATORS,
    'ICPSR.II.B': SOCIAL_INDICATORS,
    'ICPSR.II.C': SOCIAL_INDICATORS,

    'ICPSR.III': INTERNATIONAL_RELATIONS,
    'ICPSR.III.A': INTERNATIONAL_RELATIONS,
    'ICPSR.III.B': INTERNATIONAL_RELATIONS,

    'ICPSR.IV': ECON_AND_FINANCIAL,
    'ICPSR.IV.A': ECON_AND_FINANCIAL,
    'ICPSR.IV.B': ECON_AND_FINANCIAL,
    'ICPSR.IV.C': ECON_AND_FINANCIAL,

    'ICPSR.V': EDUCATION,
    'ICPSR.V.A': EDUCATION,
    'ICPSR.V.B': EDUCATION,

    'ICPSR.VI': ELECTIONS,
    'ICPSR.VI.A': ELECTIONS,
    'ICPSR.VI.B': INTERNATIONAL_RELATIONS,

    'ICPSR.VII': ENVIRONMENT,

    'ICPSR.VIII': GOVERNANCE,
    'ICPSR.VIII.A': GOVERNANCE,
    'ICPSR.VIII.B': GOVERNANCE,
    'ICPSR.VIII.B.1': GOVERNANCE,
    'ICPSR.VIII.B.2': GOVERNANCE,
    'ICPSR.VIII.C': GOVERNANCE,

    'ICPSR.IX': HEALTH,

    'ICPSR.X': '',
    'ICPSR.X.A': '',

    'ICPSR.X.A.1': ELECTIONS,
    'ICPSR.X.A.2': '',
    'ICPSR.X.A.3': '',
    'ICPSR.X.B': '',

    'ICPSR.XI': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.A': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.B': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.B.1': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.B.2': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.C': INTERNATIONAL_RELATIONS,
    'ICPSR.XI.D': INTERNATIONAL_RELATIONS,

    'ICPSR.XII': COURTS_CRIMINAL_JUSTICE,

    'ICPSR.XIII': ELECTIONS,
    'ICPSR.XIII.A': ELECTIONS,
    'ICPSR.XIII.A.1': ELECTIONS,
    'ICPSR.XIII.A.2': INTERNATIONAL_RELATIONS,
    'ICPSR.XIII.A.3': INTERNATIONAL_RELATIONS,
    'ICPSR.XIII.B': INTERNATIONAL_RELATIONS,

    'ICPSR.XIV': ELECTIONS,
    'ICPSR.XIV.A': ELECTIONS,
    'ICPSR.XIV.A.1': ELECTIONS,
    'ICPSR.XIV.A.2': ELECTIONS,
    'ICPSR.XIV.A.2.a': ELECTIONS,
    'ICPSR.XIV.A.2.b': ELECTIONS,
    'ICPSR.XIV.A.3': ELECTIONS,
    'ICPSR.XIV.A.3.a': ELECTIONS,
    'ICPSR.XIV.A.3.b': ELECTIONS,
    'ICPSR.XIV.A.4': ELECTIONS,
    'ICPSR.XIV.A.4.a': ELECTIONS,
    'ICPSR.XIV.A.4.b': ELECTIONS,
    'ICPSR.XIV.B': ELECTIONS,
    'ICPSR.XIV.B.1': ELECTIONS,
    'ICPSR.XIV.B.2': ELECTIONS,
    'ICPSR.XIV.C': PUBLIC_OPINION,
    'ICPSR.XIV.C.1': PUBLIC_OPINION,
    'ICPSR.XIV.C.2': PUBLIC_OPINION,
    'ICPSR.XIV.C.3': PUBLIC_OPINION,
    'ICPSR.XIV.C.3.a': PUBLIC_OPINION,
    'ICPSR.XIV.C.3.b': PUBLIC_OPINION,
    'ICPSR.XIV.C.3.c': PUBLIC_OPINION,
    'ICPSR.XIV.D': ELECTIONS,

    'ICPSR.XV': '',
    'ICPSR.XV.A': '',
    'ICPSR.XV.B': '',
    'ICPSR.XVI': SOCIAL_INDICATORS,
    'ICPSR.XVI.A': SOCIAL_INDICATORS,
    'ICPSR.XVI.B': SOCIAL_INDICATORS,

    'ICPSR.XVII': SOCIAL_INDICATORS,
    'ICPSR.XVII.A': SOCIAL_INDICATORS,
    'ICPSR.XVII.B': SOCIAL_INDICATORS,
    'ICPSR.XVII.C': SOCIAL_INDICATORS,
    'ICPSR.XVII.C.1': SOCIAL_INDICATORS,
    'ICPSR.XVII.C.2': SOCIAL_INDICATORS,
    'ICPSR.XVII.D': SOCIAL_INDICATORS,
    'ICPSR.XVII.E': COURTS_CRIMINAL_JUSTICE,
    'ICPSR.XVII.F': SOCIAL_INDICATORS,
    'ICPSR.XVII.G': CENSUS_AND_DEMOGRAPHY,
    'ICPSR.XVII.H': SOCIAL_INDICATORS,
    'ICPSR.XVII.I': '',

    'ICPSR.XVIII': '',

    'ICPSR.XIX': ''
}

# conditional mappings
conditional_topics = {
    'global': {
        'ICPSR.IV': INTL_POLIT_ECON,
        'ICPSR.IV.A': INTL_POLIT_ECON,
        'ICPSR.IV.B': INTL_POLIT_ECON,
        'ICPSR.IV.C': INTL_POLIT_ECON,

        'ICPSR.VI': INTERNATIONAL_RELATIONS,
        'ICPSR.XIII': INTERNATIONAL_RELATIONS,
    }

}


