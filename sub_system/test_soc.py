import os
import random
from pathlib import Path
from enum import Enum
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
import logging


## SoC Memory Map: https://gitlab.com/shaktiproject/cores/c-class/-/blob/master/test_soc/c64_c32/Soc.defines?ref_type=heads
## UART Register details: https://gitlab.com/shaktiproject/uncore/devices/-/blob/master/uart_v2/uart.defines?ref_type=heads

## CoCoTb Extensions: 
## https://github.com/alexforencich/cocotbext-axi/tree/master
## https://github.com/alexforencich/cocotbext-uart


@cocotb.test()
async def test_peripherals(dut):
    """Test to verify uart through AXI4 transactions"""
    clock = Clock(dut.CLK, 100, unit="ns")  # Create a 10us period clock on port clk
    # Start the clock. Start it low to avoid issues on the first RisingEdge
    cocotb.start_soon(clock.start(start_high=False))
    dut.RST_N.value = 0
    for i in range(0,400):
        await RisingEdge(dut.CLK)

    dut.RST_N.value = 1

    #wait for few cycles and see the waveform: make WAVES=1
