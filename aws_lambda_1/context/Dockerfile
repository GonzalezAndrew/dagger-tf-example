FROM --platform=linux/x86_64 public.ecr.aws/lambda/python:3.9

ARG FOO
ENV FOO $FOO

# ensure libs are up to date
RUN : \
    && yum -y update --security \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && :

COPY requirements.txt ./
COPY app.py ./

RUN : \
    && python3.9 -m pip install -r requirements.txt \
    && :

CMD ["app.lambda_handler"]