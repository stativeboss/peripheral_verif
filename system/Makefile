SIM ?= icarus
TOPLEVEL_LANG ?= verilog

PWD=$(shell pwd)

LIB=$(shell dirname $(shell which bsc))

COMPILE_ARGS += -I $(PWD)/../verilog -I $(LIB)/../lib/Verilog

export PYTHONPATH:=$(PWD):$(PYTHONPATH)

VERILOG_SOURCES=$(PWD)/../verilog/*.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/BRAM1Load.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/BRAM2BELoad.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/ClockInverter.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/Counter.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/FIFO1.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/FIFO2.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/FIFOL1.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/MakeClock.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/MakeReset0.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/RegFile.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/ResetEither.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/RevertReg.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/SizedFIFO.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/SyncFIFO1.v
VERILOG_SOURCES += $(LIB)/../lib/Verilog/SyncReset0.v

TOPLEVEL = mkTbSoc
MODULE   := test_soc


include $(shell cocotb-config --makefiles)/Makefile.sim


# Makefile for compiling and running RISC-V test on Spike

ifndef TEST
$(error TEST is not set. Please run: make run TEST=/path/to/test_file.S)
endif

# Variables (override TEST on the command line)
# TEST      ?= test.S
FILENAME  := $(basename $(notdir $(TEST)))
TEST_HOME := $(CURDIR)
OUT_DIR   := $(CURDIR)

# Tools
GCC       := riscv64-unknown-elf-gcc
OBJDUMP   := riscv64-unknown-elf-objdump
SPIKE     := spike
TIMEOUT   := timeout --foreground 3s

# Compiler/linker options
CFLAGS    := -march=rv64imafdczicsr_zifencei -mabi=lp64 -static -mcmodel=medany -fvisibility=hidden \
             -nostdlib -nostartfiles -DENTROPY=0x9629af2 -std=gnu99 -O2 \
             -I$(TEST_HOME)/env -T$(TEST_HOME)/env/link.ld

compile: $(TEST).S
	mkdir -p $(OUT_DIR)
	rm -rf $(OUT_DIR)/*.elf $(OUT_DIR)/*.disass $(OUT_DIR)/code.mem
	@echo "-------------------------------------------------------------------------"
	@echo "Compiling $(TEST)"
	@echo "-------------------------------------------------------------------------"
	$(GCC) $(CFLAGS) $< -o $(OUT_DIR)/$(TEST).elf
	@echo "-------------------------------------------------------------------------"
	@echo "Disassembly Generation"
	@echo "-------------------------------------------------------------------------"
	$(OBJDUMP) --disassemble-all --disassemble-zeroes \
		--section=.text --section=.text.startup --section=.text.init --section=.data \
		$(OUT_DIR)/$(TEST).elf > $(OUT_DIR)/$(TEST).disass
	@echo "-------------------------------------------------------------------------"
	elf2hex  8  4194304  $(OUT_DIR)/$(TEST).elf 2147483648 > $(OUT_DIR)/code.mem
	@echo "-------------------------------------------------------------------------"
	@echo "DONE"
	@echo "-------------------------------------------------------------------------"


dut: $(PWD)/code.mem
	@echo "-------------------------------------------------------------------------"
	@echo "Running Test on C-CLASS "
	@echo "-------------------------------------------------------------------------"
	cp sim_build/sim.vvp .
	PYGPI_PYTHON_BIN=$(shell cocotb-config --python-bin) COCOTB_TEST_MODULES=test_soc \
     COCOTB_TESTCASE= COCOTB_TEST_FILTER= \
     COCOTB_TOPLEVEL=mkTbSoc TOPLEVEL_LANG=verilog  \
     /tools/iverilog_build/bin/vvp -M $(shell cocotb-config --lib-dir) -m libcocotbvpi_icarus  \
     ./sim.vvp +rtldump
	@echo "-------------------------------------------------------------------------"
	@echo "TEST COMPLETED"
	@echo "-------------------------------------------------------------------------"

clean_all: clean
	rm -rf sim.vvp sim_build rtl.dump signature app_log 
	rm -rf $(OUT_DIR)/*.elf $(OUT_DIR)/*.disass $(OUT_DIR)/code.mem

