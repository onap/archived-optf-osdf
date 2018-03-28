# -------------------------------------------------------------------------
#   Copyright (c) 2018 AT&T Intellectual Property
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
import unittest

from osdf.utils import programming_utils as putil


class TestProgrammingUtils(unittest.TestCase):

    def test_namedtuple_with_defaults_list(self):
        MyType1 = putil.namedtuple_with_defaults('MyType1', 'afield bfield', ['a', 'b'])
        res = MyType1()
        assert res.afield == 'a'

    def test_namedtuple_with_defaults_dict(self):
        MyType2 = putil.namedtuple_with_defaults('MyType2', 'afield bfield', {'afield': 'x', 'bfield': 'y'})
        res = MyType2()
        assert res.afield == 'x'
        res = MyType2('blah')
        assert res.afield == 'blah'
        res = MyType2('a', 'bar')
        assert res.bfield == 'bar'

    def test_inverted_dict(self):
        orig = {'x': 'a', 'y': 'b', 'z': 'a'}
        res = putil.inverted_dict(['x', 'y', 'z'], orig)
        assert set(res['a']) == {'x', 'z'} and res['b'] == ['y']


if __name__ == "__main__":
    unittest.main()
