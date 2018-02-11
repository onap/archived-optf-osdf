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

import collections
import itertools


class DotDict(dict):
    """A dot-dict mixin to be able to access a dictionary via dot notation
    source: https://stackoverflow.com/questions/2352181/how-to-use-a-dot-to-access-members-of-dictionary
    """
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class MetaSingleton(type):
    """Singleton class (2nd Chapter) from Learning Python Design Patterns - 2nd ed.
    Chetan Giridhar, Packt Publ. 2016"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def namedtuple_with_defaults(typename, field_names, default_values=()):
    """A namedtuple with default values -- Stack overflow recipe from Mark Lodato
    http://stackoverflow.com/questions/11351032/named-tuple-and-optional-keyword-arguments
    :param typename: Name for the class (same as for namedtuple)
    :param field_names: Field names (same as for namedtuple)
    :param default_values: Can be specified as a dictionary or as a list
    :return: New namedtuple object
    """
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**default_values)
    else:
        prototype = T(*default_values)
    T.__new__.__defaults__ = tuple(prototype)
    return T


def dot_notation(dict_like, dot_spec):
    """Return the value corresponding to the dot_spec from a dict_like object
    :param dict_like: dictionary, JSON, etc.
    :param dot_spec: a dot notation (e.g. a1.b1.c1.d1 => a1["b1"]["c1"]["d1"])
    :return: the value referenced by the dot_spec
    """
    attrs = dot_spec.split(".")  # we split the path
    parent = dict_like.get(attrs[0])
    children = ".".join(attrs[1:])
    if not (parent and children):  # if no children or no parent, bail out
        return parent
    if isinstance(parent, list):  # here, we apply remaining path spec to all children
        return [dot_notation(j, children) for j in parent]
    elif isinstance(parent, dict):
        return dot_notation(parent, children)
    else:
        return None


def list_flatten(l):
    """
    Flatten a complex nested list of nested lists into a flat list (DFS).
    For example, [ [1, 2], [[[2,3,4], [2,3,4]], [3,4,5, 'hello']]]
    will produce [1, 2, 2, 3, 4, 2, 3, 4, 3, 4, 5, 'hello']
    """
    return list(itertools.chain(*[list_flatten(j) if isinstance(j, list) else [j] for j in l]))


def inverted_dict(keys: list, key_val_dict: dict) -> dict:
    """
    Get val -> [keys] mapping for the given keys using key_val_dict
    :param keys: the keys we are interested in (a list)
    :param key_val_dict: the key -> val mapping
    :return: inverted dictionary of val -> [keys] (for the subset dict of given keys)
    """
    res = {}
    all_tuples = ((k, key_val_dict[k] if k in key_val_dict else 'no-parent-' + k) for k in keys)
    for k, v in all_tuples:
        if v in res:
            res[v].append(k)
        else:
            res[v] = [k]
    # making sure to remove duplicate keys
    res = dict((v, list(set(k_list))) for v, k_list in res.items())
    return res
