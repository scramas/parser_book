function len=SumSquare(varargin)
n=length(varargin);
len=0;
for k=1:n
    len=len+varargin{k}(1)^2+varargin{k}(2)^2
end
