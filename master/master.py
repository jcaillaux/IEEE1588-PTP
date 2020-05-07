import socket
import sys
from datetime import datetime
import time

server_socket = None
#ADDRESS = "10.0.0.19"
#ADDRESS = "192.168.137.2"
ADDRESS = "127.0.0.1"
PORT = 2468
NUM_OF_TIMES = 1000

OFFSETS = []
DELAYS = []

def main():
  try:
    global server_socket
    print("Creating socket...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  except socket.error as e:
    print("Error creating socket: " + str(e) + ". Exitting...")
    server_socket.close();
    sys.exit(-1)

  try:
    print("Connecting to socket... " + str(ADDRESS) + ":" + str(PORT))
    server_socket.connect((ADDRESS, PORT))
  except socket.error as e:
    print("Error connecting to socket: " + e + ". Exitting...")
    server_socket.close()
    sys.exit(-1)

  sync_clock()

def sync_clock():
  print("\nSyncing time with " + ADDRESS + ":" + str(PORT) + "...")
  send("sync")
  t, resp = recv()
  send(str(NUM_OF_TIMES))

  t, resp = recv()

  if(resp == "ready"):
    time.sleep(1) #to allow for server to get ready
    for i in range(NUM_OF_TIMES):
      ms_diff = sync_packet()
      sm_diff = delay_packet()

      offset = (ms_diff - sm_diff)/2;
      delay = (ms_diff + sm_diff)/2;

      OFFSETS.append(offset)
      DELAYS.append(delay)

      send("next")

    print("\n\nAVG OFFSET: %sns" % str(sum(OFFSETS) * 1000000000L / len(OFFSETS)) + "\nAVG DELAY: %sns"% str(sum(DELAYS) * 1000000000L / len(DELAYS)))
    print("\n\nMIN OFFSET: %sns" % str(min(OFFSETS) * 1000000000L) + "\nMIN DELAY: %sns"% str(min(DELAYS) * 1000000000L))
    print("\n\nMAX OFFSET: %sns" % str(max(OFFSETS) * 1000000000L) + "\nMAX DELAY: %sns"% str(max(DELAYS) * 1000000000L))
    print("\nDone!")
  else:
    print("Error syncing times, received: " + resp)

def sync_packet():
  t1 = send("sync_packet")
  t, t2 = recv()
  return float(t2) - float(t1)

def delay_packet():
  send("delay_packet")
  t4, t3 = recv()
  return float(t4) - float(t3)


def recv():
  try:
    msg = server_socket.recv(4096)
    t = get_time()
    return (t, msg)
  except socket.error as e:
    print("Error while receiving request: " + str(e))
    server_socket.close()
    sys.exit(-1)

def send(data):
  try:
    server_socket.sendall(str(data))
    t = get_time()
    return t
    #print "Sent:" + str(data)
  except socket.error as e:
    print("Error while sending request: " + str(e))
    print("Tried to send: " + data)
    server_socket.close()
    sys.exit(-1)

def get_time():
  return time.time()

if __name__ == '__main__':
    main()
