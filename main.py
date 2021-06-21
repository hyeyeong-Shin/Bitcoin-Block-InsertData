import os
import sys
import time
sys.path.append(os.path.dirname(__file__))

from module import check_DB_bestBlockHeight
from module import getbestblock
from module import insertBlock_

def main():
    start = check_DB_bestBlockHeight.database_bestBlockHeight() 
    #start = 386780
    end = getbestblock.bitcoin_getBestBlock()
    #end = 100000
    
    if((start<end)and(start!=end)): 
        insertBlock_.insert_blockData(start, end)
        
if __name__=="__main__":
    while(1):
        main()
        
        now = time.localtime()
        print()
        print('%04d/%02d/%02d %02d:%02d:%02d'% (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        time.sleep(60)

        now = time.localtime()
        print('%04d/%02d/%02d %02d:%02d:%02d'% (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))
        print()