# Intersight Metrics Bridge

This project, based on containers, is a tool to poll metrics from Intersight, store them in InfluxDB, and display them in Grafana. 
It provides a very simple way to manage and visualize your metrics.

## Getting Started

These instructions will get you a copy of the project up and running on your machine.

### Prerequisites

* Intersight SaaS ***(no prerequisite)*** or Appliance: ***1.1.0-1*** and above
* Python 3.x
* Docker (or Podman)

### Installing

Intersight Metrics Bridge can be installed using any of ways below:

#### From GitHub

Click *"Clone or Download"* and *"Download ZIP"* on the GitHub website to download the whole project. 

Uncompress the zip and put the folder on your system. 

#### From Git command line

You need to have Git on your system (not necessarily installed by default on all types of system).

Navigate to your desired path where you want XXXX to be placed on and clone it through your command-line console:

```
git clone https://github.com/mabuelgh/intersight-metrics-bridge.git
```
### Initial Setup

This project uses .env and config/servers_inventory.yaml as source of configurations. 
Indeed, environment variables are passed to containers during their creation.
Instead of creating .env manually, this project includes a ready-to-use python script that will set up environment variables.
The initial_setup_variables.yaml files contains all the basics configurations for the project.
To add your own Grafana or change the default credentials, modify this file. If not, keep it as is.

1. Get the python required packages :
```
pip install -r requirements.txt.txt
```
2. At initial setup, run the following command :
```
python initial_setup.py
```
3. **Create an API Key from Intersight** and put the secret key file in /config named secret_key.txt. 
4. **Modify config/servers_inventory.yaml** to reflect your Intersight environment.

### Running Intersight Metrics Bridge

In the main directory:
#### From Podman
```
podman compose up  --force-recreate --build
```
#### From Docker
```
docker-compose build --no-cache
docker-compose up
```

### Accessing Intersight Metrics Bridge
Once the containers are launched, make sure that all the 3 containers are still up and running after a few seconds. 
If an error occurs, the containers will stop.
#### From Podman
```
podman ps
```
#### From Docker
```
docker ps
```
To access the influxDB and Grafana services, type in your browser:
* 127.0.0.1:8086, for influxDB
* 127.0.0.1:3000, for Grafana

Default credentials for influxDB and Grafana are admin / password.

## Collected Metrics
* Host Power Usage in Watt.

## Features to come
* New metrics to fetch.

## New Features
* If you do not input Servers' Serial Number in the YAML inventory, it will result in the collection of all servers in an Intersight domain.

## Authors

* **Adrien Lécharny** - *Creator* - [GitHub account link](https://github.com/alecharn)
* **Marc Abu El Ghait** - *Initial work* - [GitHub account link](https://github.com/mabuelgh)