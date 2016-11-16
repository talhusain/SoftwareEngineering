FROM python:3.5

MAINTAINER Adam Furbee <adam.furbee@gmail.com>

# Install uWSGI
RUN pip install uwsgi


# install git
RUN apt-get -y update && apt-get -y install git

# install nginx
ENV NGINX_VERSION 1.10.2-1~jessie
RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
    && echo "deb http://nginx.org/packages/debian/ jessie nginx" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install --no-install-recommends --no-install-suggests -y \
                        ca-certificates \
                        nginx=${NGINX_VERSION} \
                        nginx-module-xslt \
                        nginx-module-geoip \
                        nginx-module-image-filter \
                        nginx-module-perl \
                        nginx-module-njs \
                        gettext-base \
    && rm -rf /var/lib/apt/lists/*

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

# install code and requirements
add . /home/docker/code/
RUN pip3 install -r /home/docker/code/requirements.txt

# Make NGINX run on the foreground
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
# Remove default configuration from Nginx
RUN rm /etc/nginx/conf.d/default.conf
# Copy the modified Nginx conf
COPY nginx.conf /etc/nginx/conf.d/

# Install Supervisord
RUN apt-get update && apt-get install -y supervisor
# Custom Supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /home/docker/code

CMD ["/usr/bin/supervisord"]