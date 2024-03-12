# main user-config depending on environment
config = {
    "domainX": {
        "host": "host2",
        "url_prefix": "http://host2:8201",
        "user": "cas201",
        "type": "casual"
    },
    "domainY": {
        "host": "host3",
        "url_prefix": "http://host3:8301",
        "user": "cas301",
        "gateway_inbound_address" : "host3:7301",
        "type": "casual"
    },    
    "telegrafA": {
        "host": "host2",
        "user": "cas201",
        "type": "telegraf",
        "binpath" : "/usr/bin"
    },
    "telegrafB": {
        "host": "host3",
        "user": "cas301",
        "type": "telegraf",
        "binpath" : "/usr/bin"
    }
}


# helpers

def get( domain):
    if domain not in config:
        raise SystemError( f"{domain} is missing in config.")
    
    return config[domain]

def port( domain):
    if domain not in config:
        raise SystemError( f"{domain} is missing in config.")
    
    return config[domain]["url_prefix"][-4:]
