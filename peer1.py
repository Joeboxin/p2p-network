import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fileChunks = {}

    # TODO: make sure to make a file object with file name and length for the last parameter
    # TODO: Add host and port functionality
    def requestRegister(self, host, port, numFiles, fileName):
        data = open(fileName, "r")
        read = data.read()
        encodedData = f"0|{fileName}|{host}|{port}|" + read
        self.sock.send(bytes(encodedData, 'utf-8'))

    def RequestFileList(self):
        self.sock.send(bytes("1", 'utf-8'))

    def sendMsg(self):
        while True:
            command = input("Send Command:\n1) Register\n2) File List\n3) File Location\n4) Chunk Register\n5) File Chunk\n")
            match command:
                case "Register":
                    inputParams = input("Enter IP Address, Port, Number of Files, FileName: ").split()
                    self.requestRegister(inputParams[0], inputParams[1], inputParams[2], inputParams[3])
                case "File List":
                    self.RequestFileList()
                case "File Location":
                    pass
                case "Chunk Register":
                    pass
                case "File Chunk":
                    pass 
            

    def __init__(self):
        self.sock.connect((HOST, PORT))

        #Creates and starts thread
        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()

        while True:
            #Receives data checks if there is a command is passed and matches the received command
            
            data = self.sock.recv(1024)


            commandType = -1
            if data.decode()[0].isdigit():
                commandType = int(data.decode()[0])
            
            print(data.decode())
            match commandType:
                case 0:
                    splitFile = data.decode().split("|", 4)
                    if len(splitFile) < 5:
                        print("RECEIVED INCOMPLETE DATA:", splitFile)
                        continue
                    fileName = splitFile[1]
                    self.fileChunks.setdefault(fileName, [])
                    self.fileChunks[fileName] = list.append(splitFile[4])

                case 1:
                    # output = f"Number of files in list: {len(self.filesInServer)} \n"
                    # for file in self.filesInServer:
                    #     output += f"Name: {str(file[0])} Length: {str(file[1])} \n"
                    # c.send(output.encode())
                    print(data.decode()[1:])

                case 2:

                    pass
                case 3:
                    pass
                case 4:
                    pass
                case 5:
                    # Add chunks to chunk dict
                    splitData = data.decode().split("|", 3)
                    fileName = splitData[1]
                    chunk_id = int(splitData[2])
                    file_data = splitData[3]

                    self.fileChunks.setdefault(fileName, {})
                    self.fileChunks[chunk_id] = file_data
                    print(f"Received chunk {chunk_id} for file: {fileName}")

                    # Reconstruct file if all chunks are received
                    # if len(self.fileChunks[fileName]) == expected_chunk_count:  # Check if we have all chunks
                    #     self.reconstruct_file(fileName)
                
                # not valid data to parse
                case -1:
                    pass

            if not data:
                
                break
if __name__ == "__main__":
    client = Client()