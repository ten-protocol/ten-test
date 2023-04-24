FROM --platform=linux/amd64 ubuntu:20.04

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:ethereum/ethereum
RUN apt update
RUN apt install -y ethereum
RUN apt install -y curl
RUN apt install -y solc
RUN apt install -y gnuplot

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs
RUN npm install console-stamp --global
RUN npm install ganache --global
RUN npm install web3@1.9.0 --global
RUN npm install ethers@5.7.2 --global
RUN npm install commander --global

RUN apt install -y vim
RUN apt install -y python3-pip
RUN python3 -m pip install web3==5.31.3
RUN python3 -m pip install pysys==1.6.1
RUN python3 -m pip install py-solc-x

RUN mkdir /home/obscuro-test
RUN mkdir /home/go-obscuro
COPY . /home/obscuro-test

WORKDIR /home/obscuro-test/artifacts/wallet_extension
RUN rm wallet_extension
RUN ln -s wallet_extension_linux_amd64 wallet_extension

WORKDIR /home/obscuro-test

