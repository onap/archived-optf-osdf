# -------------------------------------------------------------------------
#   Copyright (C) 2021 Wipro Limited.
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


class ConfigClient(object):

    subclasses = {}

    @classmethod
    def register_subclass(cls, type):
        def decorator(subclass):
            cls.subclasses[type] = subclass
            return subclass

        return decorator

    @classmethod
    def create(cls, type):
        if type not in cls.subclasses:
            raise ValueError('Bad config client type {}'.format(type))

        return cls.subclasses[type]()
