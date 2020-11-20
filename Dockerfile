FROM	python:3
WORKDIR	/usr/src/app
COPY	redfish_ilo_server_info.py ./
COPY	requirements.txt ./
RUN	pip3 install -r ./requirements.txt
ENTRYPOINT	["python3", "./redfish_ilo_server_info.py"]
