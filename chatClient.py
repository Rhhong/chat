import socket
import threading
import tkinter as tk      

#Application class that is inherited from the tk.Frame class
#Arguments: master (optional)
#Returns: none
#Result: Creates a loginFrame upon initialization
class Application(tk.Frame):              
  def __init__(self, master=None):
    self.sock = self.open_connection()
    tk.Frame.__init__(self, master)
    self.name = ''
    self.login = self.loginFrame()
    self.grid()                       
    self.master = master

  #Creates the main chat window
  def createWidgets(self):
    self.chatText = tk.Text(self,height=20,state='disabled')
    self.chatText.mark_set("position", '1.0')
    self.inputText = tk.Text(self,height=1)    
    self.inputText.bind('<KeyRelease-Return>',self.sendText)
    self.quitButton = tk.Button(self, text='Quit',command=self.exitProgram)
    self.quitButton.grid()            
    self.chatText.grid()
    self.inputText.grid()

    #Creates thread to listen for connections
    l = threading.Thread(target = self.listenMessage)
    l.start()

  #Receives text from the text box and sends it to the server
  def sendText(self, event):
    w = event.widget
    text = w.get('1.0','end')

    text = text[:-1] #strip newline from end
    self.inputText.delete('1.0 linestart','end')
    self.inputText.mark_set('insert','1.0')

    #Send text to server
    text = self.name + ': ' + text
    self.sock.sendall(text.encode())

  #Listens for messages from the server with socket.recv()
  #When a message is received, update the main text box with message
  #Exits when a '/eof' string is received from the server
  def listenMessage(self):
    while True:
      data = self.sock.recv(1024)
      if(data.decode() == '/eof'):
        self.sock.close()
        return
      self.chatText.config(state='normal')
      self.chatText.insert('position', data.decode())
      self.chatText.config(state='disabled')

  #Function taken from client.py example
  #Opens a TCP connection to the chat server ('rhhong',45000)
  def open_connection(self):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    connect_error = s.connect_ex((socket.gethostbyname(socket.gethostname()),46000))

    if connect_error:
      if connect_error == 111:
        print('Connection refused. Exiting Program')
      else:
        print('Error connecting to chat server. Exiting Program')
      exit(1)

    return s

  #Creates a login window that prompts the user for a username
  #Returns: This login window
  def loginFrame(self):
    top = tk.Frame()
    top.grid()
    l = tk.Label(top,text='Enter a username:')
    l.pack()
    t = tk.Text(top,height=1)
    t.bind('<KeyRelease-Return>',self.nameRead)
    t.pack()
    return top

  #An event that is called when a username is entered in the loginFrame window
  #When a username is entered, send the username to the server, destroy 
  #the loginFrame window, and create the main chat window
  def nameRead(self,event):
    w = event.widget
    text = w.get('1.0','end')
    text = text[:-2]
    self.sock.sendall(text.encode())
    self.name = text
    self.login.destroy()
    self.createWidgets()

  #Exits the program
  #Is called when the "Quit" button is pressed
  #Sends the server the "/eof" string which is then echoed back
  def exitProgram(self):
    self.sock.sendall(b'/eof')
    self.master.destroy()

root = tk.Tk()
app = Application(root)                       
app.master.title('Chat Application')    
app.mainloop()  


