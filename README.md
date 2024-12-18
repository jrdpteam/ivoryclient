# IvoryClient

IvoryClient is a simple, lightweight GUI-based TCP client built using Python and PyQt5. It allows you to connect to a TCP server using a URL (including .onion domains for Tor), supports Tor, and provides message exchange capabilities.

## Features
- **TCP Communication**: Connect to TCP servers using both standard IP addresses and .onion domains via Tor.
- **Tor Support**: Use Onion network to route your connections.
- **Customizable Buffer Size**: Adjust the buffer size for receiving data.
- **ANSI Color Support**: Display responses with ANSI colors interpreted in the text output. (beta :( )
- **Interactive GUI**: Easy-to-use graphical interface built with PyQt5.

## Requirements
- Python 3.x
- PyQt5 (`pip3 install PyQt5`)
- `pysocks` for SOCKS5 proxy support (`pip3 install pysocks`)

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/jrdpteam/ivoryclient
cd ivoryclient
bash install_dependencies.sh
```

## Usage

```bash
python3 ivoryclient.py
```


The allowed url format looks like this:

    tcp://IPorDOMAIN:PORT


For Tor:

    tcp://example.onion:PORT


#   ! THIS IS NOT A SECURE COMMUNICATOR, IT DOES NOT HAVE BUILT-IN ENCRYPTION. USE WITH CAREFULNESS !


by JRDP Team 2024




