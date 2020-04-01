#!/usr/bin/env python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--inputFile", dest="inputFile", help="Path to input file", type=str, required=True)
args = parser.parse_args()

pfa1pf  = open("pfa1p_input.txt", "w")
npfa1pf = open("npfa1p_input.txt", "w")

lin_sum_energy_text = "reg [13:0] lin_sum_energy = "
tp_calc_text        = "reg [11:0] tp_calc = "
wait_text           = "#36"

stop = 2000000

lin_sum_energy_pre = 0
lin_sum_energy_now = 0
with open(args.inputFile, "r") as f:

    line = f.readline()
    
    count = 0
    while line:

        if count == stop: break

        line = line.rstrip()

        linesplit = [x.strip() for x in line.split(',')]

        aieta = abs(int(linesplit[0]))

        if aieta < 17: continue

        lin_sum_energy = int(linesplit[1])
        tp_calc        = int(linesplit[2])
        tp_calc_peak   = int(linesplit[3])

        if tp_calc_peak == -1: tp_calc_peak = 2**12

        pfa1pf.write(lin_sum_energy_text  + "14'h" + hex(lin_sum_energy)[2:].zfill(2) + ";\n")
        npfa1pf.write(lin_sum_energy_text + "14'h" + hex(lin_sum_energy)[2:].zfill(2) + ";\n")

        pfa1pf.write(tp_calc_text  + "12'h" + hex(tp_calc_peak)[2:].zfill(2) + ";\n")
        npfa1pf.write(tp_calc_text + "12'h" + hex(tp_calc)[2:].zfill(2) + ";\n")

        #pfa1pf.write(lin_sum_energy_text  + str(lin_sum_energy) + ";\n")
        #npfa1pf.write(lin_sum_energy_text + str(lin_sum_energy) + ";\n")

        #pfa1pf.write(tp_calc_text  + str(tp_calc_peak) + ";\n")
        #npfa1pf.write(tp_calc_text + str(tp_calc) + ";\n")

        pfa1pf.write("\n#36;\n\n")
        npfa1pf.write("\n#36;\n\n")

        count += 1
        line = f.readline()

pfa1pf.close()
npfa1pf.close()
