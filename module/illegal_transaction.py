import os
import sys
import csv
import time
import requests
import simplejson as json
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

def connect():
    rpc_connection = AuthServiceProxy("http://daphnea:5287710@127.0.0.1:8332", timeout=240)
    return rpc_connection

def getTransaction(blockhash, option):
    rpc_connection = connect()
    success = 0
    try_count=0

    while(success==0): 
        try:
            blockdata_ = rpc_connection.getrawtransaction(blockhash,option)
            success=1
        except:
            print('Broken pipe - getrawtransaction.py')

            if(try_count==0):
                try_count=1
                time.sleep(10)
            else:    
                sys.exit()

    return blockdata_

def getdetails(txid):
	print(str(txid))
	get_txData = getTransaction(txid,2)
	#print(str(txid))
	txdata_dump = json.dumps(get_txData)
	tx_detail = json.loads(txdata_dump)

	vin = len(tx_detail['vin'])
	vout = len(tx_detail['vout'])
	size = tx_detail['size']

	in_value = 0
	in_addr = set()
	
	for i in range(0, vin):
		sub_txid = tx_detail['vin'][i]['txid']
		get_sub_txData = getTransaction(sub_txid, 2)
		sub_txdata_dump = json.dumps(get_sub_txData)
		tx_sub_detail = json.loads(sub_txdata_dump)

		utxo_index = tx_detail['vin'][i]['vout']
		print(str(len(tx_sub_detail['vout'])))
		in_value += tx_sub_detail['vout'][utxo_index]['value']
		in_addr.add(tuple(tx_sub_detail['vout'][utxo_index]["scriptPubKey"]['addresses']))

	out_value = 0
	out_addr = set()
	for j in range(0, vout):
		out_value += tx_detail['vout'][j]['value']
		try:
			out_addr.add(tuple(tx_detail['vout'][j]["scriptPubKey"]['addresses']))
		except KeyError:
			continue

	fee = in_value - out_value
	result = [vin, vout, in_value, out_value, fee, len(in_addr), len(out_addr), size, out_value]
	return result

def writeCsv(txid, data):
#	filename_ = './transaction_csv/' + str(txid) + '.csv'
	filename_ = '/home/daphneashin/bitcoin-detection/transaction_csv/' + str(txid) + '.csv'

	row_name = ["vin","vout","vin_value","vout_value","fee","input_addr","output_addr","size","value"]
	fw = open(filename_, 'w')
	wr=csv.writer(fw)
	wr.writerow(row_name)
	wr.writerow(data)
	fw.close()

def main(txid_):
	txid = txid_['_id']
	#args = "".join(sys.argv[1:])
	data = getdetails(txid)
	writeCsv(txid, data)
	
	os.system("/usr/bin/Rscript /home/daphneashin/bitcoin-detection/illegal_transaction.r "+str(txid))
	f_open = open('/home/daphneashin/bitcoin-detection/transaction_csv/'+txid+'.txt', 'r')
	data = f_open.read()
	f_open.close()
	print(str(data))
	print()
	return int(data)
	#f_open.close()
