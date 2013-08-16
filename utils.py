
def extract_host(machine):
    start = machine.find('@') + 1
    return machine[start:]