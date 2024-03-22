## Usage

### Environment
Three variables needs to be set.

Examples:
```
export CASUAL_DOMAIN_CONFIG_FILE=domains.yaml
export CASUAL_HOST_CONFIG_FILE=hosts.yaml 
export CASUAL_SITE_NAME=develop
```

### Format domains.yaml
Example:
```
domains:
  - name: telegrafA
    inbound-http-port: None
    inbound-gateway-port: None
    binpath : "/opt/homebrew/bin/"
    casual_home: "/Users/xyz123/usr/local/casual"
    type: telegraf

  - name: domainX
    inbound-http-port: 8201
    inbound-gateway-port: 7070
    casual_log: '.*'
    casual_home: "/Users/xyz123/usr/local/casual"
    type: casual
```

### Format hosts.yaml
Example:
```
hosts:
  develop:
    - alias: host2
      user: thunder
      hostname: tom.develop.example.com

    - alias: host3
      user: sunshine
      hostname: jerry.develop.example.com
  qa:
    - alias: host2
      user: rain
      hostname: tom.qa.example.com

    - alias: host3
      user: snow
      hostname: jerry.qa.example.com

```