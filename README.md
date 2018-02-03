# Dodo

Simple CLI cryptocurrency exchange client based of cryptotik library.

Dodo is a simple CLI wrapper around [cryptotik](https://github.com/peerchemist/cryptotik) library.
Dodo does not have configuration file or keystore, instead it uses native keystore of the underlying OS.
It has been tested with Ubuntu-Gnome (17.04, 17.10) where native Gnome keyring was used to store the API keys.
Keystore package can hook into similar native functionality of Microsoft Windows and OS X as well, so dodo should be quite portable.

> Dodo is work in progress and lacks polish, you are welcome to help with bugfixes and other PR's

## Install

`pip install git+git://github.com/peerchemist/dodo.git`

## Setup

First you need to create API keys for Bittrex, Wex and Poloniex which are supported exchanges for now.
Then you need to insert the API keys into keyring, this can be done as following:

`dodo set_key EXCHANGE APIKEY SECRET`

(EXCHANGE_NAME is {poloniex, wex, bittrex, binance})

The name of the keyring is `dodo` if you wish to inspect manually using program like gnome-seahorse or alike.

## Examples

```Exchanges are reffered to by their popular short names, that is Poloniex.com is "polo", Bittrex is "btrx", Binance is "bnb" and so on.```

`dodo polo markets`

List poloniex markets.

`dodo wex volume ppc-btc`

Show volume of ppc-btc market on wex exchange.

`dodo btrx deposit xrp`

Show deposit address of Ripple on Bittrex exchange.

`dodo polo deposit ppc --new`

Create new deposit address and show it.

`dodo bnb withdraw omg 10.01 0x41c36d0896e3cc86d167ba1ed105b0c62521c54a2`

Withdraw 10.01 OMG from Binance to address.

## bash completion (on *nix platforms)

Create file `.bash_completion` with content:

```
for bcfile in ~/.bash_completion.d/* ; do
    . $bcfile
done
```

Create directory: `mkdir ~/.bash_completion.d`

Export completion file:

`dodo -- --completion > ./bash_completion.d/dodo`

Activate:

`. ~/.bash_completion`

Tab away.

### Tip jar:

> ppc: PVXLbny3ksR8Rh2FZLeigKJRBXQdF36G13
