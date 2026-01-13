# See LICENSE for license details.

#include "riscv_test.h"
#include "test_macros.h"

RVTEST_RV64M
RVTEST_CODE_BEGIN


uart:

 # clock enable
 li x5,0x11300

 

 #Baud reg
 li x6,0x5
 sh x6,0(x5)
 fence

 #read status reg
 lh x7,0xc(x5)

  #interrupt
 li x6,0x3ff
 sh x6,0x18(x5)
 fence

 #data_tx reg
 li x6,0x55
 sw x6,0x04(x5)
 fence
  
 #write ctrl reg
 li x6,0x4112
 sw x6,0x14(x5)
 fence



#  wait for 100 clk
 li x9,0
loop:
 add x9,x9,1
 li x8 ,450
 bne x8,x9,loop


  TEST_PASSFAIL
RVTEST_CODE_END

  .data
RVTEST_DATA_BEGIN

  TEST_DATA

RVTEST_DATA_END
