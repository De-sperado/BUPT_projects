LIBRARY IEEE;
USE IEEE.STD_LOGIC_1164.ALL;
USE IEEE.STD_LOGIC_Arith.ALL;
USE IEEE.STD_LOGIC_Unsigned.ALL;

ENTITY pipelining IS
PORT (SWB       : IN   STD_LOGIC; 	--模式开关值
      SWA	     	: IN   STD_LOGIC;		--模式开关值
	   	SWC		 		: IN   STD_LOGIC;		--模式开关值
	   	clr      	: IN   STD_LOGIC;		--复位信号，低电平有效
      C	     		: IN   STD_LOGIC;		--进位标志 
	   	Z	     		: IN   STD_LOGIC;		--结果为零标志
	   	IRH	  	 	: IN   STD_LOGIC_VECTOR(3 DOWNTO 0); --IR7,IR6,IR5,IR4，指令操作码
	   	T3	 	 		: IN   STD_LOGIC;		--T3时钟
			W1	 	 		: IN   STD_LOGIC;		--W1节拍输出
			W2	     	: IN   STD_LOGIC;		--W2节拍输出
			W3   	 		: IN   STD_LOGIC;		--W3节拍输出
			SELCTL	 	: OUT   STD_LOGIC;	--为1时为控制台操作
			ABUS      : OUT   STD_LOGIC;	--为1时运算器结果送数据总线
			M         : OUT   STD_LOGIC;	--运算模式
			S         : OUT   STD_LOGIC_VECTOR(3 DOWNTO 0); --S3,S2,S1,S0	   
			SEL1      : OUT   STD_LOGIC; 		--用来选择寄存器
			SEL0		 	: OUT   STD_LOGIC;
			SEL2		 	: OUT   STD_LOGIC;
			SEL3	    : OUT   STD_LOGIC;
			DRW     	: OUT   STD_LOGIC;		--为1时允许给累加器和第一、第二、第三寄存器加载
			SBUS      : OUT   STD_LOGIC;		--为1时允许数据开关值送数据总线
			LIR       : OUT   STD_LOGIC;		--为1时将从存储器读出的指令送指令寄存器
			MBUS      : OUT   STD_LOGIC;		--为1时将从存储器读出的数据送数据总线
			MEMW      : OUT   STD_LOGIC;		--为1时在T2写存储器，为0时读存储器
			LAR       : OUT   STD_LOGIC;		--为1时在T2的上升沿将数据总线上的地址打入地址寄存器
			ARINC     : OUT   STD_LOGIC;		--为1时在T2的上升沿地址寄存器加1
			LPC       : OUT   STD_LOGIC; 		--为1时在T2的上升沿将数据总线上的数据打入程序计数器PC
			PCINC     : OUT   STD_LOGIC;		--为1时在T2的上升沿程序计数器加1
			PCADD	 		: OUT	 	STD_LOGIC;		--PC加某一个值
			CIN		 		: OUT	 	STD_LOGIC;		--进位
			LONG		 	: OUT   STD_LOGIC;		--3拍
			SHORT     : OUT   STD_LOGIC;		--单拍
			STOP		 	: BUFFER STD_LOGIC;		--观察使用
			LDC		 		: OUT   STD_LOGIC;		--为1时T3的上升沿保存进位
			LDZ       : OUT   STD_LOGIC			--为1时T3的上升沿保存结果为0标志	
	);
END pipelining;

ARCHITECTURE behavior OF pipelining IS 
SIGNAL ST0: STD_LOGIC;  --控制它转换
SIGNAL SST0: STD_LOGIC;
SIGNAL SWCBA: STD_LOGIC_VECTOR(2 DOWNTO 0);

BEGIN
		
SWCBA <= SWC & SWB & SWA;
ST0_PROC: PROCESS(clr, T3)
	BEGIN
		IF clr = '0' THEN
			ST0 <= '0';
		ELSIF T3'EVENT AND T3 = '0' THEN
			IF SST0 = '1' THEN
				ST0 <= '1';
				END IF;
			IF ST0='1' AND W2='1'AND SWCBA="100" THEN
			ST0<='0';
			END IF;
		END IF;
	END PROCESS;


