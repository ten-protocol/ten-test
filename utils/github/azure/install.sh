apt update
DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
apt-get install -y software-properties-common
add-apt-repository --yes ppa:ethereum/ethereum
apt update
apt install -y ethereum
apt install -y gnuplot
apt install -y pdftk-java
curl -sL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs
npm install console-stamp --global
npm install web3@1.9.0 --global
npm install ethers@5.7.2 --global
npm install ethers6@npm:ethers@6.13.1 --global
npm install commander@11.1.0 --global
npm install @openzeppelin/merkle-tree@1.0.6 --global
npm install @ethereumjs/rlp@5.0.2 --global
npm install -g ganache
npm install -g ganache-cli
apt install -y vim
apt install -y python3-pip
python3 -m pip install eth-account==0.10.0
python3 -m pip install web3==6.13.0
python3 -m pip install pysys==1.6.1
python3 -m pip install solc-select
python3 -m pip install py-solc-x
python3 -m pip install numpy==1.24.4
python3 -m pip install mysql-connector-python==9.0.0
python3 -m pip install rlp==3.0.0
python3 -m pip install twilio==9.6.0
snap install go --classic
curl -fsSL https://get.docker.com -o get-docker.sh
sh ./get-docker.sh
ulimit -n 4096
