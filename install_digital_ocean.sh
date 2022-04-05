apt install -y python-is-python3 python3-pip
python -m pip install -r requirements.txt
cp install/app.service /etc/systemd/system/app.service
sudo systemctl daemon-reload
sudo systemctl enable app.service
sudo systemctl start app.service