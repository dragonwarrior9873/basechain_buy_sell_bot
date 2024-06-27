
# Arb Jupiter Bot - JUPV4 

This bot is to allow you to buy and sell tokens on the Base blockchain. The bot is currently written in python and uses the Uniswap V3 to execute trades.

## nav

 ⚡️[install](#install) 
# install

> Please install environment.(Install python in Ubuntu)

```bash
sudo apt install python3
sudo apt install python3-pip
sudo pip3 install --upgrade pip
pip3 install <package name>
...
```

Set your wallet private key in the `./asset.py` file

```
private_key=...
```

Set the gas price in the './main.py' file

```
gas_price = w3base.to_wei(1, 'gwei') // set value instead of first parameter - 1
```

· [back to top](#nav) ·
