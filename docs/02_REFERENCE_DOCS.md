# Quick Reference Documentation

## SoC Memory Map

From: `c-class/test_soc/c64_c32/Soc.defines`

| Peripheral | Base Address | End Address | Description |
|------------|--------------|-------------|-------------|
| UART | `0x00011300` | `0x00011340` | UART peripheral |
| Memory | `0x80000000` | `0x8FFFFFFF` | Main memory |
| BootROM | `0x00001000` | `0x00010FFF` | Boot ROM |
| CLINT | `0x02000000` | `0x020BFFFF` | Timer/Interrupt controller |
| Debug | `0x00000000` | `0x00000FFF` | Debug module |

---

## UART Register Map

**Base Address:** `0x11300`

From: `devices/uart_v2/uart.defines`

| Offset | Register | Size | R/W | Description |
|--------|----------|------|-----|-------------|
| 0x00 | BaudReg | 16-bit | R/W | Baud rate divisor |
| 0x04 | TxReg | 8-bit | W | TX data register (write to transmit) |
| 0x08 | RxReg | 8-bit | R | RX data register (read received data) |
| 0x0C | StatusReg | 16-bit | R | Status flags |
| 0x10 | DelayReg | 16-bit | R/W | TX delay control |
| 0x14 | ControlReg | 16-bit | R/W | Character size, parity, stop bits config |
| 0x18 | InterruptEn | 16-bit | R/W | Interrupt enable bits |
| 0x20 | RX_Threshold | 8-bit | R/W | RX FIFO threshold |

---

## StatusReg Bit Map (Offset 0x0C)

| Bit | Name | Description |
|-----|------|-------------|
| 8 | RX_FIFO_80_FULL | RX FIFO ~80% full |
| 7 | BREAK_ERROR | Break condition detected |
| 6 | FRAME_ERROR | Framing error (invalid stop bit) |
| 5 | OVERRUN | RX FIFO overflow |
| 4 | PARITY_ERROR | Parity check failed |
| 3 | RX_FULL | RX FIFO completely full |
| 2 | **RX_NOT_EMPTY** | **RX FIFO has data (poll before read)** |
| 1 | TX_FULL | TX FIFO completely full |
| 0 | **TX_EMPTY** | **TX FIFO empty (ready for data)** |

### Common Status Checks

**Before writing TX:**
```python
status = await read_status()
if not (status & 0x0002):  # TX not full
    await write_tx(data)
```

**Before reading RX:**
```python
status = await read_status()
if status & 0x0004:  # RX not empty
    data = await read_rx()
```

---

## ControlReg Bit Map (Offset 0x14)

| Bits | Field | Values | Description |
|------|-------|--------|-------------|
| 10:5 | Character Size | 0-4 | Character size: value+5 (5-9 bits) |
| 4:3 | Parity | 00, 01, 10 | 00=None, 01=Odd, 10=Even, 11=Undefined |
| 2:1 | Stop Bits | 00, 01, 10 | 00=1 bit, 01=1.5 bits, 10=2 bits |
| 0 | Reserved | - | Reserved |

### Configuration Examples

**8N1 (8 data bits, no parity, 1 stop bit) - Default:**
```
Bits [10:5] = 3 (8-5=3)
Bits [4:3]  = 0 (no parity)
Bits [2:1]  = 0 (1 stop bit)
Value = 0x0060
```

**8E1 (8 data bits, even parity, 1 stop bit):**
```
Bits [10:5] = 3
Bits [4:3]  = 2 (even parity)
Bits [2:1]  = 0
Value = 0x0070
```

---

## InterruptEn Register (Offset 0x18)

| Bit | Interrupt Source | Description |
|-----|------------------|-------------|
| 8 | RX_FIFO_80_FULL | Interrupt when RX FIFO reaches threshold |
| 7 | BREAK_ERROR | Interrupt on break condition |
| 6 | FRAME_ERROR | Interrupt on framing error |
| 5 | OVERRUN | Interrupt on RX overflow |
| 4 | PARITY_ERROR | Interrupt on parity error |
| 3 | RX_NOT_EMPTY | Interrupt when data received |
| 2 | RX_NOT_FULL | Interrupt when RX FIFO not full |
| 1 | TX_NOT_FULL | Interrupt when TX FIFO has space |
| 0 | TX_DONE | Interrupt when transmission complete |

---

## UART Protocol Basics

### Frame Format (8N1 example)

