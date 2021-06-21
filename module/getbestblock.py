import os
import sys
import time
import simplejson as json
sys.path.append(os.path.dirname(__file__))

from datetime import datetime
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def connect():
    #When executing the code, the user id and password information of rpc_connection must be modified 
    rpc_connection =  AuthServiceProxy("http://user_id:user_password@127.0.0.1:8332", timeout=240)
    return rpc_connection

def bitcoin_getBestBlock():
    success = 0
    while(success==0):
        try:
            rpc_connection = connect()
            get_bestblockhash = rpc_connection.getbestblockhash()
            get_bestblockinfo = rpc_connection.getblock(get_bestblockhash,1)
            success=1
        except:
            print('Broken pipe')
            sys.exit()

    get_bestblockheight = get_bestblockinfo['height']  
    return get_bestblockheight
