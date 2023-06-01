# http-load-balancer
Kruthika Ravi
CS544 - Computer Networks Spring 2023

A load balancer is a networking component that's used for distributing network traffic across multiple servers in order to horizontally scale web-based applications. There are many popular ones out there such as Nginx, HAProxy, and Traefik, to name a few. A load balancer is a critical component in system design, as it is responsible for distributing incoming requests to multiple servers to ensure that no single server becomes overwhelmed, and that the overall system performance remains optimal. This is extremely important in case of congestion control and routing protocols. 


Used the following tools:
Flask is a popular Python web framework.
pytest is a testing framework.
venv is used for creating isolated Python environments.
Make is an automation tool that generates executable and non-source files
Docker is a containerization tool designed to simplify the development and deployment of applications.

dependencies:

python3 and pip (or pip3)
venv
pytest
Flask

# Commands

Create venv
$ git clone https://github.com/Kruthikaravi/load-balancer.git
$ cd load-balancer
$ python3.9 -m venv env
$ source env/bin/activate

To install requirements
$ pip install -r requirements.txt

Build Docker Image from Dockerfile
$ docker build -t server .

Spin up Docker Containers
$ docker-compose up -d

$ docker-compose ps

Run load Balancer
$ FLASK_APP=loadbalancer.py flask run

Test 
$ curl -H 'Host: www.drexel.edu' 127.0.0.1:5000

Run all tests and shut down containers
$ make test
