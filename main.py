import paramiko
import zipfile
import shutil
import xml.etree.ElementTree as ET
import logging

logging.basicConfig(level=logging.DEBUG)

command_ls = "ls"
command_copyfrom = "cp /home/nayapay/PayPakIssuingSimulatorUAT.jar D:/Repositories"
command_copyto = "cp D:/Repositories/PayPakIssuingSimulatorUAT.jar /home/nayapay"
command_runjar = "java -jar PayPakIssuingSimulatorUAT.jar"

def create_ssh_connection(hostname, port, username, password):
  try:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, port, username, password)
    return client
  except Exception as e:
    print(f"Failed to connect to {hostname}:{port} - {e}")
    return None

def execute_command(client, command):
  try:
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode()
    error = stderr.read().decode()
    return output, error
  except Exception as e:
    print(f"Failed to execute command {command} - {e}")
    return None, None

if __name__ == "__main__":

  # Create ssh connection with server
  # copy latest file from the server to local
  # backup the original file
  # modify the xml inside the jar
  # copy the modified jar back to the server
  # run the jar
  # get logs from the server
  # close the connection
  
  hostname = "192.168.37.87" #nayapay@NP_UAT_WALLET
  port = 10984
  username = "nayapay"
  password = "vaulsys"
  
  # client = create_ssh_connection(hostname, port, username, password)
  # if client:
  #   output, error = execute_command(client, command_ls)
  #   if output:
  #     print("Output:\n", output)
  #   if error:
  #     print("Error:\n", error)

  #   output, error = execute_command(client, command_copyfrom)

  #assuming simulator jar is copied to local machine

  jar_path = "D:/Repositories/PayPakIssuingSimulatorUAT.jar"
  temp_jar = "PayPakIssuingSimulatorUAT_temp.jar"
  xml_to_modify = "ir/fanap/test/msgXMLSrc/onelink/48_merchInvoice_05032025_15.xml"

  with zipfile.ZipFile(jar_path, 'r') as jar:
      xml_data = jar.read(xml_to_modify)
      with jar.open(xml_to_modify) as xml_file:
        xml_content = xml_file.read().decode("utf-8")

  # Parse and modify the XML
  root = ET.fromstring(xml_data)
  # print(xml_content)

  print("Enter Amount Txn (DE-4): ")
  amount_txn = input()
  print("Enter Source Account (DE-102): ")
  src_account = input()
  print("Enter Destination Account (DE-103): ")
  dest_account = input()

  for field in root.findall("field"):
      if field.get("id") == "4":  #Amount Txn
        field.set("value", amount_txn)
      elif field.get("id") == "102":  #Source Account
        field.set("value", src_account)
      elif field.get("id") == "103":  #Destination Account
        field.set("value", dest_account)
      elif field.get("id") == "120":
        temp = field.get("value")
        temp = temp.replace(temp[0:20], dest_account[:20])
        field.set("value", temp)

  # Convert the modified XML back to bytes
  modified_xml = ET.tostring(root, encoding="utf-8")

  # Create a new JAR with the modified XML
  with zipfile.ZipFile(jar_path, 'r') as jar, zipfile.ZipFile(temp_jar, 'w') as new_jar:
      for item in jar.infolist():
          if item.filename == xml_to_modify:
              # Replace with modified XML
              new_jar.writestr(item.filename, modified_xml)
          else:
              # Copy everything else unchanged
              new_jar.writestr(item, jar.read(item.filename))

  # Replace the original JAR with the modified one
  shutil.move(temp_jar, jar_path)

  print("XML inside JAR modified successfully!")

  #   client.close()