from dataclasses import dataclass, field
from types import SimpleNamespace
import json
import yaml


####################################
# Common configuration for gateway #
####################################

@dataclass
class Discovery( object):
    forward: bool = False

@dataclass
class Limit( object):
    size: int = 0
    messages: int = 0

@dataclass
class InboundConnection(object):
    """
    Connection information
    """
    address: str
    discovery: Discovery = field(default_factory=Discovery)

class InboundConnectionList(list):
    """
    List containing connection connected to this gateway group
    """
    def append( self, address: str):
        if isinstance( address, InboundConnection):
            super().append( address)
        else:
            super().append( InboundConnection( address))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")


@dataclass
class OutboundConnection(object):
    """
    Connection information
    """
    address: str
    services: list = field(default_factory=list)
    queues: list = field(default_factory=list)

class OutboundConnectionList(list):
    """
    List containing connection connected to this gateway group
    """
    def append( self, address: str):
        if isinstance( address, OutboundConnection):
            super().append( address)
        else:
            super().append( OutboundConnection( address))
        return super().__getitem__(-1)

@dataclass 
class InboundGroup( object):
    alias: str
    limit: Limit = field(default_factory=Limit)
    connections: InboundConnectionList = field(default_factory=InboundConnectionList)

class InboundGroupList( list):
    def append( self, alias: str):
        if isinstance( alias, InboundGroup):
            super().append( alias)
        else:
            super().append( InboundGroup( alias))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")



@dataclass 
class OutboundGroup( object):
    alias: str
    connections: OutboundConnectionList = field(default_factory=OutboundConnectionList)

class OutboundGroupList( list):
    def append( self, alias: str):
        if isinstance( alias, OutboundGroup):
            super().append( alias)
        else:
            super().append( OutboundGroup( alias))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")


@dataclass
class Inbound(object):
    default: dict = field(default_factory=dict)
    groups: InboundGroupList = field(default_factory=InboundGroupList)

@dataclass
class Outbound(object):
    groups: OutboundGroupList = field(default_factory=OutboundGroupList)

@dataclass
class Reverse(object):
    groups: list = field(default_factory=list)

@dataclass
class GatewayMain(object):
    """
    Outer gateway section of configuration
    """
    inbound: Inbound = field(default_factory=Inbound)
    outbound: Outbound = field(default_factory=Outbound)
    reverse: Reverse = field(default_factory=Reverse)

###################################################
# Common configuration for server and executables #
###################################################

@dataclass
class ServerExecutableData(object):
    """
    Baseclass for storing Server and Executables attributes
    """
    path: str
    alias: str = ""
    arguments: list = field(default_factory=list)
    instances: int = 1
    memberships: list = field(default_factory=list)
    restart: bool = True
    restrictions: list = field(default_factory=list)

    def __repr__(self) -> str:
        return str(self.__dict__)

#######################
# Group configuration #
#######################
@dataclass
class Group(object):
    name: str
    resources: list = field(default_factory=list)
    dependencies: list = field(default_factory=list)

class GroupList( list):
    def append( self, name: str):
        if isinstance( name, Group):
            super().append( name)
        else:
            super().append( Group( name))
        return super().__getitem__(-1)

    def find_first( self, name):
        for item in self:
            if item.name == name:
                return item
        raise SystemError( f"{name} not found")

#############################
# Transaction configuration #
#############################

@dataclass
class Resource(object):
    """
    Storage of Resource attributes
    """
    name: str
    key: str
    instances: int

    def __init__(self, name: str = None, key: str = None, instances: int = 1):
        self.name = name
        self.key = key
        self.instances = instances

    def __repr__(self) -> str:
        return str(self.__dict__)

class ResourceList(list):
    def append( self, name: str = None, key: str = None, instances: int = 1):
        if isinstance( name, Resource):
            super().append( name)
        else:
            super().append( Resource( name, key, instances))
        return super().__getitem__(-1)

    def find_first( self, name):
        for item in self:
            if item.name == name:
                return item
        raise SystemError( f"{name} not found")

class Transaction(object):
    def __init__(self) -> None:
        self.resources = ResourceList()

    def __repr__(self) -> str:
        return str(self.__dict__)

#########################
# services configuration #
#########################

@dataclass
class Timeout(object):
    duration: str = "0s"
    contract: str = "linger"

