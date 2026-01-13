# Shakti C-Class UART Peripheral Verification

SoC-level verification of UART peripheral on Shakti RISC-V processor using Cocotb framework.

## Project Scope

Verification of UART peripheral's integration with Shakti C-Class processor through AXI4-Lite interface. Testing covers register access, data transmission/reception, configuration options, error handling, and interrupt functionality.

**DUT:** Shakti C-Class SoC with UART peripheral  
**Interface:** AXI4-Lite (memory-mapped registers at `0x11300`)  
**Verification Framework:** Cocotb (Python)  
**Protocol VIPs:** cocotbext-axi, cocotbext-uart

## Setup

### Dependencies
```bash
pip install cocotb cocotbext-axi cocotbext-uart
```

### Reference Repositories (local, not tracked)
```bash
git clone https://github.com/alexforencich/cocotbext-axi.git
git clone https://github.com/alexforencich/cocotbext-uart.git
git clone https://gitlab.com/shaktiproject/cores/c-class.git
git clone https://gitlab.com/shaktiproject/uncore/devices.git
```

## Directory Structure

```
├── sub_system/          # Main testbench
├── system/              # Alternative testbench
├── verilog/             # RTL files
└── .gitignore           # Excludes VIP repos and sim artifacts
```

## Running Tests

### Sub-System
```bash
cd sub_system
make                # Run tests
make WAVES=1        # Generate waveforms
make clean
```

### System
```bash
cd system
export TEST=uart64
make compile; make; make dut
make clean_all
```

## Key Addresses

- **UART Base:** `0x11300`
- **Memory Map:** `c-class/test_soc/c64_c32/Soc.defines`
- **UART Registers:** `devices/uart_v2/uart.defines`

## Test Coverage

_[To be updated as tests are implemented]_

- [ ] TX path verification
- [ ] RX path verification
- [ ] Baud rate configuration
- [ ] Parity modes
- [ ] Status register verification
- [ ] Error condition handling
- [ ] Interrupt functionality

## Progress

_[Updated as work progresses]_

**Current Phase:** Setup and infrastructure development

---

Repository: https://github.com/stativeboss/peripheral_verif

