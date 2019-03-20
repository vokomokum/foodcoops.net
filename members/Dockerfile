FROM nhoening/vokomokum-members

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install --no-install-recommends -y mysql-client ssmtp && \
    rm -Rf /var/lib/apt/lists/* /var/cache/apt/*

RUN pip install pymysql

# Fix: include protocol in whitelist (because it's http now, and we do https)
RUN sed -E -i "s#(startswith\\(')http://#\\1#" members/views/base.py

COPY ssmtp.conf /etc/ssmtp/
COPY production.ini dbsetup.py dbsetup.sql docker-entrypoint.sh ./

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["pserve", "production.ini"]