@dataclass
class Execution(object):
    timeout: Timeout = field(default_factory=Timeout)
@dataclass
class Service(object):
    name: str
    execution: Execution = field(default_factory=Execution)
    routes: list = field(default_factory=list)
    visibility: str = "discoverable"


@dataclass
class ServiceList(list):
    def append( self, name ):
        if isinstance( name, Service):
            super().append( name)
        else:
            super().append( Service( name))
        return super().__getitem__(-1)

    def find_first( self, name):
        for item in self:
            if item.name == name:
                return item
        raise SystemError( f"{name} not found")

########################
# server configuration #
########################

class Server(ServerExecutableData):
    """
    Server entry in model
    """
    def __repr__(self) -> str:
        return str(self.__dict__)

class ServerList( list):
    def append( self, path: str, alias = None, arguments: list = [], instances: int = 1, members: list = [] ):
        if isinstance( path, Server):
            super().append( path)
        else:
            super().append( Server( path, alias, arguments, instances, members))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")
    
############################
# executable configuration #
############################

class Executable(ServerExecutableData):
    """
    Executable entry in model
    """
    def __repr__(self) -> str:
        return str(self.__dict__)

class ExecutableList( list):
    def append( self, path: str, alias = None, arguments: list = [], instances: int = 1, members: list = [] ):
        if isinstance( path, Executable):
            super().append( path)
        else:
            super().append( Executable( path, alias, arguments, instances, members))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")

#######################
# queue configuration #
#######################

@dataclass
class QueueDefault(object):
    pass

@dataclass
class QueueForwardDefault(object):
    pass

@dataclass
class Reply(object):
    queue: str
    delay: str = "0s"

@dataclass
class ServiceTarget(object):
    service: str

@dataclass
class QueueTarget(object):
    queue: str

@dataclass
class ForwardQueueService(object):
    source: str
    target: ServiceTarget = field(default_factory=ServiceTarget)
    instances: int = 1
    reply: Reply = field(default_factory=Reply)

    def __init__(self, source: str, target: ServiceTarget, instances: int = 1, queue = None, delay = None):
        self.source = source
        self.target = ServiceTarget(target)
        self.instances = instances
        self.reply = Reply( queue, delay) if queue else {}


@dataclass
class ForwardQueueQueue(object):
    source: str
    target: QueueTarget = field(default_factory=QueueTarget)
    instances: int = 1

    def __init__(self, source: str, target: QueueTarget, instances: int = 1):
        self.source = source
        self.target = QueueTarget( target) if target else {}
        self.instances = instances

class ForwardQueueServiceList(list):
    def append( self, source, target, instances = 1, reply = None):
        if isinstance( source, ForwardQueueService):
            super().append( source, target, instances, reply )
        else:
            super().append( ForwardQueueService( source, target, instances, reply))
        return super().__getitem__(-1)

class ForwardQueueQueueList(list):
    def append( self, source: str, target: QueueTarget, instances: int = 1):
        if isinstance( source, ForwardQueueQueue):
            super().append( source, target, instances)
        else:
            super().append( ForwardQueueQueue( source, target, instances)) 
        return super().__getitem__(-1)

@dataclass
class ForwardQueueGroup(object):
    alias: str
    services: ForwardQueueServiceList = field(default_factory=ForwardQueueServiceList)
    queues: ForwardQueueQueueList = field(default_factory=ForwardQueueQueueList)

class ForwardQueueGroupList(list):
    def append( self, alias):
        if isinstance( alias, ForwardQueueGroup):
            super().append( alias)
        else:
            super().append( ForwardQueueGroup( alias))
        return super().__getitem__(-1)
    
    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")

@dataclass
class QueueForwardMain(object):
    default: QueueForwardDefault = field(default_factory=QueueForwardDefault)
    groups: ForwardQueueGroupList = field(default_factory=ForwardQueueGroupList)

@dataclass
class Retry(object):
    count: int = 0
    delay: str = "0s"

@dataclass
class Queue(object):
    name: str
    retry: Retry

    def __init__( self, name, count, delay):
        self.name = name
        self.retry = Retry( count, delay)

