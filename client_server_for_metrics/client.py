import socket
import time

class ClientError(Exception):
    pass

class ClientSocketError(ClientError):
    pass

class ClientProtocolError(ClientError):
    pass
 
class Client:
    def __init__(self, host, port, timeout = None):
        self.host = host
        self.port = port
        try:
            self.connection = socket.create_connection((host, port), timeout)
        except socket.error as err:
            raise ClientSocketError("error create connection", err)

    def _read(self):
        """Reads the response from the server"""      
        date_from_server = b""
        while not date_from_server.endswith(b"\n\n"):
            try:
                date_from_server = date_from_server + self.connection.recv(1024)
            except socket.error as err:
                raise ClientSocketError("error send data", err)   
        date_from_server = date_from_server.strip()
        date_from_server = date_from_server.decode().split("\n")

        if(not date_from_server):
            raise ClientError()
        elif(date_from_server[0] != "ok"):
            raise ClientError()
        return date_from_server

    def put(self, title, value, timestamp = None):
        """The method sends a command "put" and calls the method _read()"""
        timestamp = timestamp or int(time.time())
        try:
            self.connection.send("put {} {} {}\n".format(title, value, timestamp).encode())
        except socket.error as err:
                raise ClientSocketError("error recv data", err)
        self._read()
    
    def get(self, title):
        """The method sends a command "get" and calls the method _read() and converts the response"""
        try:
            self.connection.sendall(f"get {title}\n".encode())
        except socket.error as err:
            raise ClientSocketError("error send data", err)

        date_from_server = self._read()
        result = dict()
        for i in date_from_server[1:]:
            date = i.split()
            if(len(date) == 1):
                raise ClientError()

            if(date[0] not in result):
                result[date[0]] = list()

            result[date[0]].append((int(date[2]),float(date[1])))
        for i in result:
            result[i].sort(key = lambda x: (x[0]))
        return result

    def close_connection(self):
        self.connection.close()  

     
if __name__ == "__main__":
    client = Client("127.0.0.1", 8888)
    client.put("Example_1","255", "121313213")
    client.put("Example_2","41")
    client.put("Example_2", "45", "121212")
    print(client.get("*"))

    client.close_connection()     