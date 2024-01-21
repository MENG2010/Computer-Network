'''
Distance Vector Routing

@author: MENG
'''
import argparse
import socket
import threading
import time

from math import inf

# Global variables
NODES = []  # nodes in the network
DIST_VECTOR_TABLE = {}  # Distance vector table
NEIGHBORS = {}  # Neighbors of each node
lock = threading.Lock()  # lock for updating DV

LAST_DV_TABLE = {}  # the last distance vector table

# converged is used to track if DV has converged for each node
# converged[i] = True if DV for node i has converged, not converged otherwise
CONVERGED = []


def _load_network_topology(topology_file):
    """Load the network topology (as linked list) from the given file.
    """
    adjacency_matrix = []
    with open(topology_file, 'r') as f:
        print(f'[INFO] Loading network topology from {topology_file}')
        for connection in f.readlines():
            adjacency_matrix.append(connection.strip().split())
    # print(f'[DEBUG] adajanecy matrix: {len(adjacency_matrix)}, {adjacency_matrix}')
    
    # Convert the adjacency matrix into linked list,
    # each item is in the form of <source> <destination> <distance>
    # Nodes are named in the order of A, B, C, etc.
    for i in range(len(adjacency_matrix)):
        node = chr(ord('A')+i)
        NODES.append(node)
        CONVERGED.append(False)
    # print(f'[DEBUG] nodes: {NODES}')
    
    linked_list = []
    for i in range(len(adjacency_matrix)):
        for j in range(len(adjacency_matrix[0])):
            # print(f'[DEBUG] ({i}, {j}): {NODES[i]} -> {NODES[j]}: {adjacency_matrix[i][j]}')
            entrance = [NODES[i], NODES[j], adjacency_matrix[i][j]]
            linked_list.append(entrance)
    
    # print(f'[DEBUG] forwarding table: {forwarding_table}')
    return linked_list
    

def port(node):
    """Return the port number of the given node.
    Ports start from 50000.
    """
    return 50000 + (ord(node) - ord('A'))


def network_init(topology_file):
    # Read and parse txt file to initialize distance vector table (DV)
    # and set initial distances between nodes
    forwarding_table = _load_network_topology(topology_file)
    for entrance in forwarding_table:
        source, destination, distance = entrance
        distance = int(distance)
        if source not in DIST_VECTOR_TABLE:
            DIST_VECTOR_TABLE[source] = {}
        
        if destination != source and distance == 0:
            # if the distance is 0, then the two nodes are not directly connected
            # then we set the distance between the two nodes to infinity
            DIST_VECTOR_TABLE[source][destination] = inf
        elif destination == source:
            # set the distance from a node to itself to 0
            DIST_VECTOR_TABLE[source][source] = 0
        else:
            # otherwise, the distance between the two nodes is value of the edge
            DIST_VECTOR_TABLE[source][destination] = int(distance)
            # add the destination node to the neighbor list of the source node
            if source not in NEIGHBORS:
                NEIGHBORS[source] = [destination]
            else:
                NEIGHBORS[source].append(destination)


def send_distance_vector(node):
    """Send the updated distance vector to neighboring nodes."""        
    for neighbor in NEIGHBORS[node]:
        if neighbor != node:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect(('localhost', port(neighbor)))
                # Construct a DV message in the form of
                # <sender>-{<destination>: <distance>, ...}
                message = f'{node}-{DIST_VECTOR_TABLE[node]}'
                print(f'\t Sending DV to node {neighbor}')
                client.sendall(message.encode())
                client.close()
            except ConnectionRefusedError:
                pass


def update_distance_vector(node, new_dv):
    """Update the distance vector if there are any changes."""
    with lock:
        if DIST_VECTOR_TABLE[node] != new_dv:
            DIST_VECTOR_TABLE[node] = new_dv
            return True
        else:
            return False


