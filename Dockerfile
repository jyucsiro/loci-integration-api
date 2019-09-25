FROM python:3 AS base

WORKDIR /usr/src/app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python", "./app.py" ]

FROM base AS devmode
RUN pip install --no-cache-dir -r dev-requirements.txt
RUN git -C loci-testdata pull || git clone https://github.com/CSIRO-enviro-informatics/loci-testdata.git
ENTRYPOINT [ "tail", "-f", "/dev/null" ]

FROM base 
