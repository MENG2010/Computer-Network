# DNS Client for PA1, CS 555.
**Student:** Ying Meng (ymeng2@gmu.edu)

# Meta
## `dns_client.py`
This is the interface of the DNS-Client, interacting with user and server. It takes one argument (*hostname*, the domain/hostname to query), connects the server using a UDP protocol, constructs query question (using help functions defined in the `message.py`), queries from server, recieves answers from server, and interpreses the answers (using help functions in `message.py`) and displays the IP addresses to use.

There are two ways to use this client.
- Type a command like `python dns_client.py <hostname>`. For example,

``$ python dns_client.py gmu.edu``

- Make the `dns_client.py` executable with command `chmod +x dns_client.py`, then simply run it as a regular shell script. For example,

``$ ./dns_client.py gmu.edu``

## `message.py`
This script defines everything regarding message, such as formats of each section, encodes request to be sent to the server, and decodes message received from server. User does not use this script directly.