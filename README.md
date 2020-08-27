# iot-server
server_pythonanywhere.com contains the source file that I used to host
the web app online using the pythonanywhere.com platform, thus it is not recommended locally or in other hosting sites, because I followed their official tutorial for their specific platform

I also recommend using thingspeak.com, because it is much more complex if you need over the internet IoT capabilities

server_local_mysql_mariadb contains the source file that I used to make a locally hosted server on a raspberry pi 4.
Make sure to run these commands:

sudo apt-get install mariadb-server
sudo apt-get install mariadb-client

pip3 install mariadb
pip3 install flask

sudo systemctl restart mariadb.service
sudo systemctl restart mysql.service

After that, the server will spawn on the IP address of the pi, so make sure you know it. For best use, I made the IP static in my router settings.
