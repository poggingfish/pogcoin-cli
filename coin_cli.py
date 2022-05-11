endpoint = "http://localhost:8080" 
import requests
def create_tx(addr1, addr2, amount, password):    
    request = requests.post(endpoint + "/tx", f"{addr1} {addr2} {amount} {password}")
    print(request.text)
def create_wallet():
    print("Creating wallet...")
    request = requests.post(endpoint + "/create-wallet")
    return request.text.split(" ")[0], request.text.split(" ")[1]
 
def arg_parser():
    import sys
    if len(sys.argv) == 1:
        print("Usage")
        print("reset - Reset data")
        print("run - Run the cli")
    
    reset = False
    run = False
    for x in sys.argv[1:]:
        if x == "reset":
            reset = True
        elif x == "run":
            run = True
    return reset, run
 
if __name__ == "__main__":
    reset, run = arg_parser()
    if reset:
        print("Creating new wallets")
        name, password = create_wallet()
        with open("wallet.txt", "w") as f:
            f.write(f"{name}\n{password}")
        print("Created wallet.")
        print("!! DO NOT SHARE YOUR WALLET WITH ANYONE !!")
        print("Your wallet is saved in wallet.txt")
    if run:
        with open("wallet.txt", "r") as f:
            name, password = f.read().split("\n")
        print("Welcome to the PogCoin CLI!")
        print("ADDR: " + name)
        while True:
            command = input("$ ~ ")
            command = command.split(" ")
            base = command[0]
            if base == "send":
                create_tx(name, command[1], float(command[2]), password)
            elif base == "exit":
                break
            elif base == "addr":
                print(f"Your address is {name}")
                print("Share this with others to receive PogCoin!")
print("Exiting...")