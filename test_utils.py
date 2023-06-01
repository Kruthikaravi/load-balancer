import yaml

from models import Server
from utils import (
    get_healthy_server,
    healthcheck,
    least_connections,
    process_firewall_rules_flag,
    process_rules,
    process_rewrite_rules,
    transform_backends_from_config,
)


def test_transform_backends_from_config():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    output = transform_backends_from_config(input)
    assert list(output.keys()) == ['www.drexel.edu', 'www.upenn.edu', '/drexel', '/upenn']
    assert output['www.drexel.edu'][0] == Server('localhost:8081')
    assert output['www.drexel.edu'][1] == Server('localhost:8082')
    assert output['www.upenn.edu'][0] == Server('localhost:9081')
    assert output['www.upenn.edu'][1] == Server('localhost:9082')
    assert output['/drexel'][0] == Server('localhost:8081')
    assert output['/drexel'][1] == Server('localhost:8082')
    assert output['/upenn'][0] == Server('localhost:9081')
    assert output['/upenn'][1] == Server('localhost:9082')


def test_get_healthy_server():
    healthy_server = Server('localhost:8081')
    unhealthy_server = Server('localhost:8082')
    unhealthy_server.healthy = False
    register = {'www.drexel.edu': [healthy_server, unhealthy_server],
                'www.upenn.edu': [healthy_server, healthy_server],
                'www.pen.com': [unhealthy_server, unhealthy_server],
                '/drexel': [healthy_server, unhealthy_server],
                '/upenn': [unhealthy_server, unhealthy_server]}
    assert get_healthy_server('www.drexel.edu', register) == healthy_server
    assert get_healthy_server('www.upenn.edu', register) == healthy_server
    assert get_healthy_server('www.pen.com', register) is None
    assert get_healthy_server('/drexel', register) == healthy_server
    assert get_healthy_server('/upenn', register) is None


def test_healthcheck():
    config = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            servers:
              - localhost:8081
              - localhost:8888
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:4444
    ''')
    register = healthcheck(transform_backends_from_config(config))
    assert register['www.upenn.edu'][0].healthy
    assert not register['www.upenn.edu'][1].healthy
    assert register['www.drexel.edu'][0].healthy
    assert not register['www.drexel.edu'][1].healthy


def test_process_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            header_rules:
              add:
                MyCustomHeader: Test
              remove:
                Host: www.drexel.edu
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    headers = {'Host': 'www.drexel.edu'}
    results = process_rules(input, 'www.drexel.edu', headers, 'header')
    assert results == {'MyCustomHeader': 'Test'}


def test_process_param_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            param_rules:
              add:
                MyCustomParam: Test
              remove:
                RemoveMe: Remove
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    params = {'RemoveMe': 'Remove'}
    results = process_rules(input, 'www.drexel.edu', params, 'param')
    assert results == {'MyCustomParam': 'Test'}


def test_process_rewrite_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            rewrite_rules:
              replace:
                v1: v2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    path = 'localhost:8081/v1'
    results = process_rewrite_rules(input, 'www.drexel.edu', path)
    assert results == 'localhost:8081/v2'


def test_least_connections_empty_list():
    result = least_connections([])
    assert result == None


def test_least_connections():
    backend1 = Server('localhost:8081')
    backend1.open_connections = 10
    backend2 = Server('localhost:8082')
    backend2.open_connections = 5
    backend3 = Server('localhost:8083')
    backend3.open_connections = 2
    servers = [backend1, backend2, backend3]
    result = least_connections(servers)
    assert result == backend3


def test_process_firewall_rules_reject():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            firewall_rules:
              ip_reject:
                - 10.192.0.1
                - 10.192.0.2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, 'www.drexel.edu', '10.192.0.1')
    assert not results


def test_process_firewall_rules_accept():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            firewall_rules:
              ip_reject:
                - 10.192.0.1
                - 10.192.0.2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, 'www.drexel.edu', '55.55.55.55')
    assert results


def test_process_firewall_rules_path_reject():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            firewall_rules:
              path_reject:
                - /messages
                - /apps
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, 'www.drexel.edu', path='/apps')
    assert results == False


def test_process_firewall_rules_path_accept():
    input = yaml.safe_load('''
        hosts:
          - host: www.drexel.edu
            firewall_rules:
              path_reject:
                - /messages
                - /apps
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.upenn.edu
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /drexel
            servers:
              - localhost:8081
              - localhost:8082
          - path: /upenn
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, 'www.drexel.edu', path='/pictures')
    assert results == True