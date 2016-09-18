import sys
import os
import socket
import threading
import select

#A chatServer class that handles communication between clients
#Arguments: none
#Returns: none
#Result: Creates a chatServer object
#Object variables:
#self.sock: The server socket
#self.connections: A list of connections to be used by select()
#self.users: A dictionary of users that maps a socket to a user object
class chatServer():
  def __init__(self):
    self.HOST = ''
    self.PORT = 46000
    self.sock = self.bind_port()
    self.connections = [self.sock,sys.stdin]
    self.users = {}
    print('The chat server has been created.')

  #Function taken from server.py example
  #Creates socket and binds to port self.PORT
  #Returns the created socket
  def bind_port(self):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
    s.bind((self.HOST,self.PORT))
    s.listen(5)

    return s

  #Handles events. Specific events are detailed below
  def run(self):
    while True:
      rsock, wsock, esock = select.select(self.connections,[],[])

      #Each socket that has new data
      for sock in rsock:
        #if new connection, accept it and add to list of connections
        if (sock == self.sock):
          u = user(self.sock.accept())
          self.connections.append(u.getSock())
          readName = threading.Thread(target = self.recName,args=(u,))
          readName.start()
        
        #If input from stdin
        #A newline character exits the program
        #The 'users' string prints out the all of users in the chat room
        elif (sock == sys.stdin):
          d = sock.readline()
          if (d == '\n'):
            print('Exiting Program.')
            self.sock.close()
            return
          elif (d == 'users\n'):
            for i in self.users:
              self.users[i].write()

        #If incoming message, send message to all connections
        else:
          message = sock.recv(1024).decode()
          
          #if connection is closed
          if message == '':
            e = self.users[sock].getName() + " has left the chat room.\n" 
            self.sendtoall(e)
            print(e)
            self.connections.remove(sock)
            try:
              del self.users[sock] 
            except:
              pass
          #If incoming message is '/eof', echo it back to that socket
          #This causes the chatClient's listening thread to close
          elif (message == '/eof'):
            sock.sendall(message.encode())
          #If none of the above, echo message to all clients
          else:
            print('Received:', message,end='')
            self.sendtoall(message)

  #Receives a user name from a user
  #Arguments: a user object 
  #Returns: none
  #Result: Receives a user's name from a user. Sets the user's name to the 
  #username, and sends the user a welcome message.
  def recName(self, user):
    n = user.getSock().recv(1024).decode()
    if (n != ''):
      user.setName(n)
      self.users[user.getSock()] = user
      user.getSock().sendall(b'Welcome to the chat room.\n')
      str = "Current users in chat: "
      for i in self.users:
        str += self.users[i].getName() + ', '
      str = str[:-2]
      str += '\n'
      user.getSock().sendall(str.encode())
      print(user.getName(),'has joined the chat room.')

  #Sends a message to all users in the chat
  #Arguments: message - string message to be sent
  #Returns: none
  def sendtoall(self,message):
    for conn in self.connections:
      if (conn != self.sock and conn != sys.stdin):
        conn.sendall(message.encode())


#A user class that represents a single user
#class variables:
#self.sock: the user's socket
#self.address: the user's address tuple
#self.name: The user's username
class user():
  def __init__(self, param):
    self.sock = param[0]
    self.address = param[1]
    self.name = ''

  def getSock(self):
    return self.sock

  def getAddress(self):
    return self.address
  
  def sendMessage(self, message):
    self.sock.sendall(message)  

  def setName(self,name):
    self.name = name

  def getName(self):
    return self.name

  def write(self):
    print('(',self.address,',',self.name,')')


if __name__ == '__main__':
  server = chatServer()
  server.run()

