FROM alpine:3.9

RUN apk add --no-cache postfix postfix-mysql rsyslog ca-certificates && \
    update-ca-certificates

COPY rsyslog.conf /etc/
COPY *.cf /etc/postfix/
COPY docker-entrypoint.sh reload-postfix.sh /

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD /usr/libexec/postfix/master & \
    /usr/sbin/rsyslogd -n
