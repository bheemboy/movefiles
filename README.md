Steps to install in a freebsd jail

pkg install -y git python39 py39-pip nano
ln -s /usr/local/bin/python3.9 /usr/local/bin/python
cd /root
git clone https://github.com/bheemboy/movefiles.git
pip install -r /root/movefiles/app/requirements.txt

setenv EDITOR /usr/local/bin/nano
crontab -e
# @reboot /usr/local/bin/python /root/movefiles/app/app.py

good luck! you might need it.