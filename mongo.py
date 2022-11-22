import pymongo
from pymongo import MongoClient


# username = quote_plus('<mongodetran20222001 >')
# password = quote_plus('<mongodetran20222001>')
# cluster = 'cluster0.gz0srkn.mongodb.net'
# authSource = 'authSource'
# authMechanism = 'authMechanism'


conn_str = "mongodb+srv://root:detranconfigdb@clusterdetranconfig.qbvweli.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(conn_str)

dataBase = client['configdb']

collection_detran_rn = dataBase['detran_rn']
collection_log_detran_rn = dataBase['log_detran_rn']

# result = collection_log.find_one({
#     "placa" : "MXO2152"
# })
