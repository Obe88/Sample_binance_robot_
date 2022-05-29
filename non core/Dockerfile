FROM ubuntu:18.04

COPY test_binance_bot.py .
COPY input_config.py .
COPY get_data.py .
COPY account_info.py .
COPY requirements.txt .

RUN apt update \
&& apt -y install sudo \
&& sudo apt -y install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget

FROM ubuntu:18.04
COPY --from=0 ./ ./
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz \
&& tar -xf Python-3.7.6.tgz

FROM ubuntu:18.04
COPY --from=1 ./ ./
WORKDIR /tmp/Python-3.7.6
RUN ./configure --enable-optimizations \
&& sudo make install 

FROM ubuntu:18.04
COPY --from=2 ./ ./
RUN sudo pip3 install -r requirements.txt \
&& sudo apt -y install screen

FROM ubuntu:18.04
COPY --from=3 ./ ./
COPY bot_initial_instructions.sh .
RUN chmod +1 ./bot_initial_instructions.sh

# ENV PORT=8080
ENTRYPOINT [ "./bot_initial_instructions.sh" ]

CMD [ "./test_binance_bot.py"]