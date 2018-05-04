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

test:
	rm -f /tmp/cl.*.log
	python CommonLogger.py
	rm -f /tmp/cl.*.log
	python3 CommonLogger.py -k -v
	# python CommonLogger_test.py
	# python3 CommonLogger_test.py

# STAGEDIR is overridden in ../makefile
STAGEDIR=/tmp

build: CommonLogger.html
	mkdir -p $(STAGEDIR)/python
	cp -p *.py *.config *.md CommonLogger.html $(STAGEDIR)/python
	chmod a+x $(STAGEDIR)/python/*.py

CommonLogger.html: CommonLogger.py
	pydoc -w ./CommonLogger.py

clean:
	rm -rf __pycache__ *.pyc CommonLogger.html
	rm -rf *~ 
