import unittest
from casual.performance.test import configuration

class TestConfiguration(unittest.TestCase):

    def test_main_empty_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        self.assertEqual(config_domain_X.domain.name, "domainX", 'There name is wrong.')
        self.assertEqual(len( config_domain_X.domain.servers), 0, 'There should be no servers.')
        self.assertEqual(len( config_domain_X.domain.executables), 0, 'There should be no executables.')

    def test_main_exampleserver_configuration(self):
        config_domain_X = configuration.Configuration( "domainY", False, False, False, example_server=True)
        self.assertEqual(config_domain_X.domain.name, "domainY", 'There name is wrong.')
        self.assertEqual(len( config_domain_X.domain.servers), 1, 'There should be no servers.')
        self.assertEqual(len( config_domain_X.domain.executables), 0, 'There should be no executables.')
        self.assertEqual( config_domain_X.domain.servers[0].alias, "casual-example-server", "There exampleserver is missing")

    def test_main_testserver_configuration(self):
        config_domain_X = configuration.Configuration( "domainY", False, False, False, False)
        config_domain_X.domain.groups.append("test-group")
        server = config_domain_X.domain.servers.append("/bin/path/test-server")
        server.alias = "test-server"
        server.arguments = [ "-c", "0" , "-f", "somefile" ]
        server.memberships.append("test-group")
        server.restrictions.append(".*")
        self.assertEqual(config_domain_X.domain.name, "domainY", 'There name is wrong.')
        self.assertEqual(len( config_domain_X.domain.servers), 1, 'There should be no servers.')
        self.assertEqual(len( config_domain_X.domain.executables), 0, 'There should be no executables.')
        self.assertEqual( config_domain_X.domain.servers[0].alias, "test-server", "There test-server is missing")
        self.assertEqual( config_domain_X.domain.servers[0].memberships[0], "test-group", "There memberships is missing")
        self.assertEqual( config_domain_X.domain.servers[0].path, "/bin/path/test-server", "There path is missing")
        self.assertEqual( config_domain_X.domain.servers[0].restart, True, "There restart is wrong")
        self.assertEqual( config_domain_X.domain.servers[0].restrictions[0], ".*", "There should be a restriction")


    def test_main_queue_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        config_domain_X.domain.queue.groups.append("test-group").queues.append("test-queue", 3, "3ms")
        self.assertEqual( len( config_domain_X.domain.queue.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.queue.groups[0].alias, "test-group", 'There should be a group.')
        self.assertEqual( len(config_domain_X.domain.queue.groups[0].queues), 1, 'There should be a queue.') 
        q =  config_domain_X.domain.queue.groups[0].queues[0]
        self.assertEqual( q.name, "test-queue", 'There queue should have the name test-queue') 
        self.assertEqual( q.retry.count, 3, 'There queue should have a retry count') 
        self.assertEqual( q.retry.delay, "3ms", 'There queue should have a retry delay') 

    def test_main_queueforwardservice_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        config_domain_X.domain.queue.forward.groups.append("test-group").services.append("test-queue", "test-service")
        self.assertEqual( len( config_domain_X.domain.queue.forward.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.queue.forward.groups[0].alias, "test-group", 'There should be a group.')
        self.assertEqual( len( config_domain_X.domain.queue.forward.groups[0].services), 1, 'There should be a forward service.') 
        f =  config_domain_X.domain.queue.forward.groups[0].services[0]
        self.assertEqual( f.source, "test-queue", 'There source should have the name test-queue') 
        self.assertEqual( f.target.service, "test-service", 'There target should have been test-service') 

    def test_main_queueforwardqueue_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        config_domain_X.domain.queue.forward.groups.append("test-group").queues.append("test-source-queue", "test-target-queue")
        self.assertEqual( len( config_domain_X.domain.queue.forward.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.queue.forward.groups[0].alias, "test-group", 'There should be a group.')
        self.assertEqual( len( config_domain_X.domain.queue.forward.groups[0].queues), 1, 'There should be a forward queue.') 
        f =  config_domain_X.domain.queue.forward.groups[0].queues[0]
        self.assertEqual( f.source, "test-source-queue", 'There source should have the name test-source-queue') 
        self.assertEqual( f.target.queue, "test-target-queue", 'There target should have been test-target-queue') 

    def test_main_gateway_inbound_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        config_domain_X.domain.gateway.inbound.groups.append("test-inbound-group").connections.append("localhost:1234")
        self.assertEqual( len( config_domain_X.domain.gateway.inbound.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.gateway.inbound.groups[0].alias, "test-inbound-group", 'There should be a group alias.')
        self.assertEqual( len( config_domain_X.domain.gateway.inbound.groups[0].connections), 1, 'There should be a connection.') 
        self.assertEqual( config_domain_X.domain.gateway.inbound.groups[0].connections[0].address, "localhost:1234", 'There should be a connection.') 

    def test_main_gateway_outbound_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        config_domain_X.domain.gateway.outbound.groups.append("test-outbound-group").connections.append("localhost:4321")
        self.assertEqual( len( config_domain_X.domain.gateway.outbound.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.gateway.outbound.groups[0].alias, "test-outbound-group", 'There should be a group alias.')
        self.assertEqual( len( config_domain_X.domain.gateway.outbound.groups[0].connections), 1, 'There should be a connection.') 
        self.assertEqual( config_domain_X.domain.gateway.outbound.groups[0].connections[0].address, "localhost:4321", 'There should be a connection.') 
        outbound = config_domain_X.domain.gateway.outbound.groups.find_first("test-outbound-group")
        outbound.connections[0].services.append("service1")
        outbound.connections[0].queues.append("queue1")
        self.assertEqual( config_domain_X.domain.gateway.outbound.groups[0].connections[0].services[0], "service1", 'There should be a service.') 
        self.assertEqual( config_domain_X.domain.gateway.outbound.groups[0].connections[0].queues[0], "queue1", 'There should be a queue.') 

    def test_main_group_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        group = config_domain_X.domain.groups.append("test-group")
        group.resources.append("test-resource")
        group.dependencies.append("test-dependency")
        self.assertEqual( len( config_domain_X.domain.groups), 1, 'There should be a group.')
        self.assertEqual( config_domain_X.domain.groups[0].name, "test-group", 'There should be a group name.')
        self.assertEqual( config_domain_X.domain.groups[0].resources[0], "test-resource", 'There should be a resource.')
        self.assertEqual( config_domain_X.domain.groups[0].dependencies[0], "test-dependency", 'There should be a dependency.')

    def test_main_service_configuration(self):
        config_domain_X = configuration.Configuration( "domainX", False, False, False, False)
        service = config_domain_X.domain.services.append("test-service")
        service.routes.append("route1")
        service.visibility = "undiscoverable"
        service.execution.timeout.contract = "kill"
        service.execution.timeout.duration = "97ms"
        self.assertEqual( len( config_domain_X.domain.services), 1, 'There should be a service.')
        self.assertEqual( config_domain_X.domain.services[0].name, "test-service", 'There should be a service name.')
        self.assertEqual( config_domain_X.domain.services[0].visibility, "undiscoverable", 'There should be visibility undiscoverable.')
        self.assertEqual( config_domain_X.domain.services[0].routes[0], "route1", 'There should be a route.')
        self.assertEqual( config_domain_X.domain.services[0].execution.timeout.contract, "kill", 'There should be a contract kill .')
        self.assertEqual( config_domain_X.domain.services[0].execution.timeout.duration, "97ms", 'There should be a duration of 97ms.')



if __name__ == '__main__':
    unittest.main()