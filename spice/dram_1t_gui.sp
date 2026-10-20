* 1T-1C DRAM cell - Interactive GUI Plot (ngspice)
* Access NMOS: gate=WL, drain=BL, source=SD (storage node); Cs from SD to gnd.
.include nmos_generic.inc
.param VDD=5 W=2u L=0.18u CS=1p

M1 BL WL SD 0 nmos w={W} l={L}
Cs SD 0 {CS}

Vwl WL 0 PULSE(0 {VDD} 0 5n 5n 95n 200n)
Vbl BL 0 PULSE(0 {VDD} 0 5n 5n 95n 200n)

.tran 0.5n 800n
.control
run
plot v(wl) v(bl) v(sd) title "1T-1C DRAM Transient Waveforms (WL, BL, SD)"
.endc
.end
