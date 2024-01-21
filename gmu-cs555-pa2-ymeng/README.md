# Distance Vector Routing.

# Meta
## networks
Files of adjacency networks are put in this folder. Currently, it contains several pre-defined networks.

### network-ring.txt
This file defines the adjacency matrix of the **required network** with a topology of ring (i.e., the left figure in page 6).

### network-star.txt
This file defines the adjacency matrix of the **required network** with a topology of star (i.e., the right figure in page 6).

### demo-line.txt
This is a demo network consisting 3 nodes for debugging. It defines the adjacency matrix of a network with a topology of line.

### demo-ring.txt
This is a demo network consisting 3 nodes for debugging. It defines the adjacency matrix of a network with a topology of ring.

### demo-star.txt
This is a demo network consisting 4 nodes for debugging. It defines the adjacency matrix of a network with a topology of star.

## dv-routing.py
This is the only script file of the project, including the main logic, the routing algorithm, and all necessary functions and classes for PA2. It takes one argument (*input* or *i* for short), which indicating the file network topology (represented as adjacency matrix), then load the network topology from the file, creates threads for nodes in the networks, then calculates the distance-vector table using the Bellman-Ford algorithm, and finally output the converged distance-vector table for the network.

This implementation supports networks containing various number of nodes (not limited to 5-node networks).

To run this routing algorithm, type a command like `python dv-routing.py -i <filepath_to_network.txt>` or `python dv-routing.py --input <filepath_to_network.txt>`. For example,

``$ python dv-routing.py -i networks/network-ring.txt``

or

``$ python dv-routing.py --input networks/network-ring.txt``

## OUTPUT.txt
This file contains the performance logs of (1) `networks/network-ring.txt` (the left network in page 6), then (2) `networks/network-star.txt` (the right network in page 6).
