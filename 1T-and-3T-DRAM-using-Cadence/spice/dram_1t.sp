* 1T-1C DRAM cell - write then hold/read (ngspice)
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
set wr_singlescale
set wr_vecnames
wrdata results/dram_1t_waveform.dat time v(wl) v(bl) v(sd)
meas tran v_store_hi MAX v(SD)
meas tran v_store_lo MIN v(SD)
.endc
.end
