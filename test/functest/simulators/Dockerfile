FROM ubuntu:16.04

RUN apt-get update -y \
    && apt-get install -y vim unzip wget libmpfr-dev \
    && apt-get install -y git libqt5printsupport5 build-essential \
    && apt-get install -y python3 python3-setuptools python3-dev \
    && easy_install3 pip \
    && pip install --upgrade virtualenv pip wheel

RUN ln -s /usr/bin/python3.5 /usr/bin/python
ADD requirements.txt /requirements.txt
RUN pip install -r requirements.txt
ADD sim /sim

CMD cd /sim && python oof_dependencies_simulators.py > simulator-logs 2>&1