'''
Created on 15 Jul 2015

@author: Josy
'''


import myhdl
import hdlutils


def sumbits(Clk, Reset, D, Q):
    ''' a recursive pipelined implementation'''
    LWIDTH_D = len(D)

    sbs = []

    if LWIDTH_D > 2:
        # recurse by splitting things up
        LWIDTH_L = LWIDTH_D - LWIDTH_D / 2
        dupper, dlower = [myhdl.Signal(myhdl.intbv(0)[LWIDTH_L:]) for _ in range(2)]
        lql, lqu = [myhdl.Signal(myhdl.intbv(0)[hdlutils.widthr(LWIDTH_L):]) for _ in range(2)]
#         supper = sumbits(Clk, Reset, dupper, lqu)
#         slower = sumbits(Clk, Reset, dlower, lql)
        sbs.append(sumbits(Clk, Reset, dupper, lqu))
        sbs.append(sumbits(Clk, Reset, dlower, lql))

        @myhdl.always_comb
        def split():
            ''' this will expand on the left in case the input data-size is uneven '''
            dupper.next = D[: LWIDTH_L]
            dlower.next = D[LWIDTH_L:]
        sbs.append(split)

        @myhdl.always_seq(Clk.posedge, Reset)
        def rtlr():
            ''' the result is the sum of the previous branches '''
            Q.next = lqu + lql
        sbs.append(rtlr)

#         return supper, slower, split, rtlr

    # know when to stop
    else:
        @myhdl.always_seq(Clk.posedge, Reset)
        def rtl2():
            ''' the result is the sum of the two (terminal) leaves '''
            Q.next = D[1] + D[0]
        sbs.append(rtl2)
#         return rtl2

    return sbs

def tb_sumbits():
    '''' test-bench for the sumbits() implementation '''
    Clk = myhdl.Signal(bool(0))
    Reset = myhdl.ResetSignal(0, active=1, async=True)
    D = myhdl.Signal(myhdl.intbv(0)[WIDTH_D:])
    Q = myhdl.Signal(myhdl.intbv(0)[WIDTH_Q:])

    dut = sumbits(Clk, Reset, D, Q)

    tCK = 10
    ClkCount = myhdl.Signal(myhdl.intbv(0)[8:])

    @myhdl.instance
    def clkgen():
        yield hdlutils.genClk(Clk, tCK, ClkCount)

    @myhdl.instance
    def resetgen():
        yield hdlutils.genReset(Clk, tCK, Reset)

    @myhdl.instance
    def stimulusin():
        yield hdlutils.delayclks(Clk, tCK, 5)
        D.next = 0x13
        yield hdlutils.delayclks(Clk, tCK, 1)
        D.next = 0x01
        yield hdlutils.delayclks(Clk, tCK, 1)
        D.next = 0x02
        yield hdlutils.delayclks(Clk, tCK, 1)
        D.next = 0x03
        yield hdlutils.delayclks(Clk, tCK, 5)

        raise myhdl.StopSimulation

    return dut, clkgen, resetgen, stimulusin


def convert():
    Clk = myhdl.Signal(bool(0))
#     Reset = myhdl.ResetSignal(0, active=1, async=True)
    Reset = None
    D = myhdl.Signal(myhdl.intbv(0)[WIDTH_D:])
    Q = myhdl.Signal(myhdl.intbv(0)[WIDTH_Q:])

    myhdl.toVHDL(sumbits, Clk, Reset, D, Q)
    myhdl.toVerilog(sumbits, Clk, Reset, D, Q)


if __name__ == '__main__':

    WIDTH_D = 17
    WIDTH_Q = hdlutils.widthr(WIDTH_D)

    hdlutils.simulate(1000, tb_sumbits)
    convert()
