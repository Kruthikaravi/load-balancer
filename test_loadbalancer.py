import json

import pytest

from loadbalancer import loadbalancer


@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
        yield client


def test_host_routing_drexel(client):
    result = client.get('/', headers={'Host': 'www.drexel.edu'}, query_string={'RemoveMe': 'Remove'})
    data = json.loads(result.data.decode())
    assert 'This is the drexel application.' in data['message']
    assert data['server'] in ['http://localhost:8082/', 'http://localhost:8081/']
    assert data['custom_header'] == 'drexel'
    assert data['host_header'] in ['localhost:8082', 'localhost:8081']
    assert data['query_strings'] == 'MyCustomParam=drexel'
    assert data['custom_params'] == 'drexel'


def test_host_routing_upenn(client):
    result = client.get('/', headers={'Host': 'www.upenn.edu'})
    data = json.loads(result.data.decode())
    assert 'This is the upenn application.' in data['message']
    assert data['server'] in ['http://localhost:9082/', 'http://localhost:9081/']
    assert not data['custom_header']
    assert data['host_header'] in ['localhost:9082', 'localhost:9081']


def test_host_routing_pen(client):
    result = client.get('/', headers={'Host': 'www.pen.com'})
    assert b'Not Found' in result.data


def test_host_routing_notfound(client):
    result = client.get('/', headers={'Host': 'www.notdrexel.edu'})
    assert b'Not Found' in result.data
    assert 404 == result.status_code


def test_path_routing_drexel(client):
    result = client.get('/drexel')
    data = json.loads(result.data.decode())
    assert 'This is the drexel application.' in data['message']
    assert data['server'] in ['http://localhost:8082/', 'http://localhost:8081/']
    assert not data['custom_header']
    assert data['host_header'] in ['localhost:8082', 'localhost:8081']


def test_path_routing_upenn(client):
    result = client.get('/upenn')
    data = json.loads(result.data.decode())
    assert 'This is the upenn application.' in data['message']
    assert data['server'] in ['http://localhost:9082/', 'http://localhost:9081/']
    assert not data['custom_header']
    assert data['host_header'] in ['localhost:9082', 'localhost:9081']


def test_path_routing_pen(client):
    result = client.get('/pen')
    assert b'No backend servers available.' in result.data


def test_path_routing_notfound(client):
    result = client.get('/notdrexel')
    assert b'Not Found' in result.data
    assert 404 == result.status_code


def test_rewrite_host_routing(client):
    result = client.get('/v1', headers={'Host': 'www.drexel.edu'})
    assert b'This is V2' == result.data


def test_firewall_ip_reject(client):
    result = client.get('/drexel', environ_base={'REMOTE_ADDR': '10.192.0.1'}, headers={'Host': 'www.drexel.edu'})
    assert result.status_code == 403


def test_firewall_ip_accept(client):
    result = client.get('/drexel', environ_base={'REMOTE_ADDR': '55.55.55.55'}, headers={'Host': 'www.drexel.edu'})
    assert result.status_code == 200


def test_firewall_path_reject(client):
    result = client.get('/messages', headers={'Host': 'www.upenn.edu'})
    assert result.status_code == 403


def test_firewall_path_accept(client):
    result = client.get('/pictures', headers={'Host': 'www.upenn.edu'})
    assert result.status_code == 200