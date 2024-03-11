# main user-config depending on environment
config = {
    "domainX": {
        "host": "www.flurig.se",
        "url_prefix": "http://localhost:8201",
        "user": "root",
        "type": "casual"
    },
    "telegraf": {
        "host": "www.flurig.se",
        "user": "root",
        "type": "telegraf"
    }
}
    

# helpers

def remote( domain):
    if domain not in config:
        raise SystemError( f"{domain} is missing in config.")
    
    return config[domain]

def port( domain):
    if domain not in config:
        raise SystemError( f"{domain} is missing in config.")
    
    return config[domain]["url_prefix"][-4:]
