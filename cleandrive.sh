#!/bin/bash
echo "********************************************************************************"
echo "emptying trash..."
rm -rf ~/.local/share/Trash/files/*
rm -rf ~/.local/share/Trash/info/*

echo "********************************************************************************"
echo "cleaning logs..."
sudo journalctl --vacuum-time=2d

echo "********************************************************************************"
echo "cleaning apt..."
sudo apt -y clean
sudo apt -y autoclean
sudo apt -y autoremove

echo "********************************************************************************"
echo "cleaning snap cache..."
sudo sh -c 'rm -rf /var/lib/snapd/cache/*'

echo "********************************************************************************"
echo "cleaning docker..."
sudo docker system prune -a --volumes -f

echo "********************************************************************************"
echo "drive usage:"
sudo du -ah / | sort -hr | head -n 50

echo "********************************************************************************"
echo "stopping megasync to avoid sync deactivation..."
pkill -SIGTERM megasync
while pgrep -x megasync >/dev/null; do sleep 1; done
echo "optimizing free space..."
dd if=/dev/zero of=tmpfile bs=8M ; rm tmpfile
echo "megasync can be restarted now"

echo "********************************************************************************"
echo "drive usage:"
sudo du -ah / | sort -hr | head -n 50
