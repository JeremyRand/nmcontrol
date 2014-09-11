@echo off

echo Configuring Windows DNS Policy for .bit...
regedit /s local_bit_dns_start.reg

echo Starting NMControl...
nmcontrol.exe start --daemon=0

echo NMControl has exited, reverting Windows DNS Policy settings...
regedit /s local_bit_dns_stop.reg

echo Good bye!