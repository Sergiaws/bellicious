import json
with open ('config.json') as json_file:
    config = json.load (json_file)
#here we set the configuration data
host = config['host']
user = config['user']
password = config['password']
dbname = config['dbname']
server = config['server']
port = config['port']
secret = config['secret']
salt = config['salt']
mailserver = config['mailserver']
mailport = config['mailport']
usetls = config['usetls']
usessl = config['usessl']
mailusr = config['mailusr']
mailpass = config['mailpass']
API_KEY="e17960485c32a51f47f950aa55a4b86e9c739831"