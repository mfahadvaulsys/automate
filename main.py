import paramiko
import logging

logging.basicConfig(level=logging.DEBUG)

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
  hostname = "192.168.37.87"
  port = 10984
  username = "nayapay"
  password = "vaulsys"
  
  client = create_ssh_connection(hostname, port, username, password)
  if client:
    command = "ls"
    output, error = execute_command(client, command)
    if output:
      print("Output:\n", output)
    if error:
      print("Error:\n", error)
    client.close()