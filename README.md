# Dodo

Simple CLI cryptocurrency exchange client based of cryptotik library.

Dodo is a simple CLI wrapper around [cryptotik](github.com/peerchemist/cryptotik) library.
Dodo does not have configuration file or keystore, instead it uses native keystore of the underlying OS.
It has been tested with Ubuntu-Gnome 17.04 where native Gnome keyring was used to store the API keys.
Keystore package can hook into similar native functionality of Microsoft Windows and OS X as well, so dodo should be quite portable.

> Dodo is work in progress and lacks polish, you are welcome to help with bugfixes and other PR's

## Install

`pip install git+git://github.com/peerchemist/dodo.git`

## Setup

First you need to create API keys for Bittrex, Wex and Poloniex which are supported exchanges for now.
Then you need to insert the API keys into keyring, this can be done as following:

`python3 -m dodo EXCHANGE_NAME dodo {APIkey}<\/&>{APIsecret}`

The name of the keyring is `dodo` and APIkey and APIsecret are delimited by `<\/&>` which is quite specific and no conflicts with key and secret string are expected.
Strings are stored in this manner because keyring is expecting username:password format.
I've used `username` field for exchange name and `password` for concatenated APIkey:secret, whilst using `<\/&>` delimiter to separate them.


## Examples

`dodo polo markets`

List poloniex markets.

`dodo wex volume ppc-btc`

Show volume of ppc-btc market on wex exchange.

`dodo btrx deposit xrp`

Show deposit address of Ripple on Bittrex exchange.

### Tip jar:

> ppc: PVXLbny3ksR8Rh2FZLeigKJRBXQdF36G13

> btc: 13rrCWJkq1h611pBjwsF6jdABtQutx1Li4