FROM nginxinc/nginx-unprivileged:1-alpine
LABEL maintainer="Chris Weinell"
COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
COPY ./uwsgi_params /etc/nginx/uwsgi_params
COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

USER root

RUN mkdir -p /var/www/staticfiles/ && \
    chmod 755 /var/www/staticfiles/ && \
    chown -R ec2-user:ec2-user /var && \
    chmod -R 755 /var && \
    touch /etc/nginx/conf.d/default.conf && \
    chown nginx:nginx /etc/nginx/conf.d/default.conf && \
    chmod +x /run.sh

VOLUME /var/www/staticfiles/

USER nginx

CMD ["/run.sh"]