def calc_distance_vector(node):
    """Recalculate the new distance vector based on
    the received distance vectors from neighboring nodes.
    """
    new_dv = DIST_VECTOR_TABLE[node].copy()
    
    for neighbor in DIST_VECTOR_TABLE[node]:
        if neighbor != node:
            for dest in DIST_VECTOR_TABLE[neighbor]:
                if dest != node:
                    # recalculate the cost using the Bellman-Ford equation
                    cost = DIST_VECTOR_TABLE[node][neighbor] + DIST_VECTOR_TABLE[neighbor][dest]
                    
                    if dest not in new_dv or cost < new_dv[dest]:
                        # update the cost if it is smaller than the current cost
                        new_dv[dest] = cost
                        
    return new_dv


def receive_distance_vector(node):
    """Receive distance vectors from neighboring nodes.
    Then update DV accordingly and broadcast the updated DV to neighbors.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', port(node)))
    server.listen(5)
    
    # continue receiving DV if not all nodes have converged
    while not all(CONVERGED):
        conn, _ = server.accept()
        data = conn.recv(1024).decode()
        # DV message format: <sender>-{<destination>: <distance>, ...}
        sender, received_dv = data.split('-')
        # evaluate the received DV
        received_dv = eval(received_dv)
        conn.close()
        if update_distance_vector(sender, received_dv):
            print(f'\t Node {node} received DV from {sender}')
            print(f'\t Updating DV at node {node}')
            print(f'\t New DV at node {node} = {DIST_VECTOR_TABLE[node]}')
            send_distance_vector(node)  # Broadcast updated DV to neighboring nodes


def routing(stop=False):
    """The main routing algorithm logic."""
    rounds = 0
    while not stop:
        stop = all(CONVERGED)
        print(f'-------- Round {rounds} --------')
        for node in NODES:
            print(f'[Node {node}]')
            print(f'\t Current DV = {DIST_VECTOR_TABLE[node]}')
            
            # Broadcast DV to neighboring nodes
            send_distance_vector(node)
            # Wait for DV to propagate
            time.sleep(1)
            
            if not update_distance_vector(node, calc_distance_vector(node)):
                print(f'\t No change in DV at node {node}')
                # DV has temperately converged at this node
                CONVERGED[NODES.index(node)] = True
            else:
                print(f'\t Updated DV = {DIST_VECTOR_TABLE[node]}')
                # Reset converged flag for all nodes,
                # as all nodes have to recalculate their DV due to the change.
                for i in range(len(CONVERGED)):
                    CONVERGED[i] = False
                
                # Wait for all nodes to update their DV
                time.sleep(5)
        
        rounds += 1
        print()    
    print(f'Routing algorithm converged.\nNumber of rounds till convergens = {rounds}\n')


def display_distance_vectors():
    """Display the distance vectors for each node."""
    print('Final output:')
    for node in NODES:
        print(f'Node {node} DV = {sorted(DIST_VECTOR_TABLE[node].items())}')
    print()


def display_distance_vector_table():
    """Display the distance vector table."""
    print('Final Distance Vector Table')
    header = '\t'
    header += '\t'.join(NODES)
    print(header)
    print('----'*len(header))
    for node in NODES:
        distances = [str(DIST_VECTOR_TABLE[node][n]) for n in NODES]
        fwd_info = '\t'.join(distances)
        print(f'{node}\t{fwd_info}')
    
    print('----'*len(header))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Distance Vector Routing')
    parser.add_argument('-i', '--input', type=str, required=False,
                        default='networks/demo-ring.txt',
                        help='The file contains an adjacency matrix of a network.')
    args = parser.parse_args()
    
    # Initialize the network
    network_init(args.input)
    # print(f'[DEBUG] initial DV:\n{DIST_VECTOR_TABLE}')
    
    # Start thread for receiving DV from neighboring nodes
    active_nodes = []
    for node in NODES:
        node_thread = threading.Thread(target=receive_distance_vector, args=(node,))
        node_thread.start()
        active_nodes.append(node_thread)
        
    # Start main routing algorithm thread
    routing_thread = threading.Thread(target=routing)
    routing_thread.start()
    
    # Wait for threads to complete
    for node_thread in active_nodes:
        node_thread.join()
    routing_thread.join()
    display_distance_vectors()
    display_distance_vector_table()
