function my_sign
x=5;
if x>=0 && x<=2
    disp(1);
elseif (x>=-5 && x<=5) &&(x~=0 && x~=1)
    disp(-1);
else
    disp(0); 
end