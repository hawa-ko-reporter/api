# pull official base image
FROM python:3.6.7-alpine3.6

ARG FB_ACCESS_TOKEN
ARG AQI_TOKEN
ARG GEO_TOKEN

RUN echo ${FB_ACCESS_TOKEN}
RUN echo ${AQI_TOKEN}
RUN echo ${GEO_TOKEN}

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
