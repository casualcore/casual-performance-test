import requests

def information(domain: str) -> dict:
    domain_reply = requests.post(
        url = f"http://{domain}:8080/casual/.casual/domain/state",
        headers = { "content-type": "application/json"}
    )
    return domain_reply.json()

def scale_queue_forward(domain: str, alias: str, instances: int):
    requests.post(
        url = f"http://{domain}:8080/casual/.casual/queue/forward/scale/aliases",
        json = { "aliases": [ { "name": alias, "instances": instances}]},
        headers = { "content-type": "application/json"}
    )


def scale_instance(domain: str, alias: str, instances: int):
    requests.post(
        url = f"http://{domain}:8080/casual/.casual/domain/scale/instances",
        json = { "aliases": [ { "name": alias, "instances": instances}]},
        headers = { "content-type": "application/json"}
    )
