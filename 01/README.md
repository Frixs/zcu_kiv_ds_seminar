# KIV/DS #01

A basic demo of distributed systems. The same single script that runs on each machine. Each one knows about the others (specified in `[config.py](https://github.com/Frixs/zcu_kiv_ds_seminar/blob/main/01/client/config.py)`). Each one is represented as a node and they communicate to each other and based on **Bully algorithm** they decied who is the coordinator (leader). Once the coordinator is chosen, the coordinator color the nodes where 1/3 nodes are green (the group including the coordiantor) and 2/3 of nodes are red (ceiling green).

### APIs
- **[ISS Now API](http://open-notify.org/Open-Notify-API/ISS-Location-Now)**
- **[Sunrise/Sunset API](https://sunrise-sunset.org/api)**

## Installation
- requires to have installed Docker and Vagrant on your OS
- to run the system
  - use `vagrant up` in the root folder where `Vagrantfile` is located
