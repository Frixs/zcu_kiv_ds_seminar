# KIV/DS #01

*A basic demo of distributed systems.*  
The same single script runs on each machine. Each one knows about the others (specified in [`config.py`](https://github.com/Frixs/zcu_kiv_ds_seminar/blob/main/01/client/config.py)). Each one is represented as a node and they communicate to each other and based on **Bully algorithm** they decied who is the coordinator (leader).  
Once the coordinator is chosen, the coordinator color 1/3 nodes to green (the group including the coordiantor) and 2/3 nodes to red (round green up).

## Installation
- requires to have installed Docker and Vagrant on your OS
- to run the system
  - use `vagrant up` in the root folder where also `Vagrantfile` is located

## Algorithm Information / Communication
The bully algorithm is used for selecting the leader/coordinator node. The entire communication among the nodes in this example is set via HTTP requests (API).  
The nodes are requested to repaint during any node outage and the nodes are requested to do it always if any node is outaged.  
The algorithm could be optimized to request the nodes to repaint only once when any node gets outaged by implementing programming structures to keep information about outaged nodes to do not request repaint all the time.
