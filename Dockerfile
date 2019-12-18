FROM python:3.8-alpine
ADD requirements.txt /
RUN pip install -r requirements.txt
ADD src /
# Ubuntu
# RUN ln -fs /usr/share/zoneinfo/Europe/Bucharest /etc/localtime
# RUN dpkg-reconfigure -f noninteractive tzdata
# alpine
RUN apk add tzdata
RUN cp /usr/share/zoneinfo/Europe/Bucharest /etc/localtime
RUN echo "Europe/Bucharest" >  /etc/timezone
RUN date
RUN apk del tzdata

CMD [ "python", "./app.py" ]