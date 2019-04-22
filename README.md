[![Build Status](https://travis-ci.org/toros-astro/lvcgcn_prep.svg?branch=master)](https://travis-ci.org/toros-astro/lvcgcn_prep)
# LVC GCN Daemon Service [In preparation]

This is intended to perform various tasks

* A daemon to establish a connection with LVC GCN notices to receive alerts and notify the collaborators (`listen.py`).
* Once the alert VOEvent is received, generate possible targets of observation (`scheduler.py`).
* Send out emails with alert information to collaborators and upload observation targets to broker website (`listen.py`).

-------

(c) TOROS Dev Team
