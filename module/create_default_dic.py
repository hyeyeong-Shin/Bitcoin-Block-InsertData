import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__)))  # ./_statisticalTransaction

def create_coinbase_Txinfo(blockinfo, txRawinfo):
    txinfo = {
        '_id':str(txRawinfo['_id']),
        'hash': txRawinfo['hash'],
        'hex': txRawinfo['hex'],
        'block height': txRawinfo['block height'],
        'timestamp': blockinfo['timestamp'],
        'date time': blockinfo['date time'],
        'txType': 'coinbase',
        'illegality type': 'None',
        'version': txRawinfo['version'],
        'size': txRawinfo['size'],
        'vsize': txRawinfo['vsize'],
        'weight': txRawinfo['weight'],
        'locktime': txRawinfo['locktime'],
        'vin': [],
        'vout': [],
        'vout address list': [],
        'mining reward': '',
        'mining fee': '',
        'vout value': '',
    }   

    return txinfo   

def create_normal_Txinfo(blockinfo, txRawinfo):
    txinfo = {
        '_id':str(txRawinfo['_id']),
        'hash': txRawinfo['hash'],
        'hex': txRawinfo['hex'],
        'block height': txRawinfo['block height'],
        'timestamp': blockinfo['timestamp'],
        'date time': blockinfo['date time'],
        'txType': 'normal',
        'illegality type': 'None',
        'version': txRawinfo['version'],
        'size': txRawinfo['size'],
        'vsize': txRawinfo['vsize'],
        'weight': txRawinfo['weight'],
        'locktime': txRawinfo['locktime'],
        'vin': [],
        'vout': [],
        'vin address list': [],
        'vout address list': [],
        'vin value': '',
        'vout value': '',
        'fee': '',
    }            

    return txinfo

