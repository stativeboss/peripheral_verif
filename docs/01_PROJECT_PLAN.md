# Shakti UART SoC Verification - Project Execution Plan

## Project Overview

**Title:** Peripheral (UART) based SoC (Subsystem) Level Testing of Shakti Processor

**Goal:** Verify that the Shakti RISC-V processor can successfully control the UART peripheral through the AXI4-Lite bus interface.

---

## Phase 1: Setup & Learning (Week 1)

### Objective
Environment working, basic understanding of tools and protocols

### Day 1-2: Environment Setup
- [ ] Install cocotb: `pip install cocotb cocotbext-axi cocotbext-uart`
- [ ] Verify simulator installation (Verilator/Icarus/Modelsim)
- [ ] Run existing Makefile in `sub_system/`
- [ ] Generate waveforms with `make WAVES=1`
- [ ] Open waveforms in GTKWave/Verdi
- [ ] Verify basic clock/reset functionality

### Day 3-4: Learn AXI-Lite
- [ ] Read cocotbext-axi README
- [ ] Run `cocotbext-axi/tests/axil/test_axil.py` 
- [ ] Study AxiLiteMaster API documentation
- [ ] Experiment with simple read/write operations
- [ ] Understand AXI4-Lite handshake timing

### Day 5: Learn UART & Cocotb Basics
- [ ] Read cocotbext-uart README
- [ ] Run `cocotbext-uart/tests/uart/test_uart.py`
- [ ] Study cocotb trigger/clock examples
- [ ] Read `devices/uart_v2/uart.defines` - map out registers
- [ ] Understand UART frame format

### Deliverable
✅ Working test that toggles reset and reads UART status register via AXI

---

## Phase 2: Infrastructure (Week 2)

### Objective
Build reusable testbench classes and utilities

### Day 6-7: Register Abstraction Layer

**Create:** `sub_system/uart_regs.py`

```python
class UartRegisters:
    """UART register map and access methods"""
    UART_BASE = 0x11300
    
    # Register offsets
    BAUD_OFFSET = 0x00
    TX_OFFSET = 0x04
    RX_OFFSET = 0x08
    STATUS_OFFSET = 0x0C
    DELAY_OFFSET = 0x10
    CONTROL_OFFSET = 0x14
    INTERRUPT_EN_OFFSET = 0x18
    RX_THRESHOLD_OFFSET = 0x20
    
    # Status register bit masks
    STATUS_RX_FIFO_80_FULL = (1 << 8)
    STATUS_BREAK_ERROR = (1 << 7)
    STATUS_FRAME_ERROR = (1 << 6)
    STATUS_OVERRUN = (1 << 5)
    STATUS_PARITY_ERROR = (1 << 4)
    STATUS_RX_FULL = (1 << 3)
    STATUS_RX_NOT_EMPTY = (1 << 2)
    STATUS_TX_FULL = (1 << 1)
    STATUS_TX_EMPTY = (1 << 0)
    
    async def write_tx(self, axi_master, data):
        """Write byte to TX register"""
        await axi_master.write(self.UART_BASE + self.TX_OFFSET, data)
    
    async def read_rx(self, axi_master):
        """Read byte from RX register"""
        resp = await axi_master.read(self.UART_BASE + self.RX_OFFSET, 1)
        return resp.data
    
    async def read_status(self, axi_master):
        """Read status register"""
        resp = await axi_master.read(self.UART_BASE + self.STATUS_OFFSET, 2)
        return int.from_bytes(resp.data, 'little')
    
    # ... more methods
```

### Day 8-9: Testbench Environment Class

**Create:** `sub_system/shakti_env.py`

