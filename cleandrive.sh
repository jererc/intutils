#!/bin/bash
sudo journalctl --vacuum-time=2d
sudo sh -c 'rm -rf /var/lib/snapd/cache/*'
sudo docker system prune -a --volumes -f
sudo du -ah / | sort -hr | head -n 50
dd if=/dev/zero of=tmpfile bs=8M ; rm tmpfile
