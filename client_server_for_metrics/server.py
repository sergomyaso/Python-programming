import asyncio

class Storage:
    """Data storage class"""
    def __init__(self):
        self.data = dict()

    def put(self, key, value, timestamp):
        if(key not in self.data):
            self.data[key] = dict()
        self.data[key][timestamp] = value
        
    def get(self, key):
        data = self.data
        if(key != "*"):
            data ={key:self.data.get(key, {})}
        result = dict()
        for key, timestamp in data.items():
            result[key] = sorted(timestamp.items())
        return result

class CoderError(ValueError):
    pass

class Coder:
    """The class converts data when sending/receiving"""
    def decode(self, data):
        list_of_params = list()
        data = data.split("\n")
        for part in data:
            if(not part):
                continue
            try:
                command, arguments = part.split(" ", 1)             
                arguments = arguments.split()
                if("" in arguments):
                    raise CoderError("wrong command")
            except ValueError:
                raise CoderError("wrong command")
            try:
                if(command == "put" and len(arguments) == 3):
                    key, value, timestamp = arguments
                    list_of_params.append((command, key, float(value), int(timestamp)))
                elif(command == "get" and len(arguments) == 1):
                    list_of_params.append((command, arguments[0]))
                else:
                    raise CoderError("unknown method")
            except ValueError:
                raise CoderError("wrong command")
        return list_of_params

    def encode(self, data):
        answer = "ok\n"
        if(len(data) == 1 and data[0] == None):
           return answer + "\n"

        if(len(data) == 0):
            return "error\nwrong command\n\n"

        for i in range(len(data)):
            for key in data[i]:
                for timestamp_value in data[i][key]:
                    answer += "{} {} {}\n".format(key, timestamp_value[1], timestamp_value[0])
        return answer + "\n"
   
class CommandWorkerError(Exception):
    pass

class CommandWorker:
    """Server command execution class"""
    def __init__(self, storage):
        self.storage = storage
    
    def run(self, command, *params):
        print(command)
        if(command == "put"):
            return self.storage.put(*params)
        if(command == "get"):
            return self.storage.get(*params)
        else:
            raise CommandWorkerError("Unsupported method")

class ServerClientProtocol(asyncio.Protocol):
    """Implementing the server using ayncio"""
    storage = Storage()

    def __init__(self):
        super().__init__()

        self.worker = CommandWorker(self.storage)
        self.coder = Coder()
        self.buffer = b''

    def process_data(self, data):
        """Method of command processing"""
        list_of_commands = self.coder.decode(data)
        to_answer = list()
        print(list_of_commands)
        for i in list_of_commands:
            to_answer.append(self.worker.run(*i))
        return self.coder.encode(to_answer)

    def connection_made(self, transport):
        self.transort = transport

    def data_received(self, data):
        """The method is called when getting data"""
        self.buffer += data
        try:
            decode_data = self.buffer.decode()
        except UnicodeDecodeError:
            return
        if(not decode_data.endswith("\n")):
            return
        self.buffer = b''
        try:
            answer = self.process_data(decode_data)
        except(CommandWorkerError, CoderError, ValueError, UnicodeDecodeError) as error:
            self.transort.write(f"error\n{error}\n\n".encode())
            return
        self.transort.write(answer.encode())

def run_server(host, port):
    """The method is called to start the server"""
    loop = asyncio.get_event_loop()
    coro = loop.create_server(
        ServerClientProtocol,
        host, port
    )
    server = loop.run_until_complete(coro)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
                  
if __name__ == "__main__":
    run_server("127.0.0.1", 8888)
