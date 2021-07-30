#!/bin/bash
# Coppyright (c) 2020 Francisco Javier Revilla Linares to present.
# All rights reserved.

no_inet_action() {
    shutdown -r +1 'No internet.'
}

wget -q --spider http://google.com

if [ $? -ne 0 ]; then
    no_inet_action
fi
