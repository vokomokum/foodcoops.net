FROM vokomokum/members

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get -o Acquire::AllowReleaseInfoChange::Suite=true update && \
    apt-get install --no-install-recommends -y mariadb-client msmtp-mta && \
    rm -Rf /var/lib/apt/lists/* /var/cache/apt/*

RUN pip install pymysql

# Fix: include protocol in whitelist (because it's http now, and we do https)
RUN sed -E -i "s#(startswith\\(')http://#\\1#" members/views/base.py

COPY msmtprc /etc/
COPY production.ini dbsetup.py dbsetup.sql docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["pserve", "production.ini"]