```
 Start  D0  D1  D2  D3  D4  D5  D6  D7  Stop
   0    LSB                     MSB    1
<-1-><----------8 bits----------><-1->
```

- **Start bit:** Always 0 (marks beginning)
- **Data bits:** 5-9 bits, LSB first
- **Parity bit:** Optional (odd/even)
- **Stop bits:** 1, 1.5, or 2 bits (always 1)

### Timing

Bit time = 1 / baud_rate

For 115200 baud:
- Bit time = 1/115200 = 8.68 μs
- Byte time (10 bits for 8N1) = 86.8 μs

---

## AXI4-Lite Transaction Examples

### Write Transaction (AXI → UART TX)

```
Write 'A' (0x41) to UART TX register at 0x11304:

1. Address Phase (AW channel):
   AWADDR  = 0x11304
   AWVALID = 1
   Wait for AWREADY = 1
   
2. Data Phase (W channel):
   WDATA   = 0x41
   WSTRB   = 0x1  (byte enable)
   WVALID  = 1
   Wait for WREADY = 1
   
3. Response Phase (B channel):
   Wait for BVALID = 1
   Check BRESP = 00 (OKAY)
   Assert BREADY = 1
```

### Read Transaction (UART Status → AXI)

```
Read status register at 0x1130C:

1. Address Phase (AR channel):
   ARADDR  = 0x1130C
   ARVALID = 1
   Wait for ARREADY = 1
   
2. Data Phase (R channel):
   Wait for RVALID = 1
   Read RDATA (16 bits)
   Check RRESP = 00 (OKAY)
   Assert RREADY = 1
```

---

## Common Baud Rate Divisors

Assuming system clock frequency, calculate divisor:

```
divisor = (clock_freq / (16 * baud_rate)) - 1
```

Example for 50 MHz clock:

| Baud Rate | Divisor (approx) |
|-----------|------------------|
| 9600 | 325 |
| 19200 | 162 |
| 38400 | 81 |
| 57600 | 54 |
| 115200 | 27 |
| 230400 | 13 |
| 460800 | 6 |
| 921600 | 3 |

*(Actual values depend on your system clock - verify from design specs)*

---

## Software Reference (uart_driver.c)

From: `devices/uart_v2/uart_driver.c`

### Poll-based TX (putchar)
```c
// Wait for TX not full (bit 1 of status = 0)
do {
    status = *(uint16_t*)(0x11300 + 0xC);
} while (status & 0x2);

// Write byte to TX register
*(uint8_t*)(0x11300 + 0x4) = data;
```

### Poll-based RX (getchar)
```c
// Wait for RX not empty (bit 2 of status = 1)
do {
    status = *(uint16_t*)(0x11300 + 0xC);
} while (!(status & 0x4));

// Read byte from RX register
data = *(uint8_t*)(0x11300 + 0x8);
```

---

## DUT Signal Names (Typical)

Based on Shakti SoC RTL:

| Signal | Direction | Description |
|--------|-----------|-------------|
| CLK | Input | System clock |
| RST_N | Input | Active-low reset |
| uart_tx | Output | UART transmit data |
| uart_rx | Input | UART receive data |
| axi_awaddr | Input | AXI write address |
| axi_awvalid | Input | AXI write address valid |
| axi_awready | Output | AXI write address ready |
| axi_wdata | Input | AXI write data |
| axi_wstrb | Input | AXI write strobe |
| axi_wvalid | Input | AXI write data valid |
| axi_wready | Output | AXI write data ready |
| axi_bresp | Output | AXI write response |
| axi_bvalid | Output | AXI write response valid |
| axi_bready | Input | AXI write response ready |
| axi_araddr | Input | AXI read address |
| axi_arvalid | Input | AXI read address valid |
| axi_arready | Output | AXI read address ready |
| axi_rdata | Output | AXI read data |
| axi_rresp | Output | AXI read response |
| axi_rvalid | Output | AXI read data valid |
| axi_rready | Input | AXI read data ready |

*(Verify actual signal names from your RTL)*

---

## Quick Commands

### Install Dependencies
```bash
pip install cocotb cocotbext-axi cocotbext-uart
```

### Run Tests
```bash
cd sub_system
make                    # Run all tests
make WAVES=1           # Generate waveforms
make TEST=test_name    # Run specific test
```

### View Waveforms
```bash
gtkwave dump.vcd       # GTKWave
verdi -ssf dump.fsdb   # Verdi
```

### Debug
```bash
# Add to test for detailed logging
cocotb.log.setLevel(logging.DEBUG)
```
