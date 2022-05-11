endpoint = "https://coin.pogging.fish" 
import requests
import time
def create_tx(addr1, addr2, amount, password):
    global endpoint    
    request = requests.post(endpoint + "/tx", f"{addr1} {addr2} {amount} {password}")
    if request.text == "_CLIENT_TRYAGAIN":
        time.sleep(0.659)
        create_tx(addr1, addr2, amount, password)
        return 0
    print(request.text)
def create_wallet():
    global endpoint
    print("Creating wallet...")
    request = requests.get(endpoint + "/create-wallet")
    return request.text.split(" ")[0], request.text.split(" ")[1]
def get_balance(addr):
    global endpoint
    text = "NO_ARGS_PASSED"
    while text == "NO_ARGS_PASSED":
        request = requests.post(endpoint + "/get-balance", f"{addr}")   
        text = request.text
        time.sleep(0.659)
    balance = request.text
    return balance
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
                if float(command[2]) < 3:
                    print("Sorry. Minimum amount is 3 PogCoin.")
                    continue
                usr_input = input("Are you sure you want to send "+ command[2] + " pogcoin to " + command[1] + "? (y/n) ")
                if usr_input == "y":
                    print("Creating transaction...")
                    create_tx(name, command[1], float(command[2]), password)
                if usr_input == "n":
                    print("Cancelled.")
            elif base == "exit":
                break
            elif base == "addr":
                print(f"Your address is {name}")
                print("Share this with others to receive PogCoin!")
            elif base == "balance":
                print(f"Your balance is {get_balance(name)} PogCoin")
print("Exiting...")