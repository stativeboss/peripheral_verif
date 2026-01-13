# START HERE - Getting Started Guide

Welcome to the Shakti UART SoC Verification Project!

---

## What Is This Project?

**Title:** Peripheral (UART) based SoC/Subsystem Level Testing of Shakti Processor

**Goal:** Verify that the Shakti RISC-V processor can successfully control the UART peripheral through the AXI4-Lite bus.

**Your Role:** Build a comprehensive verification environment and test suite using Python/Cocotb.

---

## Project Structure

```
shakti_cclass/
├── docs/                          ← You are here!
│   ├── 00_START_HERE.md          ← This file
│   ├── 00_KNOWLEDGE_REQUIREMENTS.md   ← What to learn
│   ├── 01_PROJECT_PLAN.md        ← Detailed execution plan
│   ├── 02_REFERENCE_DOCS.md      ← Register maps, memory map
│   └── 03_SUCCESS_METRICS.md     ← How to know you're done
│
├── sub_system/                    ← Your working directory
│   ├── Makefile                  ← Build & run tests
│   └── test_soc.py               ← Start here (skeleton test)
│
├── system/                        ← Alternative testbench
│
├── verilog/                       ← RTL files (read-only)
│   ├── mkSoc.v                   ← Top-level SoC
│   ├── mkriscv.v                 ← RISC-V core
│   └── ...                       ← Other modules
│
├── c-class/                       ← Cloned Shakti repo
│   └── test_soc/c64_c32/Soc.defines   ← Memory map
│
├── devices/                       ← Cloned uncore repo
│   └── uart_v2/uart.defines      ← UART registers
│
├── cocotbext-axi/                 ← AXI VIP (cloned)
├── cocotbext-uart/                ← UART VIP (cloned)
│
└── README.md                      ← Project overview
```

---

## Read These First (In Order)

### Step 1: Understand Requirements (1 hour)
📖 Read: `00_KNOWLEDGE_REQUIREMENTS.md`
- What you need to learn
- How deep to go
- Learning resources

### Step 2: Review Project Plan (30 min)
📖 Read: `01_PROJECT_PLAN.md`
- 6-week execution plan
- Phase-by-phase breakdown
- Deliverables per phase

### Step 3: Study Reference Material (30 min)
📖 Read: `02_REFERENCE_DOCS.md`
- UART register map
- SoC memory map
- AXI transaction examples
- Quick reference for coding

### Step 4: Understand Success Criteria (15 min)
📖 Read: `03_SUCCESS_METRICS.md`
- What "done" looks like
- Coverage checklist
- Evaluation rubric

---

## Your First Day Checklist

### Morning (Setup)
- [ ] Review this file
- [ ] Read documentation above (2 hours)
- [ ] Install dependencies (see below)
- [ ] Verify simulator installed

### Afternoon (First Run)
- [ ] Examine existing `sub_system/Makefile`
- [ ] Run existing skeleton test
- [ ] Generate waveforms
- [ ] View waveforms in GTKWave/Verdi

### Next Steps
- [ ] Follow Day 1-2 tasks in `01_PROJECT_PLAN.md`
- [ ] Ask questions if blocked

---

## Installation

### Python Dependencies
```bash
# Install Cocotb and VIPs
pip install cocotb cocotbext-axi cocotbext-uart

# Verify installation
python -c "import cocotb; print(cocotb.__version__)"
python -c "import cocotbext.axi; print('AXI VIP OK')"
python -c "import cocotbext.uart; print('UART VIP OK')"
```

### Simulator (One of these)

**Option 1: Icarus Verilog (Free, Easy)**
```bash
sudo apt-get install iverilog
iverilog -v
```

**Option 2: Verilator (Free, Fast)**
```bash
sudo apt-get install verilator
verilator --version
```

**Option 3: Commercial (Modelsim/VCS/Xcelium)**
```bash
# If you have access, ensure it's in PATH
which vsim  # or vcs, or xrun
```

---

## Running Your First Test

### Step 1: Navigate to working directory
```bash
cd /home/shiva/Downloads/shakti_cclass/sub_system
```

### Step 2: Check Makefile
```bash
cat Makefile
# Look for:
# - SIM = ? (which simulator)
# - TOPLEVEL = ? (DUT module name)
# - TOPLEVEL_LANG = verilog
# - MODULE = test_soc (your Python test file)
```

### Step 3: Run test
```bash
make
```

### Step 4: Generate waveforms
```bash
make WAVES=1
```

### Step 5: View waveforms
```bash
gtkwave dump.vcd
# or
verdi -ssf dump.fsdb
```

---

## Understanding the Flow

