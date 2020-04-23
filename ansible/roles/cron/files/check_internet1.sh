ping -c4 192.168.1.1 > /dev/null

if [ $? != 0 ]; then
    echo "Offline"
else
    echo "Online"
fi
