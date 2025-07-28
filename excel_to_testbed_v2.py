import pandas as pd
import yaml
import sys

# Custom YAML representer to force quotes on specific strings
class QuotedStr(str):
    pass

def quoted_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

yaml.add_representer(QuotedStr, quoted_presenter)

def generate_testbed_yaml(excel_file, output_file='testbed_demo.yaml', sheet_name=0):
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    testbed_dict = {
        'testbed': {
            'name': 'Generated Testbed',
            'devices': {}
        }
    }

    for index, row in df.iterrows():
        hostname = str(row['hostname']).strip()
        alias_raw = row.get('alias', hostname)
        alias = QuotedStr(str(alias_raw).strip())
        os = QuotedStr(str(row['os']).strip())
        type = QuotedStr(str(row['type']).strip())
        platform = str(row['platform']).strip()
        ip = str(row['mgmt_ip']).strip()
        port = int(row.get('mgmt_port', 22))
        username = str(row['username']).strip()
        password = str(row['password']).strip()
        enable_password = row.get('enable_password', None)
        connection_type = str(row.get('connection_type', 'ssh')).strip()
        connection_timeout = row.get('connection_timeout')

        cli_connection = {
            'protocol': connection_type,
            'ip': ip,
            'port': port
        }

        if pd.notna(connection_timeout):
            cli_connection['arguments'] = {
                'connection_timeout': int(connection_timeout)
            }

        device_dict = {
            'alias': alias,
            'type': type,
            'os': os,
            #'type': QuotedStr('router'),
            'platform': platform,

            'credentials': {
                'default': {
                    'username': username,
                    'password': password
                }
            },
            'connections': {
                'cli': cli_connection
            }
        }

        if pd.notna(enable_password) and str(enable_password).strip().lower() != 'nan' and str(enable_password).strip() != "":
            device_dict['credentials']['enable'] = {
                'password': str(enable_password).strip()
            }

        testbed_dict['testbed']['devices'][hostname] = device_dict

    with open(output_file, 'w') as file:
        yaml.dump(testbed_dict['testbed'], file, sort_keys=False)

    print(f"[✓] Testbed YAML written to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python excel_to_testbed.py <devices.xlsx>")
    else:
        generate_testbed_yaml(sys.argv[1])
