

def log(message):
    print(message)
    
    with open("log.txt", "a") as log_file:
        print(message, file=log_file)