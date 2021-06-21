import os
import sys
import time
import copy
import pymongo
sys.path.append(os.path.join(os.path.dirname(__file__)))  # ./_statisticalTransaction

from datetime import datetime
from module import create_default_dic
from module import illegal_transaction

# 트랜잭션 데이터 삽입
connectionLocalIP_ = pymongo.MongoClient('127.0.0.1',1000)
Processed_Bitcoin_data_DB = connectionLocalIP_.get_database('Bitcoin')
tx_Collection = Processed_Bitcoin_data_DB.get_collection('Transaction')

# blockinfo_dic은 tx 상세정보에 기입할 블록 상세 정보
class blockData_Object(object):
    def __init__(self, blockData):
        self.block_basicInfo = {          
        '_id': int(blockData['height']),
        'timestamp': blockData['time'],
        'date time': str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(blockData['time']))),
        'nTx': int(blockData['nTx'])
    }

    def block_basicData(self):
        return self.block_basicInfo

def connect():
    rpc_connection = AuthServiceProxy("http://daphnea:5287710@127.0.0.1:8332", timeout=240)
    return rpc_connection

def transactionData(blockInfo):
    # blockinfo_dic은 tx 상세정보에 기입할 블록 상세 정보
    block = blockData_Object(blockInfo)
    blockinfo_dic = block.block_basicData()

    transaction_info = []
    transaction_data = []  
    # 트랜잭션 데이터 수정 과정
    for txInfo in blockInfo['tx']:
        #update_transactionData tx 데이터 변형
        txInfo_dic = update_transactionData(blockinfo_dic['_id'], txInfo)
        transaction_info.append(txInfo_dic)     

    # insertTransaction - 트랜잭션 vout 데이터 insert
    # vin_process_trabsaction - 트랜잭션 vin 데이터 insert
    transaction_data = insertTransaction(blockinfo_dic, transaction_info, blockinfo_dic['nTx'])
    vin_process_transaction(transaction_data, transaction_info, blockinfo_dic['nTx'])

    
def update_transactionData(insert_blockHeight, txInfo):
    txid = str(txInfo['txid'])
    txinfo_dic = {'_id':str(txid)}
    txinfo_dic.update(txInfo)
    txinfo_dic['block height'] = int(insert_blockHeight)

    return txinfo_dic

def insertTransaction(blockinfo, transactionData, nTx):
    blockinfo_dic = transactionData[0]
    transaction_data = []
    
    txinfo_dic = insert_coinbaseTx(blockinfo, blockinfo_dic)
    transaction_data.append(txinfo_dic)

    for index in range(1, nTx):
        blockinfo_dic = transactionData[index]         
        txinfo_dic_ = insert_normalTx(blockinfo, blockinfo_dic)
        transaction_data.append(txinfo_dic_)

    return transaction_data
    #tx_Collection.insert_many(transaction_data)
    #print('Inserted Block Transaction' + str(blockinfo['_id']))

def process_vout_data(txRawInfo, txInfo):
    vout_value = 0

    for voutInfo in txRawInfo['vout']:
        value = float(voutInfo['value'])
        vout_value += value

        address_dic=voutInfo['scriptPubKey']
        address_info = {
            'index': voutInfo['n'] 
        }

        if 'addresses' in address_dic.keys():
            address = address_dic['addresses'][0]
            address_info['address'] = str(address)
                            
            if address not in txInfo['vout address list']:
                txInfo['vout address list'].append(str(address))

        address_info['type'] = str(address_dic['type'])
        address_info['receive value'] = round(float(value),8) 
        address_info['state']=str('Unspent')  
        address_info['scriptPubKey'] = {
            "asm": voutInfo['scriptPubKey']['asm'],
            "hex": voutInfo['scriptPubKey']['hex']
        }

        txInfo['vout'].append(address_info)

    txInfo['vout value'] = round(float(vout_value),8)
    return txInfo

def insert_coinbaseTx(blockinfo, txRawInfo):
    txInfo_ = create_default_dic.create_coinbase_Txinfo(blockinfo, txRawInfo)
    txInfo = process_vout_data(txRawInfo, txInfo_)
     
    txInfo['vin'].append(txRawInfo['vin'][0])                        
    txInfo['mining reward'] = 0
    txInfo['mining fee'] = 0

    return txInfo                        

