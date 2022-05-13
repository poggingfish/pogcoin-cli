import colorama
import sys
import os
import time
import requests
import json
import random
import regex as re
import difflib
import signal
version = "1.0.5"
txs = {}
endpoint = "https://coin.pogging.fish/"
MOTDS = [
    "Make sure to backup your wallet!",
    "Check out my website: https://pogging.fish/",
    "Consider contributing to the project: https://github.com/poggingfish/pogcoin-cli",
    "This is a beta version, so please report any bugs you find!",
    "If you like this project, you might like some of my other projects: https://pogging.fish/",
    "This client is open source, so feel free to fork it and make your own version!",
    "The API's are free to use. So you can make your own client!",
    "Documentation is coming soon!",
    "A GUI is coming soon!",
    "Pogcoin != Cryptocurrency"
]
if os.name == 'nt':
    os.system('cls')
else:
    os.system('clear')
def loading_bar(times):
    for i in range(times):
        sys.stdout.write("\rLoading: " + colorama.Fore.GREEN + "\|/-"[i%4])
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\rLoading: " + colorama.Fore.GREEN + "Done!\n")
def sync_txs():
    global txs
    txs = json.load(open("txs.json"))
    if len(txs)-1 > 0:
        highest_id = int(txs[str(len(txs)-1)]["tx_id"])
        json_txs = json.loads(requests.get(endpoint + "txs/" + str(highest_id+1)).text)
    else:
        json_txs = json.loads(requests.get(endpoint + "txs/0").text)
    if len(json_txs) == 0:
        time.sleep(0.5)
    else:
        txs.update(json_txs)
    json.dump(txs, open("txs.json", "w"), indent=4)
    return
def get_balance(user):
    global txs
    balance = 0
    if user == "genesis":
        return 0
    for tx in txs:
        if txs[tx]["from"] == user:
            balance -= int(txs[tx]["amount"])
        if txs[tx]["to"] == user:
            balance += int(txs[tx]["amount"])
    return balance
def get_all_addresses():
    global txs
    addresses = []
    for tx in txs:
        if txs[tx]["from"] not in addresses:
            addresses.append(txs[tx]["from"])
        if txs[tx]["to"] not in addresses:
            addresses.append(txs[tx]["to"])
    return addresses
def get_total_supply():
    global txs
    supply = 0
    for x in get_all_addresses():
        supply += get_balance(x)
    usable_supply = supply - get_balance("000000000000000")
    return supply, usable_supply
def get_top_addresses(amount):
    global txs
    addresses = []
    for x in get_all_addresses():
        addresses.append((x, get_balance(x)))
    addresses.sort(key=lambda x: x[1], reverse=True)
    return dict(addresses[:amount])
def signal_handler(sig, frame):
    print("\n")
    print(colorama.Fore.GREEN + "Exiting...")
    sync_txs()
    #Re-enable cursor
    if os.name == 'nt':
        os.system('mode con: cols=80 lines=20')
    else:
        os.system('tput cnorm')
    if os.path.isfile("wallet_bkp.json"):
        os.system("mv wallet_bkp.json wallet.json")
    sys.exit()
