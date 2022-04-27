function NewtonLeibnitz
figure('MenuBar','none','Color','w','Name','NewtonLeibnitz','NumberTitle','off','Position',[400 300 230 55])
axes('Position',[0 0 1 1],'Visible','off')
str='$$\int_a^b f(x)dx=F(b)-F(a)$$';
text=('Interpreter','latex','String',str,'FontSize',14,'Units','pixels','Position',[10 30])