```python
class ShaktiUartEnv:
    """Main testbench environment for Shakti UART testing"""
    
    def __init__(self, dut, uart_baud=115200):
        self.dut = dut
        self.log = logging.getLogger("shakti_env")
        
        # Instantiate VIPs
        self.axi_master = AxiLiteMaster(
            AxiLiteBus.from_prefix(dut, "axi"), 
            dut.CLK, 
            dut.RST_N,
            reset_active_level=False
        )
        
        self.uart_sink = UartSink(dut.uart_tx, baud=uart_baud)
        self.uart_source = UartSource(dut.uart_rx, baud=uart_baud)
        
        # Register model
        self.regs = UartRegisters()
        
    async def reset_dut(self, cycles=10):
        """Perform DUT reset"""
        self.dut.RST_N.value = 0
        for _ in range(cycles):
            await RisingEdge(self.dut.CLK)
        self.dut.RST_N.value = 1
        for _ in range(5):
            await RisingEdge(self.dut.CLK)
        self.log.info("Reset complete")
        
    async def configure_uart(self, baud_div=0, parity='N', stop_bits=1, char_size=8):
        """Configure UART parameters"""
        # Write to baud register
        if baud_div > 0:
            await self.axi_master.write(
                self.regs.UART_BASE + self.regs.BAUD_OFFSET, 
                baud_div.to_bytes(2, 'little')
            )
        
        # Build control register value
        control_val = 0
        control_val |= ((char_size - 5) << 5)  # Character size
        
        if parity == 'O':
            control_val |= (1 << 3)  # Odd parity
        elif parity == 'E':
            control_val |= (2 << 3)  # Even parity
        
        if stop_bits == 2:
            control_val |= (2 << 1)
        elif stop_bits == 1.5:
            control_val |= (1 << 1)
            
        await self.axi_master.write(
            self.regs.UART_BASE + self.regs.CONTROL_OFFSET,
            control_val.to_bytes(2, 'little')
        )
        
        self.log.info(f"UART configured: parity={parity}, stop={stop_bits}, char={char_size}")
    
    async def wait_tx_ready(self, timeout_cycles=1000):
        """Poll until TX is ready (not full)"""
        for _ in range(timeout_cycles):
            status = await self.regs.read_status(self.axi_master)
            if not (status & self.regs.STATUS_TX_FULL):
                return True
            await RisingEdge(self.dut.CLK)
        raise TimeoutError("TX never became ready")
    
    async def wait_rx_data(self, timeout_cycles=1000):
        """Poll until RX has data"""
        for _ in range(timeout_cycles):
            status = await self.regs.read_status(self.axi_master)
            if status & self.regs.STATUS_RX_NOT_EMPTY:
                return True
            await RisingEdge(self.dut.CLK)
        raise TimeoutError("RX data never arrived")
```

### Day 10: Basic Checkers & Utilities

**Create:** `sub_system/uart_checkers.py`

```python
class UartCheckers:
    """Protocol checkers and utilities"""
    
    @staticmethod
    def check_status_flags(status, expected_flags, msg=""):
        """Verify status register flags"""
        for flag_name, flag_mask in expected_flags.items():
            if status & flag_mask:
                logging.info(f"✓ {flag_name} is set {msg}")
            else:
                raise AssertionError(f"✗ {flag_name} not set {msg}")
    
    @staticmethod
    def compare_data(sent, received, name="Data"):
        """Compare sent vs received data"""
        if sent != received:
            raise AssertionError(
                f"{name} mismatch!\n"
                f"  Sent:     {sent.hex()}\n"
                f"  Received: {received.hex()}"
            )
        logging.info(f"✓ {name} match: {sent.hex()}")
```

### Deliverable
✅ Reusable environment class  
✅ Can configure UART and send/receive 1 byte  
✅ Helper functions for common operations

---

## Phase 3: Core Tests (Week 3-4)

### Objective
Basic functionality coverage - happy path testing

### Day 11-12: UART TX Path Tests

**File:** `sub_system/test_uart_tx.py`

```python
@cocotb.test()
async def test_uart_tx_single_byte(dut):
    """Write single byte via AXI, verify on UART TX pin"""
    
@cocotb.test()
async def test_uart_tx_multiple_bytes(dut):
    """Write string via AXI, verify on UART TX"""
    
@cocotb.test()
async def test_uart_tx_status_polling(dut):
    """Verify TX empty/full status bits update correctly"""
    
@cocotb.test()
async def test_uart_tx_fifo_full_handling(dut):
    """Fill TX FIFO and verify full flag behavior"""
```

### Day 13-14: UART RX Path Tests

**File:** `sub_system/test_uart_rx.py`

```python
@cocotb.test()
async def test_uart_rx_single_byte(dut):
    """Send byte on UART RX pin, read via AXI"""
    
@cocotb.test()
async def test_uart_rx_multiple_bytes(dut):
    """Send string on UART RX pin, read all via AXI"""
    
@cocotb.test()
async def test_uart_rx_status_bits(dut):
    """Verify RX not empty flag updates correctly"""
    
@cocotb.test()
async def test_uart_rx_fifo_behavior(dut):
    """Test RX FIFO filling and draining"""
```

### Day 15-16: Configuration Tests

**File:** `sub_system/test_uart_config.py`

```python
@cocotb.test()
async def test_uart_baud_rate_9600(dut):
    """Test 9600 baud"""
    
@cocotb.test()
async def test_uart_baud_rate_115200(dut):
    """Test 115200 baud (default)"""
    
@cocotb.test()
async def test_uart_baud_rate_921600(dut):
    """Test high speed 921600 baud"""
    
@cocotb.test()
async def test_uart_parity_none(dut):
    """Test no parity mode"""
    
@cocotb.test()
async def test_uart_parity_odd(dut):
    """Test odd parity mode"""
    
@cocotb.test()
async def test_uart_parity_even(dut):
    """Test even parity mode"""
    
@cocotb.test()
async def test_uart_char_size_5bit(dut):
    """Test 5-bit character size"""
    
@cocotb.test()
async def test_uart_char_size_8bit(dut):
    """Test 8-bit character size (default)"""
```

### Day 17-18: Bidirectional & Concurrent Tests

**File:** `sub_system/test_uart_concurrent.py`

