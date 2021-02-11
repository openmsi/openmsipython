#imports
import sys

#helper function to listen for and add user input to a queue
def add_input(input_queue) :
    #constantly listen for user input
    while True :
        input_queue.put(sys.stdin.read(1))