def insert_normalTx(blockinfo, txRawInfo):
    txInfo_ = create_default_dic.create_normal_Txinfo(blockinfo, txRawInfo)
    txInfo = process_vout_data(txRawInfo, txInfo_)
                                                                                 
    txInfo['vin value']= 0
    txInfo['fee']= 0

    # 불법거래 탐지
    #illegal_ = illegal_transaction.main(txRawinfo)
    #if illegal_ == 1:
    #    txInfo['illegality type'] = 'Illegal Transaction'
        
    return txInfo

def vin_process_transaction(transaction_data, block_tx_info, nTx):
    miningFee = 0.0
    fee_ = 0.0

    for index in range(1, nTx):
        tx_vinData = block_tx_info[index]['vin']
        fee_ = vin_insert_normalTx(transaction_data[index], tx_vinData)
        miningFee += fee_

    vin_insert_coinbaseTx(transaction_data[0], miningFee)

# 블록에 포함된 normal transaction에서 fee를 다 더한 후, coinbase transaction 데이터 수정 
def vin_insert_coinbaseTx(basic_txData, miningFee):
    vout_value = float(basic_txData['vout value'])
    vin_value = vout_value - miningFee
    
    basic_txData['mining reward'] = round(float(vin_value),8)
    basic_txData['mining fee'] = round(float(miningFee),8)

    tx_Collection.insert(basic_txData)

# normal transaction의 vin에서 UTXO 정보 확인 후, 이전 트랜잭션의 vout 데이터 수정
def vin_insert_normalTx(basic_txData, tx_vinData):
    transaction_id = basic_txData['_id']
    vout_value = float(basic_txData['vout value'])

    transaction_vin_data = []
    n_vin = len(tx_vinData)
    vin_value = 0.0

    for n in range(0, n_vin):
        vin_transaction_id = tx_vinData[n]['txid']
        tranasaction_location = tx_vinData[n]['vout']

        #vin txid 정보 query
        tx_data_ = tx_Collection.find({'_id':vin_transaction_id})
        vinTx_ = tx_data_[0]
        vininfo = vinTx_['vout'][tranasaction_location]          

        vin_address_info = {
            'index': vininfo['index'] 
        }

        value = float(vininfo['receive value'])
        vin_value += value

        if 'address' in vininfo.keys():
            vin_address = vininfo['address']
            vin_address_info['address'] = str(vin_address)             

            if vin_address not in basic_txData['vin address list']:
                basic_txData['vin address list'].append(str(vin_address))

        vin_address_info['type'] = str(vininfo['type'])
        vin_address_info['txid'] = str(vin_transaction_id)
        vin_address_info['block height'] = int(vinTx_['block height'])
        vin_address_info['send value'] = round(float(value),8)
        vin_address_info['scriptPubKey']=vininfo['scriptPubKey']
        vin_address_info['scriptSig'] = tx_vinData[n]['scriptSig']

        transaction_vin_data.append(vin_address_info)

        spend_info={ 
            'spent block height': basic_txData['block height'],
            'spent block timestamp': basic_txData['timestamp'],
            'spent block date time': basic_txData['date time'],
            'spent transaction': str(transaction_id),
            'index': int(n),
        }
        scriptPubKey = vinTx_['vout'][tranasaction_location].pop('scriptPubKey')
        vinTx_['vout'][tranasaction_location]['state'] = str('Spent') 
        vinTx_['vout'][tranasaction_location]['spend info'] = spend_info
        vinTx_['vout'][tranasaction_location]['scriptPubKey'] = scriptPubKey            
        vinTx_['vout'][tranasaction_location]['scriptSig'] = tx_vinData[n]['scriptSig']

        vin_query = {'_id':str(vin_transaction_id)}
        vin_new_value = {'$set':
        {
            'vout': vinTx_['vout']
            }
        }

        tx_Collection.update_one(vin_query, vin_new_value, upsert=True)

    if(vin_value==vout_value):
        fee = 0.0
    else:
        fee = vin_value - vout_value    

    basic_txData['vin'] = transaction_vin_data
    basic_txData['vin address list'] = basic_txData['vin address list']
    basic_txData['vin value'] = round(float(vin_value),8)
    basic_txData['fee'] = round(float(fee),8)

    tx_Collection.insert(basic_txData)
    return fee
