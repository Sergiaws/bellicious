import json
#function for the creation of the json file with the configuration data of the application
def create_config_json():
    config = {}

    print("Please provide the following configuration details (in English):")
    config['host'] = input("Enter host: ")
    config['user'] = input("Enter user: ")
    config['password'] = input("Enter password: ")
    config['dbname'] = input("Enter dbname: ")
    config['server'] = input("Enter server: ")
    config['port'] = input("Enter port: ")

    while True:
        usetls = input("Use TLS? (Enter t for True / f for False): ")
        if usetls.lower() == 't':
            config['usetls'] = True
            break
        elif usetls.lower() == 'f':
            config['usetls'] = False
            break
        else:
            print("Invalid input. Please enter 't' for True or 'f' for False.")

    while True:
        usessl = input("Use SSL? (Enter t for True / f for False): ")
        if usessl.lower() == 't':
            config['usessl'] = True
            break
        elif usessl.lower() == 'f':
            config['usessl'] = False
            break
        else:
            print("Invalid input. Please enter 't' for True or 'f' for False.")

    config['mailserver'] = input("Enter mailserver: ")
    config['mailport'] = int(input("Enter mailport: "))
    config['mailusr'] = input("Enter mailusr: ")
    config['mailpass'] = input("Enter mailpass: ")
    config['salt'] = input("Enter salt: ")
    config['secret'] = input("Enter secret: ")

    with open('config.json', 'w') as json_file:
        json.dump(config, json_file, indent=4)

    print("Config JSON file created successfully!")

if __name__ == '__main__':
    create_config_json()
