# -------------------------------------------------------------------------
#   Copyright (c) 2015-2017 AT&T Intellectual Property
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# -------------------------------------------------------------------------
#

import itertools
from collections import defaultdict

from dateutil import tz
from dateutil.parser import parse


def tuples_to_multi_val_dict(kvw_tuples, colnums=(0, 1)):
    """Given a list of k,v tuples, get a dictionary of the form k -> [v1,v2,...,vn]
    :param kvw_tuples: list of k,v,w tuples (e.g. [(k1,v1,a1), (k2,v2,a2), (k1,v3,a3), (k1,v4,a4)]
    :param colnums: column numbers
    :return: a dict of str:set, something like {k1: {v1, v3, v4}, k2: {v2}} or {k1: {a1, a3, a4}, k2: {a2}}
    """
    res = defaultdict(set)
    for x in kvw_tuples:
        key, val = x[colnums[0]], x[colnums[1]]
        res[key].add(val)
    return dict((k, set(v)) for k, v in res.items())


def tuples_to_dict(kvw_tuples, colnums=(0, 1)):
    """Given a list of k,v tuples, get a dictionary of the form k -> v
    :param kvw_tuples: list of k,v,w tuples (e.g. [(k1,v1,a1), (k2,v2,a2), (k3,v3,a3), (k1,v4,a4)]
    :param colnums: column numbers
    :return: a dict; something like {k1: v4, k2: v2, k3: v3} (note, k1 is repeated, so last val is retained)
    """
    return dict((x[colnums[0]], x[colnums[1]]) for x in kvw_tuples)


def utc_time_from_ts(timestamp):
    """Return corresponding UTC timestamp for a given ISO timestamp (or anything that parse accepts)"""
    return parse(timestamp).astimezone(tz.tzutc()).strftime('%Y-%m-%d %H:%M:%S')


def list_flatten(l):
    """Flatten a complex nested list of nested lists into a flat list"""
    return itertools.chain(*[list_flatten(j) if isinstance(j, list) else [j] for j in l])


text_to_symbol = {
    'greater': ">",
    'less': "<",
    'equal': "="
}


def decode_data(data):
    """
    Decode bytes to string
    """
    return data.decode(encoding='utf-8') if isinstance(data, bytes) else data
