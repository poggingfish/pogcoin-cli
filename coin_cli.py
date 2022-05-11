endpoint = "https://coin.pogging.fish" 
import requests
import time
import json
import datetime
import threading
global bals
txs_waiting = 0
bals = {}
def pog_logger(text, type):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} {type}: {text}\n")
def sync_bals():
    global endpoint
    global bals
    bals = json.loads(requests.get(endpoint + "/get-all-bals").text)
    pog_logger("Synced Balances.", "INFO")
def create_tx(addr1, addr2, amount, password):
    global txs_waiting
    global endpoint    
    request = requests.post(endpoint + "/tx", f"{addr1} {addr2} {amount} {password}")
    if request.text == "_CLIENT_TRYAGAIN":
        time.sleep(0.1)
        create_tx(addr1, addr2, amount, password)
        return 0
    pog_logger("Successfully created transaction", "INFO")
    txs_waiting -= 1
def create_wallet():
    global endpoint
    print("Creating wallet...")
    request = requests.get(endpoint + "/create-wallet")
    return request.text.split(" ")[0], request.text.split(" ")[1]
def get_balance(addr):
    sync_bals()
    global endpoint
    global bals
    return bals[addr]
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
    try:
        reset, run = arg_parser()
        if reset:
            print("Creating new wallets")
            name, password = create_wallet()
            with open("wallet.txt", "w") as f:
                f.write(f"{name}\n{password}")
            print("Created wallet.")
            print("!! DO NOT SHARE YOUR WALLET WITH ANYONE !!")
            print("Your wallet is saved in wallet.txt")
            pog_logger("New wallet created.", "INFO")
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
                        print("Sent! Transaction will be broadcasted shortly.")
                        txs_waiting += 1
                        pog_logger("Started transaction process.", "INFO")
                        threading.Thread(target=create_tx, args=(name, command[1], command[2], password)).start()
                    if usr_input == "n":
                        print("Cancelled.")
                elif base == "exit":
                    break
                elif base == "addr":
                    print(f"Your address is {name}")
                    print("Share this with others to receive PogCoin!")
                elif base == "balance":
                    print(f"Your balance is {get_balance(name)} PogCoin")
    except KeyboardInterrupt:
        print("Safley exiting...")
        if txs_waiting > 0:
            print("Waiting for transactions to finish...")
            print("Please wait...")
            while txs_waiting > 0:
                time.sleep(0.1)
        exit()
print("Exiting...")