class QueueList( list):
    def append( self, name, count = 0, delay = 0):
        if isinstance( name, Queue):
            super().append( name, count, delay)
        else:
            super().append( Queue( name, count, delay))
        return super().__getitem__(-1)

@dataclass 
class QueueGroup( object):
    """
    Queuegroup
    """
    alias: str
    queuebase: str
    queues: QueueList[Queue] = field(default_factory=QueueList)

@dataclass
class QueueGroupList( list):
    def append( self, alias: str = None, queuebase: str = None):
        if not queuebase: queuebase = f"${{CASUAL_DOMAIN_HOME}}/queue/{alias}.qb"
        if isinstance( alias, QueueGroup):
            super().append( alias, queuebase)
        else:
            super().append( QueueGroup( alias, queuebase))
        return super().__getitem__(-1)

    def find_first( self, alias):
        for item in self:
            if item.alias == alias:
                return item
        raise SystemError( f"{alias} not found")

@dataclass
class QueueMain(object):
    """
    Outer queue section of configuration
    """
    default: QueueDefault = field(default_factory=QueueDefault)
    groups: QueueGroupList = field(default_factory=QueueGroupList)
    forward: QueueForwardMain = field(default_factory=QueueForwardMain)

########################
# domain configuration #
########################

class Domain(object):
    """
    Domain part of configuration. This groups all interessting configuration.
    """
    def __init__(self, name, default_transaction = True, eventlog = True, http_outbound = True, example_server = True):
        self.name = name
        self.groups = GroupList() 
        self.servers = ServerList() 
        self.executables = ExecutableList()
        self.transaction = Transaction()
        self.queue = QueueMain()
        self.gateway = GatewayMain()
        self.services = ServiceList()

        if default_transaction:
            self.transaction.resources.append( 
                name = "example-resource-server",
                key = "rm-mockup",
                instances = 2
            )

        if eventlog:
            self.executables.append( 
                alias = "casual-event-service-log",
                path = "${CASUAL_HOME}/bin/casual-event-service-log",
                arguments = [ "--file", "logs/statistics.log" ],
                instances = 1
            )
        if http_outbound:
            self.executables.append( 
                alias = "casual-http-inbound",
                path = "${CASUAL_HOME}/nginx/sbin/nginx",
                arguments = [ 
                    "-c", 
                    "${CASUAL_DOMAIN_HOME}/configuration/nginx.conf",
                    "-p",
                    "${CASUAL_DOMAIN_HOME}",
                ],
                instances = 1
            )

        if example_server:
            self.servers.append(
                alias = "casual-example-server",
                path =  "${CASUAL_HOME}/example/bin/casual-example-server",
                instances = 1
            )


    def __repr__(self):
        return str(self.model())

########################
# system configuration #
########################

def default_system_configuration():
    """
    Definition of default system configuration for tests
    """
    return [
        {
            "key": "rm-mockup",
            "server" : "rm-proxy-casual-mockup",
            "xa_struct_name": "casual_mockup_xa_switch_static",
            "libraries": [
                "casual-mockup-rm"
            ],
            "paths" : {
                "library" : [
                    "${CASUAL_HOME}/lib"
                ]
            }
        }
    ]

class System( object):
    """
    System section of configuration
    """
    def __init__(self):
        self.resources = default_system_configuration()

###############################
# configuration configuration #
###############################

class Configuration(object):
    """
    Main configuration object
    """
    def __init__(self, name = None, default_transaction = True, eventlog = True, http_outbound = True, example_server = True):
        self.domain = Domain( name, default_transaction, eventlog, http_outbound, example_server)
        self.system = System()
    
    def as_json(self):
        return json.dumps( self, indent=2, default=vars )
    
    def as_yaml(self):
        model = json.loads( str(self.as_json()))
        return yaml.dump(model)

    def configuration_file_entry(self):
        return {
            "filename" : "configuration/domain.yaml",
            "content" : self.as_yaml()
        }

    def from_yaml(self, document):
        doc = yaml.safe_load(document)
        jdoc = json.dumps( doc, indent=2, default=vars)
        x = json.loads( str(jdoc), object_hook=lambda d: SimpleNamespace(**d))
        self.__dict__.update( x.__dict__)

if __name__ == '__main__':    

    config_domain_X = Configuration( "example")
    config_domain_X.domain.services.append("test-service")
    print(config_domain_X.as_yaml())