FROM --platform=linux/amd64 ubuntu:20.04

RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:ethereum/ethereum
RUN apt update
RUN apt install -y ethereum
RUN apt install -y curl
RUN apt install -y solc
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y gnuplot

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs
RUN npm install console-stamp --global
RUN npm install ganache --global
RUN npm install web3@1.9.0 --global
RUN npm install ethers@5.7.2 --global
RUN npm install ethers6@npm:ethers@6.13.1 --global
RUN npm install commander@11.1.0 --global
RUN npm install @openzeppelin/merkle-tree@1.0.6 --global

RUN apt install -y vim
RUN apt install -y python3-pip
RUN python3 -m pip install eth-account==0.10.0
RUN python3 -m pip install web3==6.13.0
RUN python3 -m pip install pysys==1.6.1
RUN python3 -m pip install py-solc-x
RUN python3 -m pip install numpy==1.24.4

RUN mkdir /home/ten-test
RUN mkdir /home/go-ten
COPY . /home/ten-test

RUN mkdir ~/.tentest
RUN echo "[binaries.linux]" > ~/.tentest/user.properties
RUN echo "go = /usr/bin/go" >> ~/.tentest/user.properties
RUN echo "solc = /usr/bin/solc" >> ~/.tentest/user.properties
RUN echo "ganache = /usr/bin/ganache-cli" >> ~/.tentest/user.properties
RUN echo "gnuplot = /usr/bin/gnuplot" >> ~/.tentest/user.properties
RUN echo "node = /usr/bin/node" >> ~/.tentest/user.properties
RUN echo "node_path = /usr/lib/node_modules:/usr/local/lib/node_modules" >> ~/.tentest/user.properties

WORKDIR /home/ten-test/artifacts/wallet_extension
RUN rm wallet_extension
RUN ln -s wallet_extension_linux_amd64 wallet_extension

WORKDIR /home/ten-test

