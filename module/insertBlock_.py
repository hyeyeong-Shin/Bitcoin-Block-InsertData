import os
import sys
import time
import pymongo
import simplejson as json
sys.path.append(os.path.join(os.path.dirname(__file__)))  # ./_statisticalTransaction

from datetime import datetime
from module import transaction_
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

connectionLocalIP = pymongo.MongoClient('127.0.0.1',1000)
localDB = connectionLocalIP.get_database('Bitcoin')
block_Collection = localDB.get_collection('Block')
blockHeight_Collection = localDB.get_collection('BlockHeight')
tx_Collection = localDB.get_collection('Transaction')

def connect():
    #When executing the code, the user id and password information of rpc_connection must be modified 
    rpc_connection =  AuthServiceProxy("http://user_id:user_password@127.0.0.1:8332", timeout=240)
    return rpc_connection

def getblock(blockhash, option):
    rpc_connection = connect()
    success = 0
    try_count=0

    while(success==0): 
        try:
            blockdata_ = rpc_connection.getblock(blockhash,option)
            success=1
        except:
            print('Broken pipe - insertBlock_.getblock.py')

            if(try_count==0):
                try_count=1
                time.sleep(10)
            else:    
                connectionLocalIP.close()
                sys.exit()

    return blockdata_

def create_dataType(blockhash):
    blockData_ = getblock(blockhash, 1)
    blockinfo_dump=json.dumps(blockData_)
    blockinfo = json.loads(blockinfo_dump)

    blockinfo_dic = {'_id': str(blockinfo['hash']), 'height': int (blockinfo['height'])}
    blockHeight_dic = {'_id': int (blockinfo['height']), 'hash': str(blockinfo['hash']) }
        
    basicinfo_dic = {
        'timestamp': blockinfo['time'],
        'mediantime': blockinfo['mediantime'],
        'date time': str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(blockinfo['time']))),
        'nTx': int(blockinfo['nTx']),
        'size': float(blockinfo['size']),
        'strippedsize': float(blockinfo['strippedsize']),
        'version': int(blockinfo['version']),
        'versionHex': blockinfo['versionHex'],            
        'nonce': float(blockinfo['nonce']),
        'bits': blockinfo['bits'],
        'difficulty': float(blockinfo['difficulty']),
        'chainwork': blockinfo['chainwork'],
        'merkleroot': blockinfo['merkleroot'],
        'tx': blockinfo['tx'],  
    }       

    if int(blockinfo['height']) is 0:
        basicinfo_dic.update({'previousblockhash': '-', 'nextblockhash': blockinfo['nextblockhash']})
    else:
        basicinfo_dic.update({'previousblockhash': blockinfo['previousblockhash'], 'nextblockhash': blockinfo['nextblockhash']})

    blockinfo_dic.update(basicinfo_dic)
    blockHeight_dic.update(basicinfo_dic)
    block_Collection.insert(blockinfo_dic)
    blockHeight_Collection.insert(blockHeight_dic)
    print("inserted blockdata: " + str(blockinfo['height']) + ' , nTx: '+str(blockinfo['nTx']))

def removeTx(blockhash):
    blockData = getblock(blockhash, 1)
    blockinfo_dump=json.dumps(blockData)
    blockinfo = json.loads(blockinfo_dump)    

    txList = blockinfo['tx']

    for index in range(0, int(blockinfo['nTx'])):
        txID = blockinfo['tx'][index]
        tx_Collection.remove({'_id':txID})

        print('removed Tx '+str(index+1)+'/'+str(blockinfo['nTx'])+' - '+str(txID))

def insert_blockData(start_, end_):
    rpc_connection = connect()

    start_blockHeight = int(start_) + 1
    last_blockHeight = int(end_) + 1
    blockhashs = []

    print('start: '+str(start_blockHeight))
    print('end: '+str(end_)) 

    for index in range(start_blockHeight, last_blockHeight):
        blockhash = rpc_connection.getblockhash(index)
        print(str(index))
        blockhashs.append(blockhash)

    removeTx(blockhashs[0])

    for blockhash in blockhashs:
        ## getblock??? 2??? ?????? ?????? ##
        # getblock(blockhash, 1)??? ?????? txid??? ?????? ?????? ??????
        # ?????????, getblock(blockhash, 2)??? ?????? tx ?????? ?????? ???????????? blockcollection??? ?????? ?????? ???????????? ??????
        # getblock(blockhash, 2)??? ???????????? ????????? ???, txid??? ????????? ??? ????????? 3000?????? ?????? ??????????????? ????????? ?????? ??????????????? ????????? ?????????

        blockTxData = getblock(blockhash, 2)
        blockTxinfo_dump=json.dumps(blockTxData)
        blockTxinfo = json.loads(blockTxinfo_dump)
        transaction_.transactionData(blockTxinfo)

        create_dataType(blockhash)
        #print("inserted blockdata:" + str(blockTxinfo['height']))

    connectionLocalIP.close()       
