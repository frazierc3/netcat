import sys # command line arguments
import argparse # command line argument parser
import socket # sockets
import subprocess # subprocesses
import re # regular expressions
import os # os commands

# --- START CONNER ---

def CreateParserArgs():
    print("ARGS:", str(sys.argv)) # shows argv list upon start of program
    parser = argparse.ArgumentParser(prog="netcat.py", description="* Remote connect to server by IP address OR specify -l to run in server mode, then add PORT *")
    parser.add_argument("host", default=None, nargs="?", help="ip address of server you are attempting to connect to")
    parser.add_argument("port", default=None, nargs="?", help="port to use for remote connection")
    parser.add_argument("-l", "--listen", default=False, action="store_true", help="the program is set to listen (server) mode instead of client mode (default)")
    parser.add_argument(">", default=None, nargs="?", help="signifies that you are uploading X file FROM your computer to the server. ex: 192.0.0.5 > C:/vms/example.txt")
    parser.add_argument("<", default=None, nargs="?", help="signifies that you are downloading X file TO your computer from the client. ex: localhost < example.txt")
    parser.add_argument("path", default=None, nargs="?", help="used in file transfer: if listen mode, specify name of file to write to; if client mode, specify filepath")
    args = vars(parser.parse_args()) # parse args in sys.argv list, cast to dict with vars
    return args

def CheckArgs(args):
    try:
        if len(sys.argv) == 1: # running program without any args or values
            print("No arguments found. Try adding -h for help.")
            sys.exit()
        elif len(sys.argv) > 1: # 1 or more args
            global mode
            '''
            opts = []
            posi = []
            
            for it in sys.argv[1:]: # get optional arguments into opts list
                if "-" or "<" or ">" in it:
                    opts.append(it)
            
            for it in sys.argv[1:]: # get positional arguments into posi list
                if not "-" and not "<" and not ">" in it:
                    posi.append(it)
            
            index_gt = sys.argv().index(">")
            index_lt = sys.argv().index("<")
            
            print(index_gt)
            print(index_lt)
            '''
            
            if args["listen"] == True: # if -l or --listen entered
                mode = "SERVER" # server mode
                args["host"] = "127.0.0.1" # loopback
                
                if sys.argv[1] == "-l" or sys.argv[1] == "--listen": # if -l before port
                    args["port"] = sys.argv[2]
                #else: # port before -l
                    #args["port"] = sys.argv[1]
                
                if args["port"] == None: # no port entered for listen mode
                    print("Please specify port after typing -l.")
                    sys.exit()
                
            elif args["host"] != None and args["port"] == None: # no port entered for client mode
                print("Insufficient arguments for client mode. See usage with -h.")
                sys.exit()
            else: # data is there, but not validated
                if sys.argv[1] == "localhost": # localhost workaround
                    args["host"] = "127.0.0.1"
                else:
                    args["host"] = sys.argv[1]
                
                args["port"] = sys.argv[2]
            
            '''
            if args[">"] == True or args["<"] == True: # if < or > entered
                if args["path"] == None: # no path entered
                    print("Please specify full filepath/name after inputting < or >.")
                    sys.exit()
                else: # path entered, but not validated
                    pass
            '''
            
            return args
            
    except SystemExit: # trying to exit from program
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])

def ValidateArgs(a):
    try:
        if a["host"] is not None:
            match = re.search("^\d{1,3}[.]\d{1,3}[.]\d{1,3}[.]\d{1,3}$", a["host"]) # ip address regex
        
        if not match: # if hostname is not ip addr
            print("Not in correct ip address format: [0-999.0-999.0-999.0-999]")
            sys.exit()
        elif a["port"].isdigit() == False: # if port is not digit
            print("Port must be a positive integer.")
            sys.exit()
        
    except SystemExit: # trying to exit from program
        raise
    except:
        print("Unexpected error:", sys.exc_info()[0])

def ConnectionSwitch(a): # decide if cmd shell is client or server
    global mode
    
    if mode == "SERVER":
        serverSocket(a)
    else: # client mode
        clientSocket(a)

# --- END CONNER ---
# --- START CAROLINE ---

def serverSocket(args): # host computer
    try:
        #create socket object
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #get local host name
        hostname = socket.gethostname()
        host = "127.0.0.1"
        
        port = int(args["port"]) #CONNER
        
        #bind port to host
        serversocket.bind((host, port))
        
        #queue up to 5 requests
        serversocket.listen(5)
        
        print("\nListening on", hostname, "on ip", host, "on port", port, "...")
        
        #stays here until connection received
        conn, addr = serversocket.accept()
        print("Connected by", addr, "\n")
        
        #connection received
        while True:
            rcvdData = conn.recv(1024).decode() #get data from client and decode
            response = "Not recognized as a command or executable file." # default response
            print("client:", rcvdData)
            
            if rcvdData == "": # CRLF received from client
                print("\nConnection closed by client.")
                break
            
            result = rcvdData.find(".exe") #MYKEL #looks for '.exe' in command
            
            if result != -1:            #MYKEL
                subprocessing(rcvdData) #MYKEL #calls subprocessing
                response = "Attempting to open program " + rcvdData
            
            if rcvdData.startswith('os.'): #MYKEL #look for commands beginning with 'os.'
                opsys(rcvdData)            #MYKEL #calls opsys
                response = "Attempting operating system command..."
            
            conn.send(response.encode()) #send and encode data
        
        conn.close() #close connection
        serversocket.close() #close socket
        
    except ConnectionError:
        print("Connection error.")
    except:
        print("Unexpected error:", sys.exc_info()[0])

def clientSocket(args): # client computer
    try:
        #create socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #get local host
        host = args["host"]
        
        port = int(args["port"]) #CONNER
        
        #connect host to port
        s.connect((host, port))
        print("\nWelcome to the server. Type in an executable to open, OR type os.[windows/linux command] to execute a command on the server.\n")
        
        #connection received
        while True:
            sendData = input("you: ")
            s.send(sendData.encode()) #send and encode data
            
            if sendData == "": # if CRLF, leave
                print("\nExiting...")
                break
            
            rcvdData = s.recv(1024).decode() #get data from server and decode
            print("server:", rcvdData)
        
        s.close() #close socket
        
    except ConnectionRefusedError:
        print("Connection refused by peer. No server with given address and port may exist.")
    except BrokenPipeError:
        print("Cannot read or write from closed or shutdown socket.")
    except ConnectionError:
        print("Connection error.")
    except:
        print("Unexpected error:", sys.exc_info()[0])

# --- END CAROLINE ---
# --- START MYKEL ---

def subprocessing(data):
    if os.path.isfile('C:\\Windows\System32\\' + data) is True: #checks to see if ___.exe exists
        subprocess.check_output(data) #runs ___.exe
    else:
        print('Cannot find ' + data)

def opsys(data):
    command = data.split('.', 1) # splits 'os.' from command
    os.system(command[1])

# --- END MYKEL ---

def FileStream():
    try:
        # UNFINISHED
        #stream = open(filename, mode="w+", encoding = None)
        
        #stream.close()
        pass
    except:
        print("Unexpected error:", sys.exc_info()[0])

def Main():
    args = CreateParserArgs()
    CheckArgs(args)
    ValidateArgs(args)
    ConnectionSwitch(args)

# MAIN
mode = "CLIENT" # global
Main()