```python
@cocotb.test()
async def test_uart_simultaneous_tx_rx(dut):
    """Send and receive at same time (full duplex)"""
    
@cocotb.test()
async def test_uart_back_to_back_writes(dut):
    """Stress test: rapid AXI writes to TX"""
    
@cocotb.test()
async def test_uart_back_to_back_reads(dut):
    """Stress test: rapid AXI reads from RX"""
```

### Deliverable
✅ 10-15 passing tests covering basic functionality  
✅ TX path fully tested  
✅ RX path fully tested  
✅ Configuration options validated

---

## Phase 4: Advanced Tests (Week 5)

### Objective
Error conditions, interrupts, corner cases

### Day 19-20: Error Injection Tests

**File:** `sub_system/test_uart_errors.py`

```python
@cocotb.test()
async def test_uart_parity_error_detection(dut):
    """Send wrong parity, check error bit in status"""
    
@cocotb.test()
async def test_uart_frame_error_detection(dut):
    """Send invalid stop bit, check error bit"""
    
@cocotb.test()
async def test_uart_overrun_condition(dut):
    """Overflow RX FIFO, check overrun bit"""
    
@cocotb.test()
async def test_uart_break_condition(dut):
    """Send break signal, check break error bit"""
```

### Day 21-22: Interrupt Testing

**File:** `sub_system/test_uart_interrupts.py`

```python
@cocotb.test()
async def test_uart_tx_complete_interrupt(dut):
    """Enable TX done interrupt, verify assertion"""
    
@cocotb.test()
async def test_uart_rx_not_empty_interrupt(dut):
    """Enable RX interrupt, verify on data arrival"""
    
@cocotb.test()
async def test_uart_rx_threshold_interrupt(dut):
    """Fill FIFO to 80%, check threshold interrupt"""
    
@cocotb.test()
async def test_uart_error_interrupts(dut):
    """Enable error interrupts, trigger and verify"""
    
@cocotb.test()
async def test_uart_interrupt_enable_disable(dut):
    """Test interrupt masking functionality"""
```

### Day 23: Random/Constrained Random Tests

**File:** `sub_system/test_uart_random.py`

```python
@cocotb.test()
async def test_uart_random_traffic(dut):
    """100 iterations of random data/config"""
    # Random: baud, parity, character size, data patterns
    
@cocotb.test()
async def test_uart_random_stress(dut):
    """Long-running stress test with random stimulus"""
```

### Deliverable
✅ 8-10 tests covering error cases and interrupts  
✅ All interrupt conditions tested  
✅ Error detection verified

---

## Phase 5: Polish & Documentation (Week 6)

### Objective
Production-ready deliverable

### Day 24-25: Code Cleanup & Refactoring
- [ ] Refactor common code into utilities
- [ ] Add comprehensive logging to all tests
- [ ] Remove magic numbers, use named constants
- [ ] Add docstrings to all functions/classes
- [ ] Code review and cleanup

### Day 26-27: Coverage Analysis
- [ ] Create functional coverage checklist
- [ ] Track coverage per test
- [ ] Identify coverage gaps
- [ ] Add tests for missing scenarios
- [ ] Generate coverage matrix

### Day 28-29: Documentation
- [ ] Test plan document (this file!)
- [ ] Feature coverage matrix
- [ ] Known issues/limitations
- [ ] Setup/run instructions (README.md)
- [ ] Architecture diagram
- [ ] Results summary

### Day 30: Final Review & Regression
- [ ] Run full regression suite
- [ ] Fix any failing tests
- [ ] Generate final coverage report
- [ ] Prepare presentation/demo
- [ ] Archive results and waveforms

### Deliverable
✅ Complete test suite (25-30 tests)  
✅ Comprehensive documentation  
✅ Coverage report  
✅ Clean, maintainable code

---

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| Phase 1 | Week 1 (5 days) | Setup & Learning |
| Phase 2 | Week 2 (5 days) | Infrastructure |
| Phase 3 | Week 3-4 (10 days) | Core Tests |
| Phase 4 | Week 5 (5 days) | Advanced Tests |
| Phase 5 | Week 6 (5 days) | Polish & Documentation |
| **Total** | **30 working days** | **6 weeks** |

### Milestone Checkpoints

**End of Week 1:** First passing test  
**End of Week 2:** Reusable testbench framework  
**End of Week 4:** Core functionality verified  
**End of Week 5:** All features tested  
**End of Week 6:** Project complete

---

## Risk Mitigation

### Potential Blockers
1. **RTL bugs discovered** → Document and work around if possible
2. **Simulator issues** → Switch to alternate simulator
3. **VIP compatibility** → Debug VIP configuration
4. **Understanding gaps** → Allocate extra learning time

### Buffer Strategy
- Each phase has 1-2 day buffer built in
- Can compress Phase 5 if needed
- Prioritize core tests over advanced features if time-constrained

---

## Next Steps

1. Review this plan
2. Set up development environment (Day 1-2)
3. Start Phase 1 execution
4. Track progress against this plan daily
5. Update plan as needed based on actual progress
