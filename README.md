# http-load-balancer
https://testdriven.io/courses/http-load-balancer/

A load balancer is a networking component that's used for distributing network traffic across multiple servers in order to horizontally scale web-based applications. There are many popular ones out there such as Nginx, HAProxy, and Traefik, to name a few. A load balancer is a critical component in system design, as it is responsible for distributing incoming requests to multiple servers to ensure that no single server becomes overwhelmed, and that the overall system performance remains optimal. This is extremely important in case of congestion control and routing protocols. <br />


Used the following tools: <br />
Flask is a popular Python web framework. <br />
pytest is a testing framework. <br />
venv is used for creating isolated Python environments. <br />
Make is an automation tool that generates executable and non-source files <br />
Docker is a containerization tool designed to simplify the development and deployment of applications. <br />

dependencies: <br />

python3 and pip (or pip3) <br />
venv <br />
pytest <br />
Flask <br />

# Commands

Create venv
$ git clone https://github.com/Kruthikaravi/load-balancer.git <br />
$ cd load-balancer <br />
$ python3.9 -m venv env <br />
$ source env/bin/activate <br />

To install requirements <br />
$ pip install -r requirements.txt <br />

Build Docker Image from Dockerfile <br />
$ docker build -t server . <br />

Spin up Docker Containers <br />
$ docker-compose up -d <br />

$ docker-compose ps <br />

Run load Balancer <br />
$ FLASK_APP=loadbalancer.py flask run <br />

Test 
$ curl -H 'Host: www.drexel.edu' 127.0.0.1:5000 <br />

Run all tests and shut down containers <br />
$ make test <br />