OUT_SIG_PROC: PROCESS( SWCBA, IRH, W1, W2, W3, ST0, C, Z) 
  BEGIN
        --给信号设置默认值
   SHORT 	<= '0';
   LONG		<= '0';
   CIN		<= '0';
   SELCTL   <= '0';
   ABUS     <= '0';
   SBUS	    <= '0';
   MBUS		<= '0';
   M        <= '0';
   S        <= "0000";
   SEL3		<= '0';
   SEL2		<= '0';
   SEL1     <= '0'; 
   SEL0		<= '0';
   DRW      <= '0';
   SBUS    <= '0';
   LIR      <= '0';
   MEMW     <= '0';
   LAR      <= '0';
   PCADD	<='0';
   ARINC    <= '0';
   LPC      <= '0';
   LDZ		<= '0';
   LDC		<= '0';
   STOP	    <= '0';
   PCINC	<= '0';
   SST0	<= '0';
   CASE SWCBA IS
		WHEN "000" =>   --执行指令
			SBUS	<=(NOT ST0)AND W1;
			LPC		<=(NOT ST0)AND W1;
			SHORT	<=(NOT ST0)AND W1;
			SST0	<=(NOT ST0)AND W1;
      CASE IRH IS  --指令处理
              
				WHEN "0000"=>
				LIR<=W1;
				PCINC<=W1;
				SHORT<=W1;

				WHEN "0001" =>	--ADD
				LIR <= W1;  
				PCINC <= W1;
				SHORT<=W1;
				S <= "1001";
				CIN <= W1;
				ABUS <= W1;
				DRW <= W1;
				LDC <= W1;
				LDZ <= W1;

				WHEN "0010" =>	--SUB
				LIR <= W1;  
				PCINC <= W1;
				SHORT<=W1;
				S <= "0110";
				ABUS <= W1;
				DRW <= W1;
				LDC <= W1;
				LDZ <= W1;

				WHEN "0011" =>	--AND
				LIR <= W1;  
				PCINC <= W1;
				SHORT<=W1;
				S <= "1011";
				M<=W1;
				ABUS <= W1;
				DRW <= W1;
				LDZ <= W1;
				
			  WHEN "0101" => --LD
				LAR <= W1;  --出现问题，划分成了3排
				M <= W1;
				S <= "1010";
				ABUS <= W1;
				LIR <= W3;
				PCINC<=W3;
				LONG<='1';
				DRW <= W2;
				MBUS <= W2;

				WHEN "1100"=>   --XOR(new)
				M<=W1;
				S<="0110";
				ABUS<=W1;
				DRW<=W1;
				LDC<=W1;
				LDZ<=W1;
			
				WHEN "0000"=>   --NOT(new)
				M<=W1;
				S<="0000";
				ABUS<=W1;
				DRW<=W1;
				LDC<=W1;
				LDZ<=W1;

				WHEN "1101"=>   --DEC(new)
				CIN<=W1;
				S<="1111";
				ABUS<=W1;
				DRW<=W1;
				LDC<=W1;
				LDZ<=W1;
				
			  WHEN "0110" =>	--ST
				LAR <= W1;
				PCINC <= W2;
				M <= W2 OR W1;
				if W1 = '1' then
					S <= "1111";
				end if;
				if W2 = '1' then 
					S <= "1010";
				end if;
				ABUS <= W2 OR W1;
				LIR <= W2;
			    MEMW <= W2;
				
			  WHEN "0100" =>	--INC
				LIR <= W2;
				PCINC <= W2;
				S <= "0000";
				ABUS <= W1;
				DRW <= W1;
				LDZ <= W1;
				LDC <= W1;
				
			  WHEN "1000" =>	--JZ
			  LIR <= (W1 AND (NOT Z)) OR W3;--划分成了三拍
				PCINC <= (W1 AND (NOT Z)) OR W3;
				PCADD <= W2 AND Z;
				SHORT<=NOT Z;
				LONG<=Z;
				
			  WHEN "0111" =>	--JC
				LIR <= ((NOT C)AND W1) OR W2;  --取指
				PCINC <= ((NOT Z)AND W1) OR W2;
				PCADD <= W1 AND C;
				SHORT<=(NOT C)AND W1;
								
			  WHEN "1001" =>	--JMP
		   	LIR <= W2;
				PCINC <= W2;
				LPC<=W1;
		    S <= "1111";
		    M <= W1;
		    ABUS <= W1;
				
			  WHEN "1110" =>	--STP
				STOP <= W1;

				WHEN "1010" => --OUT
				M<=W1;
				S<="1010";
				ABUS<=W1;
				LIR<=W1;
				PCINC<=W1;
				--SHORT<=W1;
			
			  WHEN OTHERS =>
				LIR <= W1;
				PCINC <= W1;
		          
					
		   END CASE;
		
		WHEN "001" =>	--写存储器
		  SELCTL <= '1';
	  	SST0 <= NOT ST0 AND W1;
			SBUS <= W1;
	  	STOP <= W1;
			LAR  <= NOT ST0 AND W1;
			SHORT <= W1;
			MEMW <= ST0 AND W1;
			ARINC <= ST0 AND W1;
		   
			
		WHEN "010" =>	--读存储器
			SBUS <= NOT ST0 AND W1;
			LAR <= NOT ST0 AND W1;
			STOP <= W1;
			SST0 <= NOT ST0 AND W1;
			SHORT <= W1 OR W2;
			SELCTL <= '1';
			MBUS <= ST0 AND W1;
			ARINC <= W1 AND ST0;
		
		WHEN "011" =>	--读寄存器
		  SELCTL <= '1';
	  	STOP <= W1 OR W2;
			SEL3 <= W2;
			SEL2 <= W1 AND W2;
			SEL1<= W2;
			SEL0 <= W1 OR W2;
		  		 	
		WHEN "100" =>  --写寄存器
			SELCTL	 <= '1';--不会反复写R2，R3
	  	SST0 <= W2; 
			SBUS <= W1 OR W2;
	  	STOP <= W1 OR W2;
			DRW <= W1 OR W2;
			SEL3 <= (ST0 AND W1) OR (ST0 AND W2);
			SEL2 <= W2;
			SEL1<= (NOT ST0 AND	W1) OR (ST0 AND W2);
			SEL0 <= W1; 
		  
		WHEN OTHERS =>
			NULL;
	  END CASE;
		
	END PROCESS;
		
END behavior;