# Digital Systems (CSIE 2344, NTU, Spring 2026)

Coursework from NTU CSIE 2344 Digital Systems, Spring 2026 (114-2).

## Contents

| Folder | Assignment | Description |
| ------ | ---------- | ----------- |
| [`lab2/`](lab2/) | Laboratory 2 | Pipelined fast 4-bit multiplier (`mult_fast`) in Verilog, with testbench waveforms and report |

### Lab 2

- `lab2_part1.v`, `lab2_part2.v`: Verilog sources for Part 1 and Part 2
- `lab2.sav`: GTKWave save file
- `plot_wave.py`: renders VCD waveforms to PNG (`shots/`)
- `build_report.py`: builds `report.pdf` with ReportLab
- `report.pdf`: submitted report

Simulate with Icarus Verilog:

```bash
iverilog -o lab2_part1 lab2_part1.v && vvp lab2_part1
```
