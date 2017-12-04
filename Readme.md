Approach:

The design idea for developing this Distributed Hash tables implementation is as follows:
dht_peer --> Provides all functionality of the root node as well as peer
network  --> Provides all functionality of socket objects and also initialize connections
message  --> Provides a message object with message validation functionality to check for types
dht_client > Provides client side command line interface

Dht_Peer:
    Every peer has an object of sockets to communicate with either the client(if peer is root)
    or its successor and predecessor.
    When the root is up, it actively listens for connection either from client or a different
    peer.
    If a client connects, then it provides store and retrieve (iterative and recursive)
    functionality to the root.
    If a peer connects, then its exact position is determined in the
    ring and accordingly the successor and predecessor values are updated of the nodes involved
    in join. After a join is completed, then successor, predecessor and ping(heartbeat_send and
    heartbeat_listen) threads are started to communicate among the peers. Apart from this, keys
    in the ring are redistributed to balance the load on the peers.
    When a node crashes, the heartbeat thread senses that its predecessor is crashed and checks
    for the node whose successor has crashed and then connects to that node.
    
DHT_Client:
    When a client starts, it firsts connect to the root and displays the menu to user. Depending
    on the input from user, relevant messages are forwarded to the root.
    
Challenges faced:
1. Handling concurrent reads from socket for all threads
2. Overall design to setup and tear down connections after every join
3. Iterative -- to iterate over all successor chain in the ring
4. Recursive -- to forward the request to its successor if it does not have the data
5. join -- to enumerate all the possibilities where a peer could be placed in the ring and 
           implementing recursion accordingly
6. leave/crash -- handling timeouts and to find out if one node's predecessor is down, then 
                  which node's successor is down
                  
Testing:

I have tested the code for following scenarios:
Scenario                                                       Expected         Actual              Status
1. root starts -> client connects -> store -> retrieve         no crash         no crash            pass
2. root starts -> client connects -> retrieve                  not found        not found           pass
3. peer starts                                                 waiting          waiting             pass
4. root starts->one peer->client connects->store->retrieve     properly         properly            pass
                                                                 retrieved        retrieved         
5. root starts->3 peers->client->store->retrieve               properly         properly            pass
                                                                 retrieved        retrieved
6. root starts->3 peers->client->10 stores->peer close->store  successfully     successfully        pass
                                                                 stored           stored

Limitations:
1. Right now, the data stored is in tuples. Client takes key value from user and returns the same thing
2. Thread handling is kind of shaky. It crashes intermittently only when a node leaves. Adding happens
    gracefully, but after a node leaves, there are intermittent crashes. 