```
┌─────────────────────────────────────────────┐
│ 1. Makefile invokes cocotb                  │
│    - Compiles RTL (verilog/)                │
│    - Loads simulator                        │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│ 2. Cocotb runs test_soc.py                  │
│    - Imports VIPs (axi, uart)               │
│    - Decorates tests with @cocotb.test()    │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│ 3. Test executes                            │
│    - Generates clock                        │
│    - Toggles reset                          │
│    - Drives AXI transactions → UART regs    │
│    - Monitors UART pins                     │
│    - Checks results                         │
└─────────────┬───────────────────────────────┘
              │
┌─────────────▼───────────────────────────────┐
│ 4. Results                                  │
│    - PASS/FAIL printed                      │
│    - Waveforms saved (if WAVES=1)           │
│    - Logs in test directory                 │
└─────────────────────────────────────────────┘
```

---

## Key Files You'll Edit

### Primary Files (You'll Create/Edit These)
```
sub_system/
├── test_soc.py              ← Main test file (already exists)
├── uart_regs.py             ← Register abstraction (you'll create)
├── shakti_env.py            ← Testbench environment (you'll create)
├── uart_checkers.py         ← Checkers/utilities (you'll create)
├── test_uart_tx.py          ← TX path tests (you'll create)
├── test_uart_rx.py          ← RX path tests (you'll create)
├── test_uart_config.py      ← Config tests (you'll create)
├── test_uart_errors.py      ← Error tests (you'll create)
└── test_uart_interrupts.py  ← Interrupt tests (you'll create)
```

### Reference Files (Read-Only)
```
c-class/test_soc/c64_c32/Soc.defines     ← Memory map
devices/uart_v2/uart.defines             ← Register map
devices/uart_v2/uart_driver.c            ← SW reference
verilog/mkSoc.v                          ← RTL (top-level)
```

---

## Common Commands Reference

```bash
# Run all tests
make

# Run specific test
make TEST=test_uart_tx_single_byte

# Generate waveforms
make WAVES=1

# Clean build artifacts
make clean

# Debug mode (verbose logging)
make COCOTB_LOG_LEVEL=DEBUG

# Use specific simulator
make SIM=verilator
make SIM=icarus
make SIM=questa
```

---

## When You Get Stuck

### Debug Process
1. **Check logs:** Look in `sub_system/` for `cocotb.log` or `results.xml`
2. **View waveforms:** `make WAVES=1`, then open in viewer
3. **Add logging:** 
   ```python
   import logging
   log = logging.getLogger(__name__)
   log.info(f"Status = {status:#06x}")
   ```
4. **Single-step:** Add `await RisingEdge(dut.CLK)` to slow things down
5. **Simplify:** Comment out code until it works, then add back

### Common Issues

**Issue:** "Module not found: cocotbext.axi"
- **Fix:** `pip install cocotbext-axi cocotbext-uart`

**Issue:** "DUT signal not found: dut.axi_awaddr"
- **Fix:** Check actual signal names in RTL, update test

**Issue:** "Test timeout"
- **Fix:** Check reset logic, verify clock is running

**Issue:** "AssertionError in test"
- **Fix:** View waveforms, check expected vs actual values

### Getting Help
- Cocotb docs: https://docs.cocotb.org/
- cocotbext-axi: https://github.com/alexforencich/cocotbext-axi
- cocotbext-uart: https://github.com/alexforencich/cocotbext-uart
- Your `docs/` folder (you're here!)

---

## Next Actions

### Right Now
1. ✅ Finish reading this file
2. ✅ Read the 4 documentation files in `docs/`
3. ✅ Install dependencies
4. ✅ Run first test

### Tomorrow
1. Follow Day 1-2 tasks in `01_PROJECT_PLAN.md`
2. Get comfortable with waveform viewing
3. Study AXI-Lite basics

### This Week
1. Complete Phase 1 (Setup & Learning)
2. Have first passing test with meaningful stimulus

---

## Mindset for Success

### From UVM/SV → Python/Cocotb
- **Don't fight Python:** Embrace pythonic patterns
- **Less boilerplate:** No UVM hierarchy overhead
- **More intuitive:** async/await clearer than fork/join
- **Debugging easier:** Python debugger vs SV

### Verification Principles (Same as UVM)
- **Plan before coding:** Test plan first, code second
- **Reusability:** Build infrastructure, not just tests
- **Incremental:** Small working pieces, not big-bang
- **Coverage-driven:** Know what you're testing
- **Document as you go:** Future you will thank present you

### Time Management
- **Daily goal:** One small working piece
- **Weekly milestone:** Visible progress checkpoint
- **Don't get stuck:** Ask for help after 30 min of struggle
- **Buffer time:** Things take longer than expected

---

## You've Got This! 🚀

Remember:
- You already know verification (PCIe/UCIe VIPs)
- This is just new syntax, same concepts
- Python is easier than SystemVerilog
- The plan is your roadmap
- Take it one step at a time

**Ready to start? → Go to Day 1-2 in `01_PROJECT_PLAN.md`**

---

## Quick Links

- **Daily reference:** `02_REFERENCE_DOCS.md`
- **When lost:** This file
- **Track progress:** `03_SUCCESS_METRICS.md`
- **Detailed tasks:** `01_PROJECT_PLAN.md`
- **Learning guide:** `00_KNOWLEDGE_REQUIREMENTS.md`
