from xmlrpc.server import SimpleXMLRPCServer
import sys
import json

# Storage of data
data_table = {}

#load data based on which portion it handles (am or nz)
def load_data(group):
    global data_table
    filename = f"data-{group}.json" 

    try:
        with open(filename, "r") as file:
            #read json content and convert to python dictionary
            data_table = json.load(file) 
        
        #check if file's empty
        if not data_table:
            print(f"Error! '{filename}' is empty")
            sys.exit(1)
        #print number of loaded data
        print(f"{len(data_table)} records loaded from {filename}")

    except FileNotFoundError:
        print(f"Error!'{filename}' not found.")
        sys.exit(1) 

def getbyname(name):
    """ 
     search by name and returns matching record if found otherwise return list
     args: name (str)- the name to search for
     returns: dict: {'error': bool, 'result': list of matching records} 
     """
    try:
        name = name.lower().strip() 
        # check if name's empty
        if not name:
            return {'error': True, 'result': []}
        # Check if the name is a key in the dictionary 
        if name in data_table:
            return {
                'error': False,
                'result': [data_table[name]] 
            }
        else:
            # name doesn't exist in this worker's portion and returns empty list
            return {
                'error': False,
                'result': [] 
            }
        
    except Exception as e:
        print(f"Error in getbyname: {e}")
        return {'error': True, 'result': []}
     
def getbylocation(location):
    ''' finds and returns person info who lived in the specific location
       args: location (str)- the location to search for
       return: dict: {'error': bool, 'result': list of matching records} ''' 
    try:
        # check if location's empty
        if not location or not location.strip():
            return {'error': True, 'result': []}
         #store matching records
        matches = []
        #iterate through the values of the dictionary 
        for record in data_table.values():
            #add the matching record 
            if record['location'].lower() == location.lower():
                matches.append(record) 
        return {
            'error': False,
            'result': matches
        }
    
    except Exception as e:
        print(f"Error in getbylocation: {e}")
        return {'error': True, 'result': []}
    
def getbyyear(location, year):
    ''' finds and returns person information who lived in a specific location at a specific year
        args: location (str)- the residence location to search for
        year (int)- the year of residence
        return:  dict: {'error': bool, 'result': list of matching records}
    '''
    try:
        # check if the location's empty
        if not location or not location.strip():
            return {'error': True, 'result': []}
        year = int(year) 
        matches = [] 
        # Loop through the person's records in the dictionary
        for record in data_table.values():
            # check if both location and year match
            if (record['location'].lower() == location.lower() and record['year'] == year):
                matches.append(record)
        return {
            'error': False,
            'result': matches
        }
    
    except ValueError:
        print(f"Error in getbyyear: Invalid year '{year}'")
        return {'error': True, 'result': []}
    except Exception as e:
        print(f"Error in getbyyear: {e}")
        return {'error': True, 'result': []}

def main():
    if len(sys.argv) < 3: 
        print('Usage: Assignment-Worker.py <port> <group: am or nz>')
        sys.exit(0) 

    try:
        port = int(sys.argv[1])
    except ValueError:
        print("Error! Invalid port number")
        sys.exit(1)

    group = sys.argv[2].lower() 
    if group not in ('am', 'nz'):
        print("Error! group must be 'am' or 'nz'")
        sys.exit(1) 

    # Load the appropriate JSON data file 
    load_data(group)

    # Create the RPC server
    server = SimpleXMLRPCServer(("localhost", port))
    print(f"Worker ({group}) listening on port {port}...")

    # Register functions so the Master can call them remotely
    server.register_function(getbyname, 'getbyname')      
    server.register_function(getbylocation, 'getbylocation') 
    server.register_function(getbyyear, 'getbyyear')       
    server.serve_forever()

if __name__ == '__main__':
    main()