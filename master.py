from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import sys

workers = {
    'worker-1': ServerProxy("http://localhost:23001/"),
    'worker-2': ServerProxy("http://localhost:23002/")
}

def query_worker(worker_key, func_name, *args):
    """
    helper function to  call an RPC function on a specific worker. If server goes down, system still stays alive
    args: worker_key (str)- 'worker-1' or 'worker-2',
        func_name (str): name of the RPC function to call,
        *args: arguments to pass to the RPC function
    returns: list- results from the worker, or empty list on failure
    """ 
    try:
        #retrieves the connection for the specified worker
        worker = workers[worker_key]       
        #dynamically call the correct function by name
        rpc_func = getattr(worker, func_name) 
        response = rpc_func(*args)
        #retrieves a value from a dictionary 
        return response.get('result', [])
    except Exception as e:
        #if worker's down/killed don't crash master
        print(f"Could not reach {worker_key}: {e}")
        return []
    
      
def getbylocation(location):
    """
    find all persons who lived in a location. This query goes to both workers
    args: location (str)- the location to search for
    returns dict:{'error': bool, 'result': combined list from both workers}
    """
    print(f"Master routing getbylocation('{location}') to both workers")
    result_w1 = query_worker('worker-1', 'getbylocation', location)
    result_w2 = query_worker('worker-2', 'getbylocation', location)
    # Combine results from both workers into a single list
    combined = result_w1 + result_w2
    return {
        'error': False,
        'result': combined
    }


def getbyname(name):
    """
    look up a person by name. The query goes to the relevant worker based on the first letter:
    args: name (str)- the person's name to search for
    returns: dict: {'error': bool, 'result': list of matching records}
    """
    name = name.lower().strip()   
    if not name:
        return {'error': True, 'result': []}
    
    first_letter = name[0]
    #decide which worker handles this name 
    if 'a' <= first_letter <= 'm':
        print(f"Master routing getbyname('{name}') to Worker-1")
        result = query_worker('worker-1', 'getbyname', name)
    else:
        print(f"Master routing getbyname('{name}') to Worker-2")
        result = query_worker('worker-2', 'getbyname', name)
    return {
        'error': False,
        'result': result
    }

def getbyyear(location, year):
    """
    rind all persons who lived in avlocation during a year. this goes to both workers 
    args: location (str)- the residence location
        year (int)- the year of residence
    returns: dict: {'error': bool, 'result': combined list from both workers}
    """
    print(f"Master routing getbyyear('{location}', {year}) to both workers")
    result_w1 = query_worker('worker-1', 'getbyyear', location, year)
    result_w2 = query_worker('worker-2', 'getbyyear', location, year)
    combined = result_w1 + result_w2
    return {
        'error': False,
        'result': combined
    }
 
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 master.py <port>")
        sys.exit(1)

    port = int(sys.argv[1])
    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Listening on port {port}..")
    #register functions
    server.register_function(getbyname, 'getbyname')
    server.register_function(getbylocation, 'getbylocation')
    server.register_function(getbyyear, 'getbyyear')
    server.serve_forever()

if __name__ == '__main__':
    main()