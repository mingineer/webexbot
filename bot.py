from webexteamssdk import WebexTeamsAPI, ApiError
import os

# Initialize the Webex Teams API object
api = WebexTeamsAPI(access_token='${ACCESS_TOKEN')
room = '${ROOM_ID}'
email = '${EMAIL}'
log_path = '${LOG_FILE}'


#Create a chat room
def create_rooms():
  try:
      rooms = api.rooms.list()
      for room in rooms:
          print(f"Room ID: {room.id}, Title: {room.title}")
      room = api.rooms.create(title='Managed Alert')
      print(f"Chat room created with ID: {room.id}")
  except ApiError as e:
      print(f"Failed to create chat room: {e}")

# Retrieve the list of rooms
def list_rooms():
  try:
      rooms = api.rooms.list()
      for room in rooms:
          print(f"Room ID: {room.id}, Title: {room.title}")
  except ApiError as e:
      print(f"Failed to retrieve room list: {e}")


# Invite the user to the room
def invite_user_to_room(room_id, account):
  try:
      api.memberships.create(roomId=room_id, personEmail=email)
      print(f"Invitation sent to {email}")
  except ApiError as e:
      print(f"Failed to invite user: {e}")


# Delete the chat room
def delete_rooms(room_id):
  # Delete the chat room
  try:
      api.rooms.delete(roomId=room_id)
      print(f"Chat room with ID {room_id} has been deleted.")
  except ApiError as e:
      print(f"Failed to delete chat room: {e}")

def send_messages(room_id, texts):
  try:
      api.messages.create(roomId=room_id, text=texts)
      print('message sent successfully.')
  except Exception as e:
      print(f'Failed to send hello message: {e}')

# Check OpenStack Service Status
def check_svc_status(log_path, text_check, svc):
  status = os.popen('cat {}  | grep -i "{}"'.format(log_path, text_check)).read().strip()
  err_status = os.popen('cat {}  | grep -A1 "{}"| sed -n "2p"'.format(log_path, svc)).read().strip()

  if status != text_check :
      msg = '## Check OpenStack {} Status\n{}'.format(svc, err_status)
      send_messages(room, msg)

# Check OpenStack Log Status
def check_log_status(log_path, text_check, svc):
  sys_status = os.popen('cat {}  | grep -A1 "{}" | sed -n "2p"'.format(log_path, text_check)).read().strip()

  if sys_status != "" :
      msg = '## Check {} Status\n{}'.format(svc, sys_status)
      send_messages(room, msg)


def check_bit_error(log_path, text_check, bit):
  current_bit = os.popen("cat {}  | grep -A1 '{}' | sed -n '2p' | awk -F count '{{print $2}}'".format(log_path, text_check)).read().strip()

  if current_bit != '' and int(current_bit) > bit:
      msg = '## Check {}\n{}'.format(text_check, current_bit)
      send_messages(room, msg)


# Check PaceMaker Log Status
def check_pacemaker_status(log_path, text_check, svc):
  sys_status = os.popen('cat {}  | grep -A2 "{}" | sed -n "3p"'.format(log_path, svc)).read().strip()

  if sys_status != text_check :
      msg = '## Check {} Status\n{}'.format(svc, sys_status)
      send_messages(room, msg)

def check_netapp_usage(log_path, text_check):
  disk_usage = os.popen("cat {}  | grep 10.210 | awk '{{print $5}}' | sed 's/%//g'".format(log_path)).read().strip()
  disk_usage = disk_usage.replace('\n', ' ').split()
  
  flag = 0


  for i in disk_usage:
    flag = flag+1
    if int(i) > 80:
      critical_disk = os.popen("cat {}  | grep 10.210 | sed -n '{}p'".format(log_path, flag)).read().strip()
      msg = '## Check {} Status\n{}'.format(text_check, critical_disk)
      send_messages(room, msg) 


# Check Ceph Status
def check_ceph_status(log_path, text_check, svc):
  status = os.popen('cat {}  | grep -i "{}"'.format(log_path, text_check)).read().strip()
  err_status = os.popen('cat {}  | grep -A1 "{}"| sed -n "2p"'.format(log_path, svc)).read().strip()

  if status != text_check :
      msg = '## Check {}\n{}'.format(svc, err_status)        
      send_messages(room, msg) 


def check_ceph_usage(log_path, text_check):
  disk_usage = os.popen("cat {}  | grep -A4 '{}' | sed -n '3,5p' | awk '{{print $4}}'".format(log_path, text_check)).read().strip()
  disk_usage = disk_usage.replace('\n', ' ').split()
  
  flag = 0

  for i in disk_usage:
    flag = flag+1
    if float(i) > 80:
      critical_disk = os.popen("cat {}  | grep -A4 '{}' | sed -n '3,5p' | sed -n '{}p'|awk '{{print $1, $4}}'".format(log_path, text_check, flag)).read().strip()
      msg = '## Check {} Status\n{}'.format(text_check, critical_disk)
      send_messages(room, msg) 

# Check Ceph Fault Disk
def check_ceph_fault_disk(log_path, text_check, svc):
  sys_status = os.popen('cat {}  | grep -A1 "{}" | sed -n "2p"'.format(log_path, text_check)).read().strip()

  if sys_status != "" :
      msg = '## Check {}\n{}'.format(svc, sys_status)
      send_messages(room, msg)



# main def
def main():
  check_svc_status(log_path, "Compute Service is OK", "Compute Service")
  check_svc_status(log_path, "Network Service OK", "Network Service")
  check_svc_status(log_path, "Cinder Service OK", "Cinder Service")
  check_log_status(log_path, "OpenStack System Log Messages", "OpenStack System Log Messages")
  check_bit_error(log_path, "OpenStack 1Bit Error Log Messages", 24)
  check_log_status(log_path, "OpenStack Rabbit MQ Error", "RabbitMQ")
  check_pacemaker_status(log_path, "Pacemaker is OK", "Pacemaker Error Log Messages")
  check_netapp_usage(log_path, "NetApp")
  check_ceph_status(log_path, "HEALTH IS OK", "Ceph Status")
  check_ceph_usage(log_path, "Ceph Capacity")
  check_ceph_fault_disk(log_path, "Ceph Fault Disk", "Ceph Fault Disk")
  check_log_status(log_path, "Ceph Near Full Check", "OSD")
  check_log_status(log_path, "Ceph Log Messages", "Ceph Log")
  check_bit_error(log_path, "Ceph 1Bit Log Messages", 24)

  
if __name__ == '__main__':
    main()

