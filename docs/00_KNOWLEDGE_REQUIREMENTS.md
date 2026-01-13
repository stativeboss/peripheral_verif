# Knowledge Requirements for Shakti UART SoC Verification

This document outlines the minimum knowledge required to complete the peripheral-level SoC testing project.

## 1. AXI Protocol - 2-3 days learning

### What you MUST know:
- **AXI4-Lite only** (NOT full AXI4) - it's simpler, just read/write transactions
- **5 channels:**
  - AR (read address)
  - R (read data)
  - AW (write address)
  - W (write data)
  - B (write response)
- **Handshake:** VALID/READY protocol (like PCIe TLP valid/ready)
- **Transaction flow:** Address phase → Data phase → Response
- **RESP codes:** OKAY, SLVERR, DECERR (like PCIe completion status)

### What you DON'T need:
- Bursts, wrapping, narrow transfers (AXI-Lite doesn't have these)
- Transaction ordering, QoS, caching
- Full AXI4 complexities

### Resources:
- ARM IHI0022E spec, Chapter C (AXI-Lite only) - pages 100-120
- cocotbext-axi examples in `cocotbext-axi/tests/axil/` - reverse engineer from code

---

## 2. UART Protocol - 1 day learning

### What you MUST know:
- **Asynchronous serial:** Start bit (0), 5-9 data bits, optional parity, 1-2 stop bits (1)
- **Baud rate:** Bits per second (115200 common)
- **No handshaking** for basic UART (just TX/RX wires)

### What you DON'T need:
- Hardware flow control (RTS/CTS)
- RS-485, RS-422 variants
- Modem control signals

### Resources:
- Wikipedia "UART" article
- `devices/uart_v2/uart.defines` (already in repo)

---

## 3. Python - Already sufficient + 2 days

### What you MUST know:
- **async/await (coroutines)** - critical for cocotb
- Classes and inheritance
- Byte arrays, bit manipulation
- Basic logging

### What you DON'T need:
- Advanced Python features
- Web frameworks, data science libraries

### Quick async/await refresher:
```python
# This is your daily bread in cocotb
async def my_test(dut):
    await some_function()  # Waits for completion
    data = await read_operation()  # Gets return value
```

---

## 4. Cocotb - 3-4 days learning

### What you MUST know:
- `@cocotb.test()` decorator
- Clock generation
- Triggers: `RisingEdge`, `Timer`
- Signal access: `dut.signal.value = X`
- `cocotb.start_soon()` for concurrent tasks
- How to instantiate VIP classes

### What you DON'T need:
- Advanced scheduling
- Custom triggers
- Cocotb internals

### Resources:
- Cocotb docs: quickstart + tutorial (2 hours)
- cocotbext-axi/uart test examples (reverse engineer)

---

## 5. Shakti Processor - 0.5 days

### What you MUST know:
- It's a RISC-V processor (64-bit)
- Memory map (in `c-class/test_soc/c64_c32/Soc.defines`)
- UART is memory-mapped peripheral at `0x11300`
- **That's it!**

### What you DON'T need:
- Instruction set details
- Pipeline architecture
- Cache coherency
- Privilege modes

---

## 6. RISC-V - 0 days

### What you need: **NOTHING** for this project!

You're not running software, not testing CPU instructions. You're only verifying the AXI→UART path. The processor could be ARM, x86, anything - doesn't matter.

---

## Summary

| Topic | Learning Time | Critical Level |
|-------|---------------|----------------|
| AXI4-Lite | 2-3 days | HIGH |
| UART Protocol | 1 day | MEDIUM |
| Python async/await | 2 days | HIGH |
| Cocotb | 3-4 days | HIGH |
| Shakti Processor | 0.5 days | LOW |
| RISC-V ISA | 0 days | NONE |

**Total Learning Investment:** ~8-10 days before starting actual test development
