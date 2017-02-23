FROM ubuntu:16.04
MAINTAINER Brendan Cox
WORKDIR /app/blastor

RUN echo 'deb http://deb.torproject.org/torproject.org trusty main' | tee /etc/apt/sources.list.d/torproject.list
RUN gpg --keyserver keys.gnupg.net --recv 886DDD89
RUN gpg --export A3C4F0F979CAA22CDBA8F512EE8CBC9E886DDD89 | apt-key add -

RUN apt-get update && apt-get install -y tor privoxy python3 python3-setuptools inetutils-ping curl less telnet netcat
# apt-get install python3-pip requires 203MB of space.  Just use easy_install3 for now
# if you really need pip3 and don't need to build packages, just easy_install3 pip
RUN easy_install3 aiohttp

RUN bash -c "echo 'ControlPort 9051' >> /etc/tor/torrc"
RUN bash -c "echo 'CookieAuthentication 0' >> /etc/tor/torrc"

RUN bash -c "echo 'listen-address    :8118' >> /etc/privoxy/config"
RUN bash -c "echo 'forward-socks5   /   127.0.0.1:9050 .' >> /etc/privoxy/config"
RUN bash -c "echo 'debug 1' >> /etc/privoxy/config"

expose 8118
expose 8080

COPY master_blastor.py ./
CMD python3 /app/blastor/master_blastor.py