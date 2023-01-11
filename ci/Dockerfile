# This docker container acts as a runner for dagger.
FROM --platform=linux/x86_64 amazonlinux:latest

ARG tfv=1.3.1

# Install required repos
RUN : \
    && yum update -y -q \
    && yum install -y -q yum-utils \
    && yum-config-manager --add-repo https://rpm.releases.hashicorp.com/AmazonLinux/hashicorp.repo \
    && :

# Install required packages
RUN : \
    && yum install -y -q \
        terraform-${tfv} \
        jq \
        unzip \
        sudo \
        docker \
        git \
    && yum clean all \
    && rm -rf /var/cache/yum \
    && :

# install aws cli https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
RUN : \
    && curl -s "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip -q awscliv2.zip \
    && sudo ./aws/install \
    && rm -rf awscliv2.zip \
    && :

RUN : \
    && mkdir -p /src \
    && chmod -R 777 /src \
    && :