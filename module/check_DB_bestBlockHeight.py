import os
import sys
import time
import pymongo
sys.path.append(os.path.dirname(__file__))

connectionLocalIP = pymongo.MongoClient('210.125.31.245',1000)
localDB = connectionLocalIP.get_database('Bitcoin')
block_Collection = localDB.get_collection('BlockHeight')
tx_Collection = localDB.get_collection('Transaction')

def database_bestBlockHeight():
    block_count = block_Collection.find({}).sort("_id",-1).count()
#    return lastBlock[0]['_id']

    if block_count !=0 :
        lastBlock = block_Collection.find({}).sort("_id",-1).limit(1)
        lastBlockHeight = lastBlock[0]['_id']
        
        gap = block_count - lastBlockHeight
        connectionLocalIP.close()
        if gap == 1 :
            return lastBlockHeight
        else :
            return -1    
    else :
        return -1

        