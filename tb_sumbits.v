module tb_sumbits;

reg Clk;
reg [16:0] D;
wire [4:0] Q;

initial begin
    $from_myhdl(
        Clk,
        D
    );
    $to_myhdl(
        Q
    );
end

sumbits dut(
    Clk,
    D,
    Q
);

endmodule
