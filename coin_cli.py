endpoint = "https://coin.pogging.fish" 
import requests
import time
import json
import datetime
import threading
global bals
exclude_from_baltop = []
txs_waiting = 0
bals = {}
def pog_logger(text, type):
    with open("log.txt", "r") as f:
        if len(f.readlines()) > 100:
            with open("log.txt", "w") as f:
                pass
    with open("log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} {type}: {text}\n")
def sync_bals():
    global endpoint
    global bals
    global exclude_from_baltop
    bals = json.loads(requests.get(endpoint + "/get-all-bals").text)
    bals["aaaaaaaaaa (poggingfish)"] = bals["aaaaaaaaaa"]
    bals["buakglrlmx (Stigl)"] = bals["buakglrlmx"]
    exclude_from_baltop = ["aaaaaaaaaa", "buakglrlmx"]
    pog_logger("Synced Balances.", "INFO")
def create_tx(addr1, addr2, amount, password):
    global txs_waiting
    global endpoint
    request = requests.get(endpoint + f"/tx/{addr1}/{addr2}/{amount}/{password}")
    if request.text == "_CLIENT_TRYAGAIN":
        time.sleep(.5)
        create_tx(addr1, addr2, amount, password)
        return 0
    if request.text == "TX Successful!":
        pog_logger(f"Sent {amount} pogcoin to {addr2} from {addr1}", "INFO")
        txs_waiting -= 1
    else:
        pog_logger(f"Failed to send {amount} pogcoin to {addr2} from {addr1}", "ERROR")
        print("\n\n FAILED TO SEND TX \n\n")
        print(request.text)
        txs_waiting -= 1
    return 1
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
            sync_bals()
            with open("wallet.txt", "r") as f:
                name, password = f.read().split("\n")
            if name not in bals:
                print("Your wallet is not in the database. Please create a new wallet.")
                print("Possible reasons:")
                print("You have not created a wallet yet.")
                print("Your wallet was purged when wiping zero balance wallets.")
                exit()
            print("Welcome to the PogCoin CLI!")
            print("ADDR: " + name)
            while True:
                command = input("$ ~ ")
                command = command.split(" ")
                base = command[0]
                if base == "send":
                    sync_bals()
                    if command[1] not in bals:
                        print("Invalid address.")
                        continue
                    if float(command[2]) < 3:
                        print("Sorry. Minimum amount is 3 PogCoin.")
                        continue
                    usr_input = input("Are you sure you want to send "+ command[2] + " pogcoin to " + command[1] + "? (y/n) ")
                    if usr_input == "y":
                        print("Your transaction will be sent shortly.")
                        txs_waiting += 1
                        pog_logger("Started transaction process.", "INFO")
                        threading.Thread(target=create_tx, args=(name, command[1], command[2], password)).start()
                        time.sleep(1)
                    if usr_input == "n":
                        print("Cancelled.")
                elif base == "exit":
                    break
                elif base == "addr":
                    print(f"Your address is {name}")
                    print("Share this with others to receive PogCoin!")
                elif base == "balance":
                    print(f"Your balance is {get_balance(name)} PogCoin")
                elif base == "baltop":
                    sync_bals()
                    print(f"Top {command[1]} balances:")
                    baltop_bals = bals
                    for x in exclude_from_baltop:
                        del baltop_bals[x]
                    baltop_bals = sorted(baltop_bals.items(), key=lambda x: x[1], reverse=True)
                    for x in baltop_bals[:int(command[1])]:
                        print(f"{x[0]} - {x[1]} PogCoin")
                elif base == "supply":
                    sync_bals()
                    baltop_bals = bals
                    for x in exclude_from_baltop:
                        del baltop_bals[x]
                    print(f"The current supply is {sum(baltop_bals.values())} PogCoin")
                    del baltop_bals["burn"]
                    print(f"The current usable supply is {sum(baltop_bals.values())} PogCoin")
                elif base == "balanceof":
                    sync_bals()
                    if command[1] not in bals:
                        print("Invalid address.")
                        continue
                    print(f"{command[1]} has {bals[command[1]]} PogCoin")
                elif base == "get_txs":
                    sync_bals()
                    txs = json.loads(requests.get(endpoint + "/get-txs").text)
                    x = int(command[1])
                    if x >= len(txs):
                        print("Invalid number.")
                        continue
                    while x >= 0:
                        print("Transaction:")
                        print("ID: " + str(x))
                        print(f"From: {txs[str(x)]['from']}")
                        print(f"To: {txs[str(x)]['to']}")
                        print(f"Amount: {txs[str(x)]['amount']}")
                        print(f"Timestamp: {txs[str(x)]['time']}")
                        print("")
                        x -= 1
    except KeyboardInterrupt:
        print("\n\n\nSafley exiting...")
        if txs_waiting > 0:
            print("Waiting for transactions to finish...")
            print("Please wait...")
            while txs_waiting > 0:
                time.sleep(0.1)
        exit()
print("\n\n\nExiting...")
if txs_waiting > 0:
    print("Waiting for transactions to finish...")
    print("Please wait...")
    while txs_waiting > 0:
        time.sleep(0.1)