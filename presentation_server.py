#!/usr/bin/env python

import sys
import os
import time

import socket
from thread import *

import logo
from ui import screenwrite
sw = screenwrite(ymin=13, ymax=23)

try:
    from msvcrt import getch  # try to import Windows version
except ImportError:
    def getch():   # define non-Windows version
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

bShouldExit = False
slideNumber = 0
numberConnections = 0


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False

def initui():
    os.system('clear')

    sw.printStatic(logo.title, 0, 0, 5)

    sw.printStatic('-' * 82, 0, 12)

    for i in range(13,24):
        sw.printStatic('|', 41, i)
        sw.printStatic('|', 82, i)


    sw.printStatic("q : Exit ", 0, 11)

    #test layour
    sw.printStatic("current slide : ", 42, 13)
    sw.printStatic("set slide to : ", 42, 14)

    sw.printStatic("Active Connections : ", 42, 16, 1)



# initialize socket
def init_server():
    HOST = ''   # Symbolic name meaning all available interfaces
    PORT = 50007 # Arbitrary non-privileged port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sw.printnl('Socket created')

    #Bind socket to local host and port
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    sw.printnl('Socket bind complete',3)

    return s


#start server
def startserver():

    # build server  ui
    initui()


    sw.printnl('initializing server')
    s = init_server()


    #Start listening on socket
    s.listen(10)
    sw.printnl('Socket now listening', 2)


    # Start window
    #sw.printStatic("STARTING", 51, 13, 1)
    #sw.printStatic("ACTIVE  ", 51, 13, 3)



    #now keep talking with the client
    '''
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        sw.printnl('Connected with ' + addr[0] + ':' + str(addr[1]))

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        start_new_thread(clientthread ,(conn,rw,rg))
    '''

    #listen for key input
    start_new_thread(keylistener, (s,))

    start_new_thread(listen, (s, ))

    # now saty awake until user quits
    while(not bShouldExit):
        time.sleep(5)
        sw.printStatic(numberConnections, 63, 16, 1)

    sw.printnl('shutdown complete', 5)

def listen(s):

    while 1:
        #wait to accept a connection - blocking call
        try:
            conn, addr = s.accept()
        except socket.error as msg:
            break

        sw.printnl('Connected with ' + addr[0] + ':' + str(addr[1]))

        #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.


        start_new_thread(clientthread ,(conn,rw,rg))

    #s.close()

def keylistener(s):

    global bShouldExit
    global slideNumber

    inputNumber = ''
    while 1:
        keyinput = getch()
        if keyinput == 'q':
            #s.shutdown(socket.SHUT_RDWR)
            s.close()
            sw.printnl('server closing connection', 4)
            bShouldExit = True
            break
        elif keyinput == '\r':
            if inputNumber != '':
                slideNumber = inputNumber
                sw.printStatic(slideNumber+'     ', 58, 13, 3)
                inputNumber = ''
                sw.printStatic('        ', 57, 14, 4)
        elif keyinput == '\x08':  # handle backspace
            inputNumber = inputNumber[:-1]
            sw.printStatic(inputNumber+'     ', 57, 14, 4)
        else:
            if is_number(keyinput):
                inputNumber += keyinput
                sw.printStatic(inputNumber, 57, 14, 4)



#Function for handling connections. This will be used to create threads
def clientthread(conn,rw,rg):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)
        if not data:
            break
        if data == 'q':
            break
        if int(data) < 157:

            conn.sendall('betting on : %s'%data)

            conn.sendall('result is : %s')



    #came out of loop
    conn.close()
    sw.printnl('connection closed')

def clientthreadb(conn):
    #Sending message to connected client
    conn.send('Welcome to the server. Type something and hit enter\n') #send only takes string

    #infinite loop so that function do not terminate and thread do not end.
    while True:

        #Receiving from client
        data = conn.recv(1024)
        if not data:
            break

        clickpos = map(int, data.split(','))

        conn.sendall('result is : %s'%str(clickpos))
        sw.printStatic(" "*10, 51, 14, 3)
        sw.printStatic(str(clickpos), 51, 14, 3)



    #came out of loop
    conn.close()
    sw.printnl('connection closed')





if __name__=='__main__':

    #test_roulette()
    startserver()

    sw.printStatic('press Enter to Continue...', 0, 11, 5)
    raw_input("")
    os.system('clear')
    os.system('cls')
