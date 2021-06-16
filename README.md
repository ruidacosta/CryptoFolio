# CryptoFolio
Control cryptocurrencies portfolio PNL using IEX Cloud API

## Usage
```
$ ./cryptofolio.py -h

usage: cryptofolio.py [-h] [-v] [-d DATA] [-c CONFIG] {list,add,del,modify} ...

Control cryptocurrency protfolio PNL (Profit and Loss) using IEX Cloud API.

positional arguments:
  {list,add,del,modify}
                        Subparsers
    list                list command
    add                 add command
    del                 delete command
    modify              edit command

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show version
  -d DATA, --data DATA  data file path (default: ~/.cryptofolio/folio.data)
  -c CONFIG, --config CONFIG
                        configuration file path (default: ~/.cryptofolio/cryptofolio.config)
```