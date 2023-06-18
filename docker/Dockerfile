FROM debian:latest
LABEL maintainer="Anton Orlichenko <aorlichenko@tulane.edu>"

RUN apt-get update
RUN apt-get install -y python3 python3-pip git

WORKDIR ~
RUN git clone https://github.com/TulaneMBB/ImageNomer
RUN cd ImageNomer
RUN pip install -r requirements.txt --break-system-packages

CMD python3 backend/app.py
