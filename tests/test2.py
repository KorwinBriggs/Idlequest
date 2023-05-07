


import time



#------------- GAME LOOP -------------#
interval = 1 #1 second
elapsed = 0

while(True): 
    time.sleep(interval - time.monotonic() % interval) #sleep until next second
    print(time.strftime("%H:%M:%S"))
    elapsed += 1
   #  if (time.strftime('%S') == '00'):
   #      interval = 2 

