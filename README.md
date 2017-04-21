#Introduction 
The main source code for the first-year university PROM module. This project is the 'lock' system, where we have to use a Raspberry Pi and external hardware to create a system which can receive keypad inputs, check them against a code, and then output a signal to LEDs and buzzers informing the user on if their guess was correct.

#Build and Test
After creating the full software diagram, we will be implementing the system in 2 main area, interface and internals. The interface deals with the GPIO ports, and the internals handle the received data and the required state of the hardware outputs.

For testing, Python unit testing would be most useful, since they can be run against the code we write and instantly tell us whether it is working correctly.