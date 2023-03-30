import socket

CACHE = {}  # dictionary to cache web pages
MAX_CACHE_SIZE = 10  # maximum number of pages to cache


# parse the request to determine where to redirect it
# local requests will be sent to localhost on port 6789
# external website requests will be sent to the specified
# web address on port 80

def handle_request(request):

    request_core = request.split(' ')[1] # /localhost:6789/helloworld.html

    # remove https:// to make it easier to parse and because socket.connect doesn't accept that in the address
    if 'https://' in request_core:
        request_core = request_core.replace('https://', '')
    elif 'http://' in request_core:
        request_core = request_core.replace('http://', '')

    destination = request_core.split('/')[1] # localhost:6789

    path = request_core.split(destination).pop() # /helloworld.html
    if len(path) == 0:
        path = '/'

    # new address
    new_address = destination.split(':')[0] # localhost
    # print("new address: " + str(new_address))

    # new port
    new_port = 80
    if '6789' in destination:
        new_port = 6789
    # print("new port: " + str(new_port))
   
    # new request
    new_request = bytes("GET " + str(path) + " HTTP/1.1\r\nHost: " + str(destination) + "\r\nConnection: close\r\n\r\n", 'utf-8')
    # print("new request: " + str(new_request))
    
    # redirect request to its destination
    new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    new_socket.connect((new_address, new_port))
    new_socket.sendall(new_request)
    response = b''
    while True:
        data = new_socket.recv(1024)
        if not data:
            break
        response += data
    return response


# if the requested path was cached then simply send the response from cache
# otherwise make the request, cache the response, and then send the response

def handle_client(client_socket, address):

    request = client_socket.recv(1024).decode()

    file_path = request.split(' ')[1]
    response = b''
    if file_path in CACHE:
        print("Found path in cache.")
        response = CACHE[file_path]
    else:
        print("Path not found in cache. Accessing server.")
        response = handle_request(request)
        if len(CACHE) >= MAX_CACHE_SIZE:
            CACHE.popitem()
        CACHE[file_path] = response

    print("Returning response...")
    client_socket.sendall(response)
    print("Done.")

    client_socket.close()


HOST = ''
PORT = 8888

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print("Server is listening...")

    while True:
        client_socket, address = server_socket.accept()
        handle_client(client_socket, address)
        print("Server is listening...")
