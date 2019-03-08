FROM nhoening/vokomokum-members

# Fix: include protocol in whitelist (because it's http now, and we do https)
RUN sed -E -i "s#(startswith\\(')http://#\\1#" members/views/base.py

COPY docker-entrypoint.sh ./
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["pserve", "development.ini", "--reload"]
