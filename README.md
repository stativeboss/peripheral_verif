# Build and Run tests on C-Class

## Sub-System
```
cd sub_system
make
make clean
```

## System
```
cd system
export TEST=add
make compile; make; make dut
make clean_all

## uart test
cd system
export TEST=uart64
make compile; make; make dut
make clean_all
```

