FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install --yes curl
RUN apt-get install --yes wget
RUN apt-get install --yes bzip2
RUN apt-get install --yes iputils-ping
RUN apt-get install --yes libmpfr-dev
RUN apt-get install --yes libqt5printsupport5
RUN apt-get install --yes git

RUN rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/MiniZinc/MiniZincIDE/releases/download/2.1.6/MiniZincIDE-2.1.6-bundle-linux-x86_64.tgz\
  && tar xvzf /MiniZincIDE-2.1.6-bundle-linux-x86_64.tgz && rm -rf /MiniZincIDE-2.1.6-bundle-linux-x86_64.tgz

ENV PATH /MiniZincIDE-2.1.6-bundle-linux-x86_64:$PATH

RUN wget https://repo.continuum.io/archive/Anaconda3-5.1.0-Linux-x86_64.sh

RUN chmod 777 /Anaconda3-5.1.0-Linux-x86_64.sh

RUN /Anaconda3-5.1.0-Linux-x86_64.sh -b

RUN rm -rf /Anaconda3-5.1.0-Linux-x86_64.sh

ENV PATH /root/anaconda3/bin:$PATH

RUN git clone http://gerrit.onap.org/r/optf/osdf

CMD ["/bin/bash"]
#CMD ["bash", "-c", "/root/anaconda3/bin/jupyter lab --port=8181 --ip=10.172.161.6 --allow-root /vdns-plus-vfw-use-case/placement-minizinc.ipynb"]
