ARG CASUAL_VERSION=1.8.5

FROM casual/middleware:${CASUAL_VERSION} AS base
USER root

FROM base AS builder
RUN yum -y install gcc-toolset-14-gcc-c++
ADD client/main.cpp /tmp/main.cpp
RUN source /opt/rh/gcc-toolset-14/enable && cd /tmp && g++ -std=c++20 -I/opt/casual/include -L/opt/casual/lib -lcasual-xatmi -o tpcall-client main.cpp

FROM base AS runtime
RUN yum -y install python3.12 python3.12-pip
RUN rm /opt/casual/python/casual/__init__.py

ENV CASUAL_DOMAIN_HOME=/home/casual
RUN mkdir -p $CASUAL_DOMAIN_HOME/logs
RUN mkdir -p $CASUAL_DOMAIN_HOME/configuration
RUN chown -R casual $CASUAL_DOMAIN_HOME
ADD docker/casual-performance/requirements.txt requirements.txt
# RUN python3 -m venv /home/casual/venv && source /home/casual/venv/bin/activate && pip install -r requirements.txt 
RUN pip3 install -r requirements.txt 

USER casual
RUN echo "source /opt/casual/etc/bash_completion.d/casual" >> /home/casual/.bashrc
ADD docker/casual-performance/*.py $CASUAL_DOMAIN_HOME/
ADD casual $CASUAL_DOMAIN_HOME/python/casual
COPY --from=builder /tmp/tpcall-client ${CASUAL_DOMAIN_HOME}/

ENV CASUAL_DOMAIN_HOME=/home/casual
ENV CASUAL_LOG_PATH=${CASUAL_DOMAIN_HOME}/logs/casual.log
ENV CASUAL_LOG="(error|warning|information)"
ENV PYTHONPATH=/opt/casual/python:${CASUAL_DOMAIN_HOME}/python/

WORKDIR $CASUAL_DOMAIN_HOME
