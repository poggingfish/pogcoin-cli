endpoint = "https://coin.pogging.fish" 
import requests
import time
import json
import os
import datetime
import threading
global bals
exclude_from_baltop = []
txs_waiting = 0
txs = json.loads(open("data/txs.json").read())
bals = {}
#Check if the txs and bals files exist
if os.path.isdir("data") != True:
    os.mkdir("data")
if os.path.isfile("data/txs.json") != True:
    with open("data/txs.json", "w") as f:
        f.write("""
{
    "block_height": 0
}
                """)
if os.path.isfile("data/bals.json") != True:
    with open("data/bals.json", "w") as f:
        f.write("""
{
    "block_height": 0
}
                """)
if os.path.isfile("data/log.txt") != True:
    with open("data/log.txt", "w") as f:
        pass
    with open("bals.json", "w") as f:
        f.write("{}")
def pog_logger(text, type):
    with open("data/log.txt", "r") as f:
        if len(f.readlines()) > 100:
            with open("data/log.txt", "w") as f:
                pass
    with open("data/log.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} {type}: {text}\n")
def sync_bals():
    global txs
    global endpoint
    global bals
    global exclude_from_baltop
    block_height = json.loads(open("data/bals.json").read())["block_height"]
    request = requests.get(endpoint + f"/current-block-height")
    request = requests.get(endpoint + f"/get-blocks-since/{block_height}")
    #Load txs
    for block in json.loads(request.text):
        """
        TX:
        {
        0:{
            "sender": str,
            "receiver": str,
            "amount": int,
            "timestamp": timestamp
        }
        }
        """
        tx = block
        if tx["sender"] not in bals:
            bals[tx["sender"]] = 0
        if tx["receiver"] not in bals:
            bals[tx["receiver"]] = 0
        bals[tx["sender"]] -= tx["amount"]
        bals[tx["receiver"]] += tx["amount"]
        txs[tx["block_id"]] = tx
    #Save txs
    with open("data/txs.json", "w") as f:
        f.write(json.dumps(txs, indent=4))
    #Save block height
    with open("data/bals.json", "w") as f:
        request = requests.get(endpoint + f"/current-block-height")
        f.write(json.dumps({"block_height": request.text}, indent=4))
    #load txs
    with open("data/txs.json", "r") as f:
        txs = json.loads(f.read())
        #load bals
        for tx in txs:
            if txs[tx]["sender"] not in bals:
                bals[txs[tx]["sender"]] = 0
            if txs[tx]["receiver"] not in bals:
                bals[txs[tx]["receiver"]] = 0
            bals[txs[tx]["sender"]] -= txs[tx]["amount"]
            bals[txs[tx]["receiver"]] += txs[tx]["amount"]
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
            with open("data/wallet.txt", "w") as f:
                f.write(f"{name}\n{password}")
            print("Created wallet.")
            print("!! DO NOT SHARE YOUR WALLET WITH ANYONE !!")
            print("Your wallet is saved in wallet.txt")
            pog_logger("New wallet created.", "INFO")
        if run:
            sync_bals()
            with open("data/wallet.txt", "r") as f:
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
                    users_txs = []
                    for x in txs:
                        if txs[x]["sender"] == name or txs[x]["receiver"] == name:
                            print(f"{txs[x]['sender']} -> {txs[x]['receiver']} - {txs[x]['amount']} PogCoin at {txs[x]['time']}")
                elif base == "purge":
                    if name == "aaaaaaaaaa":
                        print(requests.get(endpoint + "/delete_zero/"+password).text)
                elif base == "cls":
                    #If windows
                    if os.name == "nt":
                        os.system("cls")
                    else:
                        os.system("clear")
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