signal.signal(signal.SIGTSTP, signal_handler)
def main():
    doas = False
    temp_wallet = False
    ver = json.loads(requests.get(endpoint + "ver").text)
    if ver["version"] != version:
        print("Your CLI version is outdated! Please update to version " + ver["version"] + ".")
        print("Get it here: https://github.com/poggingfish/pogcoin-cli")
        print("Or. If you cloned the repo, run: " + colorama.Fore.GREEN + "git pull")
        print("\n\n")
        sys.exit(0)
    if len(sys.argv) > 1:
        if sys.argv[1] == "-v" or sys.argv[1] == "--version":
            print("PogCoin CLI v" + version)
            sys.exit()
        elif sys.argv[1] == "--help":
            print("-v or --version: Prints the version of the CLI.")
            print("--temp-wallet: Creates a temporary wallet.")
            sys.exit()
        elif sys.argv[1] == "--temp-wallet":
            temp_wallet = True
        else:
            print("Unknown argument: " + sys.argv[1])
            print("Use --help for more info.")
            sys.exit()
    
    global txs
    print("\n\n")
    #check if wallet.json exists
    #Disable cursor
    if os.name == 'nt':
        os.system('mode con: cols=80 lines=20')
    else:
        os.system('tput civis')
    if os.path.isfile("wallet.json"):
        print(colorama.Fore.GREEN + "Wallet found!")
        time.sleep(0.5)
    else:
        print(colorama.Fore.RED + "No wallet found!")
        print(colorama.Fore.GREEN + "Creating wallet...")
        wallet = requests.post(endpoint + "wallet")
        json_wallet = json.loads(wallet.text)
        with open("wallet.json", "w") as f:
            json.dump(json_wallet, f, indent=4)
        loading_bar(10)
        print(colorama.Fore.GREEN + "Wallet created!")
    if os.path.isfile("txs.json"):
        print(colorama.Fore.GREEN + "Transcation History Found!")
        time.sleep(0.5)
    else:
        print(colorama.Fore.RED + "No Transaction History Found!")
        print(colorama.Fore.GREEN + "Creating Transaction History...")
        with open("txs.json", "w") as f:
            json.dump({}, f, indent=4)
        loading_bar(10)
        print(colorama.Fore.GREEN + "Transaction History Created!")
    print("Syncing Transaction History...")
    sync_txs()
    loading_bar(10)
    print(colorama.Fore.GREEN + "Transaction History Synced!")
    
    #Re-enable cursor
    if os.name == 'nt':
        os.system('mode con: cols=80 lines=20')
    else:
        os.system('tput cnorm')
    #START OF CLI
    if temp_wallet:
        temporary_wallet = json.loads(requests.get(endpoint + "wallet").text)
        os.system("mv wallet.json wallet_bkp.json")
        with open("wallet.json", "w") as f:
            json.dump(temporary_wallet, f, indent=4)
    print(colorama.Fore.GREEN + "\n\nPogcoin CLI v" + version + "\n")
    print(colorama.Fore.GREEN + "Made by: " + colorama.Fore.RED + "poggingfish\n")
    print(colorama.Fore.GREEN + random.choice(MOTDS))
    print(colorama.Fore.GREEN + "\nType 'help' for help")
    while True:
        #Display shell as publickey ~$
        command_split = input(colorama.Fore.CYAN + json.loads(open("wallet.json").read())["public_key"] + colorama.Fore.GREEN + " ~$ " + colorama.Fore.WHITE).split(" ")              
        #Input  parsing
        command = command_split[0]
        if command == "cls" or command == "clear":
            if os.name == 'nt':
                os.system('cls')
            else:
                os.system('clear')
        elif command == "help":
            print(colorama.Fore.GREEN + "Commands:")
            print(colorama.Fore.GREEN + "help - Displays this help menu")
            print(colorama.Fore.GREEN + "cls/clear - Clears the screen")
            print(colorama.Fore.GREEN + "balance - Displays your balance")
            print(colorama.Fore.GREEN + "send <to> <amount> - Sends a transaction")
            print(colorama.Fore.GREEN + "balanceof <address> - Displays the balance of an address")
            print(colorama.Fore.GREEN + "history - Displays your transaction history")
            print(colorama.Fore.GREEN + "txinfo <tx_id> - Displays information about a transaction")
            print(colorama.Fore.GREEN + "addr - Displays your address")
            print(colorama.Fore.GREEN + "supply - Displays the total supply")
            print(colorama.Fore.GREEN + "top <amount> - Displays the top <amount> addresses")
            print(colorama.Fore.GREEN + "resync - Resyncs the transaction history")
            print(colorama.Fore.GREEN + "burn <amount> - Permenantly destroys pogcoins")
            print(colorama.Fore.GREEN + "doas <user> <private_key> - Become another user")
            print(colorama.Fore.GREEN + "doas_back - Become the original user")
            print(colorama.Fore.GREEN + "exit - Exits the program")
        elif command == "balance":
            sync_txs()
            print(colorama.Fore.WHITE + "Your balance is: " + colorama.Fore.CYAN + str(get_balance(json.load(open("wallet.json"))["public_key"])))
        elif command == "send":
            # /tx/<from>/<to>/<amount>/<private_key>
            sync_txs()
            if len(command_split) == 3:
                if get_balance(json.load(open("wallet.json"))["public_key"]) < float(command_split[2]):
                    print(colorama.Fore.RED + "You do not have enough Pogcoins!")
                    continue
                yn = input(colorama.Fore.GREEN + "Are you sure you want to send " + colorama.Fore.CYAN + command_split[2] + colorama.Fore.GREEN + " Pogcoins to " + colorama.Fore.CYAN + command_split[1] + colorama.Fore.GREEN + "? (y/n) ")
                if yn == "y":
                    tx = requests.get(endpoint + "tx/" + json.load(open("wallet.json"))["public_key"] + "/" + command_split[1] + "/" + command_split[2] + "/" + json.load(open("wallet.json"))["private_key"])
                    if tx.text == "Transaction successful":
                        print(colorama.Fore.GREEN + "Transaction successful!")
                        sync_txs()
                    else:
                        print(colorama.Fore.RED + tx.text)
                else:
                    print(colorama.Fore.GREEN + "Transaction cancelled!")
            else:
                print(colorama.Fore.RED + "Not enough arguments!")
        elif command == "balanceof":
            sync_txs()
            if len(command_split) == 2:
                print(colorama.Fore.WHITE + "The balance of " + colorama.Fore.CYAN + command_split[1] + colorama.Fore.WHITE + " is: " + colorama.Fore.CYAN + str(get_balance(command_split[1])))
            else:
                print(colorama.Fore.RED + "Not enough arguments!")
        elif command == "history":
            sync_txs()
            for tx in txs:
                if txs[tx]["from"] == json.load(open("wallet.json"))["public_key"]:
                    print(colorama.Fore.WHITE + "You sent " + colorama.Fore.CYAN + str(txs[tx]["amount"]) + colorama.Fore.WHITE + " Pogcoins to " + colorama.Fore.CYAN + txs[tx]["to"])
                elif txs[tx]["to"] == json.load(open("wallet.json"))["public_key"]:
                    print(colorama.Fore.WHITE + "You received " + colorama.Fore.CYAN + str(txs[tx]["amount"]) + colorama.Fore.WHITE + " Pogcoins from " + colorama.Fore.CYAN + txs[tx]["from"])
        elif command == "txinfo":
            if len(command_split) == 2:
                sync_txs()
                if command_split[1] in txs:
                    print(colorama.Fore.WHITE + "Transaction ID: " + colorama.Fore.CYAN + command_split[1])
                    print(colorama.Fore.WHITE + "From: " + colorama.Fore.CYAN + txs[command_split[1]]["from"])
                    print(colorama.Fore.WHITE + "To: " + colorama.Fore.CYAN + txs[command_split[1]]["to"])
                    print(colorama.Fore.WHITE + "Amount: " + colorama.Fore.CYAN + str(txs[command_split[1]]["amount"]))
                else:
                    print(colorama.Fore.RED + "Invalid transaction ID!")
            else:
                print(colorama.Fore.RED + "Not enough arguments!")
        elif command == "addr":
            print(colorama.Fore.WHITE + "Your address is: " + colorama.Fore.CYAN + json.load(open("wallet.json"))["public_key"])
        elif command == "supply":
            sync_txs()
            print(colorama.Fore.WHITE + "The total supply is: " + colorama.Fore.CYAN + str(get_total_supply()[0]))
            print(colorama.Fore.WHITE + "The total usable supply is: " + colorama.Fore.CYAN + str(get_total_supply()[1]))
        elif command == "top":
            sync_txs()
            if len(command_split) == 2:
                top_addresses = get_top_addresses(int(command_split[1]))
                for address in top_addresses:
                    #Print the address and the balance
                    print(colorama.Fore.WHITE + str(top_addresses[address]) + colorama.Fore.CYAN + " Pogcoins in account " + colorama.Fore.WHITE + address)        
            else:
                print(colorama.Fore.RED + "Not enough arguments!")
        elif command == "resync":
            os.remove("txs.json")
            with open("txs.json", "w") as txs_file:
                txs_file.write("{}")
            sync_txs()
        elif command == "burn":
            #Burn address: 000000000000000
            print("!! THIS IS A PERMANENT BURN ADDRESS !!\n")
            tx_question = input(colorama.Fore.GREEN + "Are you sure you want to burn " + colorama.Fore.CYAN + command_split[1] + colorama.Fore.GREEN + " Pogcoins? (y/n) ")
            if tx_question != "y":
                continue
            if len(command_split) == 2:
                tx = requests.get(endpoint + "tx/" + json.load(open("wallet.json"))["public_key"] + "/" + "000000000000000" + "/" + command_split[1] + "/" + json.load(open("wallet.json"))["private_key"])
                if tx.text == "Transaction successful":
                    print(colorama.Fore.GREEN + "Destroyed " + colorama.Fore.CYAN + command_split[1] + colorama.Fore.GREEN + " Pogcoins!")
                    sync_txs()
                else:
                    print(colorama.Fore.RED + tx.text)
        elif command == "doas":
            if temp_wallet:
                print(colorama.Fore.RED + "You cannot doas while in a temporary wallet!")
                continue
            if doas == True:
                print(colorama.Fore.RED + "Please use doas_back before using doas again!")
                continue
            if len(command_split) < 3:
                print(colorama.Fore.RED + "Not enough arguments!")
                continue
            if len(command_split) > 3:
                print(colorama.Fore.RED + "Too many arguments!")
                continue
            #Copy the wallet.json file to wallet_bkp.json
            os.rename("wallet.json", "wallet_bkp.json")
            os.system("cp wallet_bkp.json wallet.json")
            #save the private key and public key to the wallet.json file
            #The private key is the last argument
            #The public key is the first argument
            with open("wallet.json", "r") as wallet_file:
                wallet = json.load(wallet_file)
            #Make sure command has not been run before
            wallet["public_key"] = command_split[1]
            wallet["private_key"] = command_split[2]
            json.dump(wallet, open("wallet.json", "w"))
            doas = True
        elif command == "doas_back":
            if temp_wallet:
                print(colorama.Fore.RED + "You cannot doas_back while in a temporary wallet!")
                continue
            #Copy the wallet_bkp.json file to wallet.json
            os.remove("wallet.json")
            os.rename("wallet_bkp.json", "wallet.json")
            doas = False
        elif command == "exit":
            
            break
        else:
            if command != "":
                #Detect close matches (Be generous)
                commands = ["balanceof", 
                            "history", 
                            "txinfo", 
                            "addr", 
                            "supply", 
                            "top", 
                            "resync", 
                            "burn", 
                            "exit", 
                            "cls", 
                            "clear",
                            "help",
                            "balance"]
                #Get the closest match
                closest_match = difflib.get_close_matches(command, commands, 1, 0.5)
                if len(closest_match) > 0:
                    print(colorama.Fore.RED + "Did you mean " + colorama.Fore.CYAN + closest_match[0] + colorama.Fore.RED + "?")
                else:
                    print(colorama.Fore.RED + "Invalid command!")
    print(colorama.Fore.GREEN + "Exiting...")
    sync_txs()
    if os.path.isfile("wallet_bkp.json"):
        os.system("mv wallet_bkp.json wallet.json")
    sys.exit()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print(colorama.Fore.GREEN + "Exiting...")
        sync_txs()
        #Re-enable cursor
        if os.name == 'nt':
            os.system('mode con: cols=80 lines=20')
        else:
            os.system('tput cnorm')
        if os.path.isfile("wallet_bkp.json"):
            os.system("mv wallet_bkp.json wallet.json")
        sys.exit()