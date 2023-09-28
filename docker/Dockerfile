FROM debian:latest
LABEL maintainer="Anton Orlichenko <aorlichenko@tulane.edu>"

RUN apt-get update
RUN apt-get install -y python3 python3-pip git

# --break-system-packages is bad, however, we only need to run ImageNomer
# and I'm currently not able to get rid of the "externally managed environment" 
# error using venv
WORKDIR /root
RUN git clone https://github.com/TulaneMBB/ImageNomer
RUN cd ImageNomer && pip install -r requirements.txt --break-system-packages

CMD cd ImageNomer && pwd && ls data && python3 backend/app.py
