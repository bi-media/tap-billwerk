# Prepare Server

1. Installation of Ubuntu 18.04
2. Install python 3.7.1 from source code
```
sudo apt update
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
cd /tmp
wget https://www.python.org/ftp/python/3.7.1/Python-3.7.1.tgz
tar –xf Python-3.7.1.tgz
```

Info: https://phoenixnap.com/kb/how-to-install-python-3-ubuntu

3. Install pip3
See here: https://linuxize.com/post/how-to-install-pip-on-ubuntu-18.04/

4. Install setuptools for pip
```
pip install setuptools
```

# Download Repo
1. Create folder and clone repo
```
mkdir /home/ubuntu/tap-billwerk
cd /home/ubuntu/tap-billwerk
git clone https://github.com/bi-media/tap-billwerk.git
```

# Create python environments
We use different environments for each pymodul from singer.io to avoid version conflicts
1. Create tap-billwerk environment
```
#Create environment
python3 -m venv /home/ubuntu/.virtualenvs/tap-billwerk
#Activate environment
source /home/ubuntu/.virtualenvs/tap-billwerk/bin/activate
# Go to billwerk git repo
cd /home/ubuntu/tap-billwerk
#Install requierements
pip install -r requirements.txt
# Install tap-billwerk as py modul in environment
python setup.py build --force
python setup.py install
```

2. Create environment for target for example stitch
```
# create environments
python3 -m venv /home/ubuntu/.virtualenvs/target-stitch
# install py modul
pip install target-stitch
```

# Create configuration folder

1. Create folder
```
mkdir /home/ubuntu/billwerkreporting
```
2. copy all config files from script example folder
```
cp /home/ubuntu/tap-billwerk/scripts/*.* /home/ubuntu/billwerkreporting
```

Have fun and make singer.io as documented in README.md