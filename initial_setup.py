"""To be used to set up or modify .env variables and inventory.yaml file"""
#!/usr/bin/env python3

import yaml

def yaml_to_env(yaml_file_path, env_file_path):
    # Read the YAML file
    with open(yaml_file_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    # Convert YAML data to .env format
    with open(env_file_path, 'w') as env_file:
        env_file.write("# FOLDER FOR INTERSIGHT-METRICS-BRIDGE CONFIG THAT INCLUDES THE LIST OF HOSTS TO POLL\n")
        env_file.write(
            f'INTERSIGHT_METRICS_BRIDGE_CONFIG_INVENTORY="{data.get("intersight_metrics_bridge_config_inventory", "")}"\n\n')

        env_file.write("# INFLUXDB CONFIG\n")
        env_file.write(f'INFLUXDB_URL="{data.get("influxdb_url", "")}"\n')
        env_file.write(f'INFLUXDB_USERNAME={data.get("influxdb_username", "")}\n')
        env_file.write(f'INFLUXDB_PASSWORD={data.get("influxdb_password", "")}\n')
        env_file.write(f'INFLUXDB_ORGANIZATION={data.get("influxdb_organization", "")}\n')
        env_file.write(f'INFLUXDB_BUCKET={data.get("influxdb_bucket", "")}\n')
        env_file.write(f'INFLUXDB_RETENTION={data.get("influxdb_retention", "")}\n')
        env_file.write(f'INFLUXDB_TOKEN="{data.get("influxdb_token", "")}"\n\n')

        env_file.write("# GRAFANA CONFIG\n")
        env_file.write(f'GRAFANA_USERNAME={data.get("grafana_username", "")}\n')
        env_file.write(f'GRAFANA_PASSWORD={data.get("grafana_password", "")}\n')

# Usage
print("\n" + "="*65)
print(f"Starting the initial setup process...")
yaml_to_env('initial_setup_variables.yaml', '.env')
print(f"File .env created or modified successfully!")
print(f"Update config/servers_inventory.yaml before starting containers.")
print("="*65 + "\n")