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
