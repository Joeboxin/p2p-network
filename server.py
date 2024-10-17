import socket
import threading
import sys

HOST = '127.0.0.1'
PORT = 65432

class Server:
    """
    Sets up the socket, binding it and listening
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []
    filesInServer = []
    peerInfo = {}
    data = None
    def __init__(self):
        self.sock.bind((HOST, PORT))
        self.sock.listen(1)

    """
    While a process of handler is true it will receive data and send or process information based on the request
    """
    def handler(self, c, a):
        try:
            while True:
                data = c.recv(1024)

                # Ensure command begins with number
                commandType = -1
                if data.decode()[0].isdigit():
                    commandType = int(data.decode()[0])

                match commandType:
                    case 0:
                        #Splits file and registers in the server
                        splitFile = data.decode().split("|", 4)
                        fileName = splitFile[1]
                        host = splitFile[2]
                        port = splitFile[3]
                        print(f"File {fileName} registered!")
                        c.send(bytes(f"File {fileName} registered!".encode()))
                        self.filesInServer.append([fileName, len(splitFile[4]), splitFile[4]])

                        # Chunk and distribute
                        self.distribute_chunks(fileName)
                        c.send(f"Chunks of {fileName} distributed to peers!".encode())

                    case 1:
                        output = f"Number of files in list: {len(self.filesInServer)} \n"
                        for file in self.filesInServer:
                            output += f"Name: {str(file[0])} Length: {str(file[1])} \n"
                        c.send(f"1{output}".encode())

                    # TODO: Sending File Locations of peers
                    case 2:
                        pass
                    # TODO: Receive information about a peer downloading a chunk successfully, this allows the peer to become a source for the chunk
                    case 3: 
                        pass
                    # TODO: Ask peer to return the file chunk in the format file name, chunk id
                    case 4:
                        pass
                    # Not a valid command
                    case -1:
                        pass
                if not data:
                    
                    break
        except ConnectionResetError:
            pass
        finally:
            print(str(a[0]) + ":" + str(a[1]), "disconnected")
            self.connections.remove(c)
            c.close()
    """
    Accepts a connection where c is the socket and a is the address
    Creates a thread that calls its own process of handler, passing in the socket and address as arguments
    Adds the socket to the server's list of connections
    """
    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0]) + ":" + str(a[1]), "connected")


    """
    Gets a list/array of all chunks, number of chunks, and the number of peers/connections

    Checks if there are any peers connected, then sends a download command, file name, chunk id, and the chunk's data
    """
    def distribute_chunks(self, fileToDivide):
        # Chunk the file into 1024-byte pieces
        chunkList = self.chunkFile(fileToDivide)
        numChunks = len(chunkList)
        numPeers = len(self.connections)

        if numPeers == 0:
            print("No peers to distribute the file.")
            return

        # Round-robin distribution of chunks
        for i, chunk in enumerate(chunkList):
            peer = self.connections[i % numPeers] 
            chunk_id = i  
            message = f"5|{fileToDivide}|{chunk_id}|".encode() + chunk
            print(message)
            peer.send(message)  # Send chunk with its ID

        print(f"Distributed {numChunks} chunks of {fileToDivide} to {numPeers} peers.")


    """
    Creates an array then reads the file bytes, and each chunk reads specifically 1024 bytes
    Chunk count is iterated and chunks are added to chunkList until there is nothing being read
    """
    def chunkFile(self, fileToDivide):
        chunkList = []
        with open(fileToDivide, "rb") as f:
            chunk = f.read(950) #leave space for header bits
            chunkCount = 1

            while chunk:
                chunkList.append(chunk)
                chunkCount += 1
                chunk = f.read(950)

        return chunkList

if __name__ == "__main__":
    server = Server()
    print("Starting server...")
    server.run()