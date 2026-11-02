"""Sinh bảng ô nhập trực tiếp từ GUI và chương BPTT theo từng mô hình.

Chỉ sinh tài liệu; không thay đổi thuật toán của ứng dụng.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from pps.gui import TOOLS,fields
OUT=Path(__file__).resolve().parent
CH=OUT.parent/'chapters'


def tex(s):
    out=''
    for c in str(s):
        out+= {'\\':r'\textbackslash{}','_':r'\_','&':r'\&','%':r'\%','#':r'\#','$':r'\$',
                '{':r'\{','}':r'\}','^':r'\textasciicircum{}','~':r'\textasciitilde{}'}.get(c,c)
        if c in ',;/':out+=r'\allowbreak{}'
    return out


GROUPS={'poly':'Nội suy đa thức','inverse':'Nội suy ngược','spline':'Spline','ls':'Bình phương tối thiểu',
    'calculus':'Tích phân','ode':'Phương trình vi phân','bvp':'Bài toán biên','nodes':'Chọn mốc','horner':'Đạo hàm & Horner'}
for slug,group in GROUPS.items():
    methods=TOOLS[group][0]
    forms=[fields(group,m) for m in methods]
    shared=[f for f in forms[0] if all(f in form for form in forms[1:])]
    lines=[r'\subsection*{Input: các ô đúng tên trên giao diện}',
      'Bảng này được lấy từ biểu mẫu của tool. Giá trị mặc định là ví dụ nhập, cần thay bằng dữ liệu đề. Hai dãy $x,y$ là bảng dữ liệu riêng bên dưới nếu chức năng dùng bảng.']
    def table(rows):
        if not rows:return
        lines.extend([r'\begin{center}\small\begin{tabular}{@{}p{.32\linewidth}p{.17\linewidth}p{.43\linewidth}@{}}\toprule',
            r'Ô nhập & Khóa JSON & Cách nhập / mặc định\\\midrule'])
        for key,label,default,helptext in rows:
            if group=='Bình phương tối thiểu' and key=='basis':
                helptext=('Nhập đầy đủ các cơ sở, kể cả 1 nếu mô hình có hằng; lựa chọn này không tự thêm cột 1.'
                          if default=='1; x' else 'Chỉ nhập các cơ sở biến thiên trong số mũ; tool tự thêm cột hằng cho biên độ. Không nhập thêm 1.')
            desc=(r'\texttt{'+tex(default)+'}' if default else 'Để trống')
            if helptext:desc+='\n'+r'\par '+tex(helptext)
            lines.append(tex(label)+r' & \texttt{'+tex(key)+'} & '+desc+r'\\[3pt]')
        lines.append(r'\bottomrule\end{tabular}\end{center}')
    if shared:
        lines.append(r'\subsubsection*{Ô chung của các lựa chọn trong nhóm}')
        table(shared)
    profiles={}
    for method,form in zip(methods,forms):
        extra=tuple(f for f in form if f not in shared)
        if extra:profiles.setdefault(extra,[]).append(method)
    for extra,ms in profiles.items():
        lines.append(r'\subsubsection*{Ô riêng: '+tex(' / '.join(ms))+'}')
        table(extra)
    (OUT/f'inputs_{slug}.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')


INTRO=r'''\chapter[Bình phương tối thiểu: từng mô hình]{Tool Bình phương tối thiểu: input, bảng tính và output từng mô hình}
\label{ch:ls}
\section{Chọn mô hình rồi mới chọn phép biến đổi}
Cho $N$ cặp $(x_0,y_0),\ldots,(x_{N-1},y_{N-1})$. Các $x$ có thể lặp: đó là các quan sát riêng. Tool tìm hàm khớp $g$, không ép hàm đi qua mọi điểm.
\input{verification/inputs_ls.tex}
\paragraph{Các bước bấm.} Chọn nhóm Bình phương tối thiểu $\to$ chọn đúng mô hình bên dưới $\to$ nhập $x,y$ $\to$ nhập cơ sở nếu có ô đó $\to$ trọng số nếu đề cho $\to$ điểm dự đoán nếu cần $\to$ Tính kết quả. Mục \emph{Chi tiết} mở các bước của bộ giải thực tế. Chương này tập trung việc lập bài toán và đọc kết quả; không giảng lại Gauss, QR hay SVD.

\section{Mẫu chung cho bài hai tham số sau biến đổi}
\label{sec:ls-general-table}
Mỗi mô hình sẽ quy định cụ thể $U_i,V_i$. Khi có dạng $V\approx c_0+c_1U$, điền bảng dưới đây. Nếu không nhập trọng số thì $w_i=1$ cho mọi dòng.
\begin{center}\small\begin{tabular}{@{}crrrrr@{}}\toprule
Dòng&$w_i$&$w_iU_i$&$w_iV_i$&$w_iU_i^2$&$w_iU_iV_i$\\\midrule
0&$w_0$&$w_0U_0$&$w_0V_0$&$w_0U_0^2$&$w_0U_0V_0$\\
$i$&$w_i$&$w_iU_i$&$w_iV_i$&$w_iU_i^2$&$w_iU_iV_i$\\
$N-1$&$w_{N-1}$&$w_{N-1}U_{N-1}$&$w_{N-1}V_{N-1}$&$w_{N-1}U_{N-1}^2$&$w_{N-1}U_{N-1}V_{N-1}$\\\midrule
Tổng&$S_1$&$S_U$&$S_V$&$S_{UU}$&$S_{UV}$\\\bottomrule
\end{tabular}\end{center}
Hàng $i$ là khuôn để điền mọi hàng giữa, không phải một quan sát bổ sung. Thứ tự: biến đổi $U,V$ $\to$ nhân trọng số và tính các tích $\to$ cộng từng cột:
\begin{align*}
S_1&=\sum_{i=0}^{N-1}w_i=w_0+w_1+\cdots+w_{N-1},\\
S_U&=\sum_{i=0}^{N-1}w_iU_i=w_0U_0+w_1U_1+\cdots+w_{N-1}U_{N-1},\\
S_V&=\sum_{i=0}^{N-1}w_iV_i=w_0V_0+w_1V_1+\cdots+w_{N-1}V_{N-1},\\
S_{UU}&=\sum_{i=0}^{N-1}w_iU_i^2=w_0U_0^2+w_1U_1^2+\cdots+w_{N-1}U_{N-1}^2,\\
S_{UV}&=\sum_{i=0}^{N-1}w_iU_iV_i=w_0U_0V_0+w_1U_1V_1+\cdots+w_{N-1}U_{N-1}V_{N-1}.
\end{align*}
Từ hàng tổng lập hệ
\[
\boxed{\begin{cases}S_1c_0+S_Uc_1=S_V,\\S_Uc_0+S_{UU}c_1=S_{UV}.\end{cases}}
\]
Không trọng số thì $S_1=N$. Nếu $D=S_1S_{UU}-S_U^2\ne0$, kiểm nhanh bằng
\[
c_0=(S_VS_{UU}-S_US_{UV})/D,\quad c_1=(S_1S_{UV}-S_US_V)/D.
\]
Nếu $D=0$ thì tham số chưa duy nhất theo dữ liệu hiệu lực; không gọi là vô nghiệm bình phương tối thiểu. Dòng trọng số 0 vẫn cần dữ liệu và phép biến đổi hợp lệ.

\section{Tuyến tính theo cơ sở: tự chỉ định mọi cột}
\label{sec:ls-linear-tool}
\paragraph{Input.} Chọn \textbf{Tuyến tính theo cơ sở}. Ô cơ sở nhập đầy đủ, ngăn bằng \texttt{;}: đường thẳng \texttt{1;x}, bậc hai \texttt{1;x;x\^{}2}, đi qua gốc \texttt{x}, hoặc \texttt{1;x;cos(x)}. Ở lựa chọn này không tự thêm cột 1.
\paragraph{Bước 1 -- mỗi dòng tạo một hàng.}
\[
g(x)=\sum_{j=0}^{p-1}c_j\phi_j(x)=c_0\phi_0(x)+c_1\phi_1(x)+\cdots+c_{p-1}\phi_{p-1}(x).
\]
\begin{center}\small\begin{tabular}{cllll}\toprule
Dòng&$y_i$&$\phi_0(x_i)$&$\phi_1(x_i)$&$\ldots,\phi_{p-1}(x_i)$\\\midrule
0&$y_0$&$\phi_0(x_0)$&$\phi_1(x_0)$&$\ldots,\phi_{p-1}(x_0)$\\
$i$&$y_i$&$\phi_0(x_i)$&$\phi_1(x_i)$&$\ldots,\phi_{p-1}(x_i)$\\
$N-1$&$y_{N-1}$&$\phi_0(x_{N-1})$&$\phi_1(x_{N-1})$&$\ldots,\phi_{p-1}(x_{N-1})$\\\bottomrule
\end{tabular}\end{center}
Các cột cơ sở tạo $\Phi$; đích $z=(y_0,\ldots,y_{N-1})^T$. Viết $\Phi c\approx z$ vì đây là bài khớp.
\paragraph{Bước 2 -- tính các tích và tổng.}
\begin{align*}
G_{jk}&=\sum_iw_i\phi_j(x_i)\phi_k(x_i)\\
 &=w_0\phi_j(x_0)\phi_k(x_0)+\cdots+w_{N-1}\phi_j(x_{N-1})\phi_k(x_{N-1}),\\
b_j&=\sum_iw_i\phi_j(x_i)y_i=w_0\phi_j(x_0)y_0+\cdots+w_{N-1}\phi_j(x_{N-1})y_{N-1}.
\end{align*}
\paragraph{Bước 3 -- giải bài khớp.} Hệ chuẩn $Gc=b$, trong đó hàng $j$ là
\[
G_{j0}c_0+G_{j1}c_1+\cdots+G_{j,p-1}c_{p-1}=b_j.
\]
Tool dùng đúng bộ giải đã chọn; không giả sử mọi lựa chọn đều khử hệ chuẩn. Đây là quá trình hữu hạn, không có ngưỡng hội tụ tham số cho bài tuyến tính.
\paragraph{Bước 4 -- output.} Vector $(c_0,\ldots,c_{p-1})$ theo thứ tự cơ sở, hàm $g$, dự đoán trên dữ liệu, phần dư, sai số và $g(x_*)$ nếu nhập điểm dự đoán.

\subsection{Đường thẳng và đa thức: viết rõ hệ từ những tổng nào}
Với \texttt{1;x}, dùng bảng hai tham số với $U_i=x_i,V_i=y_i$. Ví dụ $x=(0,1,2,3),y=(1,2,2,4)$:
\[
S_1=4,\quad S_U=0+1+2+3=6,\quad S_V=1+2+2+4=9,
\]
\[
S_{UU}=0^2+1^2+2^2+3^2=14,\quad S_{UV}=0(1)+1(2)+2(2)+3(4)=18.
\]
Hệ $4c_0+6c_1=9$, $6c_0+14c_1=18$ cho $g(x)=0.9+0.9x$.

Với \texttt{1;x;x\^{}2}, bảng cần thêm các tích $w_ix_i^3,w_ix_i^4,w_ix_i^2y_i$. Đặt
\[
M_r=w_0x_0^r+\cdots+w_{N-1}x_{N-1}^r,\quad
T_r=w_0x_0^ry_0+\cdots+w_{N-1}x_{N-1}^ry_{N-1}.
\]
Riêng $M_0=w_0+\cdots+w_{N-1}$, $T_0=w_0y_0+\cdots+w_{N-1}y_{N-1}$, kể cả khi có $x_i=0$. Hệ là
\[
\begin{bmatrix}M_0&M_1&M_2\\M_1&M_2&M_3\\M_2&M_3&M_4\end{bmatrix}
\begin{bmatrix}c_0\\c_1\\c_2\end{bmatrix}=\begin{bmatrix}T_0\\T_1\\T_2\end{bmatrix}.
\]
Khôi phục $g=c_0+c_1x+c_2x^2$. Bậc cao hơn tạo hệ tương tự với đủ các lũy thừa đến $2p-2$.
'''

# Mỗi mô hình có bảng và các tổng riêng, không thay bằng một ví dụ số.
MODELS=[
dict(title='Lũy thừa: Ax mũ b',label='power',menu='Lũy thừa',
 input=r'Không có ô cơ sở. Cần mọi $x_i>0$, $y_i\ne0$ và cùng dấu; điểm dự đoán cũng cần $x_*>0$.',
 relation=r'y\approx Ax^b\quad\Longrightarrow\quad\ln|y|\approx C+b\ln x,\quad C=\ln|A|.',
 u=r'\ln x_{i}',v=r'\ln|y_{i}|',u0=r'\ln x_0',v0=r'\ln|y_0|',un=r'\ln x_{N-1}',vn=r'\ln|y_{N-1}|',
 su=r'w_0\ln x_0+\cdots+w_{N-1}\ln x_{N-1}',sv=r'w_0\ln|y_0|+\cdots+w_{N-1}\ln|y_{N-1}|',
 suv=r'w_0\ln x_0\ln|y_0|+\cdots+w_{N-1}\ln x_{N-1}\ln|y_{N-1}|',
 c0='C',c1='b',output=r'Đặt $s=\operatorname{sign}(y_0)$; trả $A=se^C$, giữ $b$ rồi viết $g=Ax^b$. Hệ số $(C,b)$ của bài tuyến tính chưa phải $(A,b)$ của đề.',
 objective=r'$\ln|y|$; dữ liệu $y$ âm cùng dấu vẫn khôi phục biên độ $A$ âm'),
dict(title='Hàm mũ: Ae mũ bx',label='exp-log',menu='Hàm mũ',
 input=r'Ô cơ sở nhập \texttt{x} cho $Ae^{bx}$. Tool tự thêm cột 1 để tìm $\ln|A|$; không nhập thêm 1. Cần mọi $y_i$ cùng dấu khác 0; $x_i$ hữu hạn.',
 relation=r'y\approx Ae^{bx}\quad\Longrightarrow\quad\ln|y|\approx C+bx,\quad C=\ln|A|.',
 u='x_{i}',v=r'\ln|y_{i}|',u0='x_0',v0=r'\ln|y_0|',un='x_{N-1}',vn=r'\ln|y_{N-1}|',
 su=r'w_0x_0+\cdots+w_{N-1}x_{N-1}',sv=r'w_0\ln|y_0|+\cdots+w_{N-1}\ln|y_{N-1}|',
 suv=r'w_0x_0\ln|y_0|+\cdots+w_{N-1}x_{N-1}\ln|y_{N-1}|',
 c0='C',c1='b',output=r'Trả $A=se^C$ với $s=\operatorname{sign}(y_0)$; viết $g=Ae^{bx}$. $b$ là hệ số của $x$ trong số mũ, không phải cơ số.',objective=r'$\ln|y|$'),
dict(title='Log của tổ hợp cơ sở: ln(a+bx) và dạng nhiều cơ sở',label='log-combination',menu='Log của tổ hợp cơ sở',
 input=r'Nhập đầy đủ cơ sở trong log: \texttt{1;x} cho $\ln(a+bx)$; không tự thêm cột 1. $y_i$ hữu hạn bất kỳ, nhưng $e^{y_i}$ phải không tràn/hụt số.',
 relation=r'y\approx\ln(a+bx)\quad\Longrightarrow\quad e^y\approx a+bx.',
 u='x_{i}',v='e^{y_{i}}',u0='x_0',v0='e^{y_0}',un='x_{N-1}',vn='e^{y_{N-1}}',
 su=r'w_0x_0+\cdots+w_{N-1}x_{N-1}',sv=r'w_0e^{y_0}+\cdots+w_{N-1}e^{y_{N-1}}',
 suv=r'w_0x_0e^{y_0}+\cdots+w_{N-1}x_{N-1}e^{y_{N-1}}',
 c0='a',c1='b',output=r'Giữ $a,b$ và viết $g=\ln(a+bx)$; không đổi $a$ thành $e^a$. Kiểm $a+bx>0$ tại các điểm cần đánh giá. Với nhiều cơ sở, giữ $V_i=e^{y_i}$ và lập thiết kế từ mọi cơ sở bên trong log.',objective=r'$e^y$'),
dict(title='1/(a+b*x): biến đổi nghịch đảo tung độ',label='reciprocal',menu='1/(a+b*x)',
 input=r'Không nhập cơ sở. Cần mọi $y_i\ne0$; có thể khác dấu. Điểm dự đoán cần $a+bx_*\ne0$.',
 relation=r'y\approx\frac1{a+bx}\quad\Longrightarrow\quad\frac1y\approx a+bx.',
 u='x_{i}',v=r'1/y_{i}',u0='x_0',v0='1/y_0',un='x_{N-1}',vn='1/y_{N-1}',
 su=r'w_0x_0+\cdots+w_{N-1}x_{N-1}',sv=r'w_0/y_0+\cdots+w_{N-1}/y_{N-1}',
 suv=r'w_0x_0/y_0+\cdots+w_{N-1}x_{N-1}/y_{N-1}',
 c0='a',c1='b',output=r'Hệ số đã là $a,b$; viết $g=1/(a+bx)$, tính lại $g(x_i)$ để đánh giá sai số gốc. Mẫu gần 0 làm dự đoán nhạy.',objective=r'$1/y$'),
dict(title='x/(a+b*x): trả lại đúng thứ tự a,b',label='rational',menu='x/(a+b*x)',
 input=r'Không nhập cơ sở. Khi khớp cần mọi $x_i\ne0,y_i\ne0$. Tool tự dùng hai cơ sở $(1,1/x)$.',
 relation=r'y\approx\frac{x}{a+bx}\quad\Longrightarrow\quad\frac1y\approx b+a\frac1x.',
 u='1/x_{i}',v='1/y_{i}',u0='1/x_0',v0='1/y_0',un='1/x_{N-1}',vn='1/y_{N-1}',
 su=r'w_0/x_0+\cdots+w_{N-1}/x_{N-1}',sv=r'w_0/y_0+\cdots+w_{N-1}/y_{N-1}',
 suv=r'w_0/(x_0y_0)+\cdots+w_{N-1}/(x_{N-1}y_{N-1})',
 c0='b',c1='a',output=r'Bảng tuyến tính cho $(c_0,c_1)=(b,a)$, phải đổi lại $a=c_1,b=c_0$ rồi viết $g=x/(a+bx)$. Không thay bước đổi biến bằng $V=x/y$ khi mô tả tool: mục tiêu biến đổi sẽ khác. Tại điểm mới $x_*=0$, mô hình gốc có thể tính được nếu $a\ne0$.',objective=r'$1/y$ với cơ sở $1/x$'),
dict(title='a+b*ln(x): biến đổi hoành độ',label='plus-log',menu='a+b*ln(x)',
 input=r'Không nhập cơ sở. Cần mọi $x_i>0$; $y_i$ hữu hạn bất kỳ. Điểm dự đoán cũng cần $x_*>0$.',
 relation=r'y\approx a+b\ln x\quad\Longrightarrow\quad V\approx a+bU,\quad U=\ln x,\ V=y.',
 u=r'\ln x_{i}',v='y_{i}',u0=r'\ln x_0',v0='y_0',un=r'\ln x_{N-1}',vn='y_{N-1}',
 su=r'w_0\ln x_0+\cdots+w_{N-1}\ln x_{N-1}',sv=r'w_0y_0+\cdots+w_{N-1}y_{N-1}',
 suv=r'w_0y_0\ln x_0+\cdots+w_{N-1}y_{N-1}\ln x_{N-1}',
 c0='a',c1='b',output=r'Giữ trực tiếp $a,b$, viết $g=a+b\ln x$; không mũ hóa $a$. Chỉ đổi hoành độ nên mục tiêu vẫn ở thang tung độ gốc.',objective=r'$y$ gốc'),
dict(title='A*b mũ x: khôi phục biên độ và cơ số',label='geometric',menu='A*b^x',
 input=r'Không nhập cơ sở. Cần $y_i$ cùng dấu, khác 0; $x_i$ hữu hạn bất kỳ. Ký hiệu cơ số bằng $B$ để phân biệt hệ số mũ của $Ae^{bx}$; dạng hỗ trợ có $B>0$.',
 relation=r'y\approx AB^x\quad\Longrightarrow\quad\ln|y|\approx C+Dx,\quad C=\ln|A|,\ D=\ln B.',
 u='x_{i}',v=r'\ln|y_{i}|',u0='x_0',v0=r'\ln|y_0|',un='x_{N-1}',vn=r'\ln|y_{N-1}|',
 su=r'w_0x_0+\cdots+w_{N-1}x_{N-1}',sv=r'w_0\ln|y_0|+\cdots+w_{N-1}\ln|y_{N-1}|',
 suv=r'w_0x_0\ln|y_0|+\cdots+w_{N-1}x_{N-1}\ln|y_{N-1}|',
 c0='C',c1='D',output=r'Trả $A=se^C$, $B=e^D$, $s=\operatorname{sign}(y_0)$; viết $g=AB^x$. Không lấy $D$ làm cơ số. Ví dụ $y=(2,6,18)$ tại $x=(0,1,2)$ cho $g=2\cdot3^x$.',objective=r'$\ln|y|$'),
]
parts=[INTRO]
for m in MODELS:
    parts += [r'\section{'+m['title']+'}',r'\label{sec:ls-'+m['label']+'}',
      r'\paragraph{Input trong tool.} Chọn \textbf{'+tex(m['menu'])+'}; nhập $x,y$, trọng số nếu có và điểm dự đoán nếu cần. '+m['input'],
      r'\paragraph{Bước 1 -- biến đổi từng dòng.}\['+m['relation']+r'\]',
      r'\begin{center}\small\begin{tabular}{cllll}\toprule',
      r'Dòng&$U_i$&$V_i$&$w_iU_i^2$&$w_iU_iV_i$\\\midrule']
    for i,u,v in [('0',m['u0'],m['v0']),('i',m['u'],m['v']),('N-1',m['un'],m['vn'])]:
        parts.append('$'+i+'$&$'+u+'$&$'+v+'$&$w_{'+i+'}('+u+')^2$&$w_{'+i+'}('+u+')('+v+r')$\\')
    parts += [r'\bottomrule\end{tabular}\end{center}',
      r'\paragraph{Bước 2 -- cộng cột, lập hệ.} Các tổng viết riêng cho loại này là',
      r'\begin{align*}S_U&='+m['su']+r',\\S_V&='+m['sv']+r',\\S_{UV}&='+m['suv']+r'.\end{align*}',
      r'$S_1=w_0+\cdots+w_{N-1}$; $S_{UU}$ là tổng cột bình phương ở bảng trên, tức $w_0U_0^2+\cdots+w_{N-1}U_{N-1}^2$. Hệ cần giải:',
      r'\[\boxed{\begin{cases}S_1'+m['c0']+'+S_U'+m['c1']+r'=S_V,\\S_U'+m['c0']+'+S_{UU}'+m['c1']+r'=S_{UV}.\end{cases}}\]',
      r'\paragraph{Bước 3 -- output và cách đọc.} '+m['output'],
      'Tool cực tiểu hóa tổng bình phương có trọng số trên thang '+m['objective']+'. Sai số trên thang $y$ còn được báo thêm sau khôi phục. Đây là phép giải hữu hạn; không có bảng vòng hội tụ tham số ở nhánh này.']
    if m['label']=='exp-log':
        parts.append(r'''\subsection{Nhiều cơ sở trong số mũ: Ae mũ (bx bình phương + c/x)}
Input cơ sở \texttt{x\^{}2;1/x}, không thêm 1. Hàng $i$ là $(1,u_i,v_i)$ với $u_i=x_i^2,v_i=1/x_i$; đích $z_i=\ln|y_i|$. Lập đủ các cột $w_iu_i,w_iv_i,w_iu_i^2,w_iu_iv_i,w_iv_i^2,w_iz_i,w_iu_iz_i,w_iv_iz_i$.
Đặt $\langle f\rangle=w_0f(x_0,y_0)+\cdots+w_{N-1}f(x_{N-1},y_{N-1})$. Khi ấy
\[
\begin{bmatrix}\langle1\rangle&\langle x^2\rangle&\langle1/x\rangle\\
\langle x^2\rangle&\langle x^4\rangle&\langle x\rangle\\
\langle1/x\rangle&\langle x\rangle&\langle1/x^2\rangle\end{bmatrix}
\begin{bmatrix}C\\b\\c\end{bmatrix}
=\begin{bmatrix}\langle\ln|y|\rangle\\\langle x^2\ln|y|\rangle\\\langle\ln|y|/x\rangle\end{bmatrix}.
\]
Ví dụ $\langle x\rangle=w_0x_0+\cdots+w_{N-1}x_{N-1}$ do $u_iv_i=x_i$;
$\langle x^2\ln|y|\rangle=w_0x_0^2\ln|y_0|+\cdots+w_{N-1}x_{N-1}^2\ln|y_{N-1}|$.
Output $A=se^C$, $g=A\exp(bx^2+c/x)$. Đổi cơ sở thành \texttt{x;1/x} thì phải lập lại các tích từ hàng $(1,x_i,1/x_i)$.
''')

TAIL=r'''
\section{Lũy thừa -- SSE thang y: lặp trực tiếp cho Ax mũ b}
\label{sec:ls-power-raw}
\paragraph{Input.} Chọn \textbf{Lũy thừa -- SSE thang y}, nhập $x_i>0$, $y_i$ hữu hạn bất kỳ; không cần $y$ cùng dấu. Không có ô cơ sở. Tham số đầu theo thứ tự \texttt{A b}, ngưỡng dừng mặc định $10^{-10}$, tối đa 100 vòng.
\paragraph{Quá trình riêng của mô hình.} Tại bộ $(A,b)$ hiện tại, tính từng dòng:
\begin{center}\small\begin{tabular}{cllll}\toprule
Dòng&$g_i$&$g_i-y_i$&$\partial g_i/\partial A$&$\partial g_i/\partial b$\\\midrule
0&$Ax_0^b$&$Ax_0^b-y_0$&$x_0^b$&$Ax_0^b\ln x_0$\\
$i$&$Ax_i^b$&$Ax_i^b-y_i$&$x_i^b$&$Ax_i^b\ln x_i$\\
$N-1$&$Ax_{N-1}^b$&$Ax_{N-1}^b-y_{N-1}$&$x_{N-1}^b$&$Ax_{N-1}^b\ln x_{N-1}$\\\bottomrule
\end{tabular}\end{center}
Mục tiêu $E=w_0(Ax_0^b-y_0)^2+\cdots+w_{N-1}(Ax_{N-1}^b-y_{N-1})^2$. Dùng bảng này tạo phần dư và Jacobian, chạy chu trình LM ở mục \ref{sec:ls-lm-tool}, tính lại bảng sau mỗi bước nhận. Không dùng $\ln y_i$ làm đích của mục tiêu.
\paragraph{Output.} $(A,b)$ theo đơn vị gốc, $g=Ax^b$, mọi bước thử nhận/từ chối, SSE và lý do dừng. Khi chưa đạt ngưỡng, tham số cuối chỉ để kiểm tra.

\section{Hàm mũ -- SSE thang y: một hoặc nhiều cơ sở số mũ}
\label{sec:ls-exp-raw}
\paragraph{Input.} Chọn \textbf{Hàm mũ -- SSE thang y}. Cơ sở chỉ nhập phần số mũ, ví dụ \texttt{x} hoặc \texttt{x\^{}2;1/x}, không thêm 1. Với $q$ cơ sở, tham số đầu là \texttt{A b1 ... bq}. $y$ có thể khác dấu/0 nhưng mọi cơ sở phải xác định. Một mô hình mũ có biên độ cố định vẫn có một dấu; cho phép dữ liệu đổi dấu không có nghĩa khớp đúng mọi dòng.
\paragraph{Quá trình riêng của mô hình.}
\[
L_i=\sum_{j=1}^qb_j\psi_j(x_i)=b_1\psi_1(x_i)+\cdots+b_q\psi_q(x_i),\quad g_i=Ae^{L_i}.
\]
Jacobian hàng $i$ theo $(A,b_1,\ldots,b_q)$ là
\[
(e^{L_i},\ Ae^{L_i}\psi_1(x_i),\ldots,Ae^{L_i}\psi_q(x_i)).
\]
Ví dụ \texttt{x\^{}2;1/x}, $L_i=bx_i^2+c/x_i$:
\begin{center}\small\begin{tabular}{cllll}\toprule
Dòng&$g_i$&Cột theo $A$&Cột theo $b$&Cột theo $c$\\\midrule
0&$Ae^{L_0}$&$e^{L_0}$&$Ae^{L_0}x_0^2$&$Ae^{L_0}/x_0$\\
$i$&$Ae^{L_i}$&$e^{L_i}$&$Ae^{L_i}x_i^2$&$Ae^{L_i}/x_i$\\
$N-1$&$Ae^{L_{N-1}}$&$e^{L_{N-1}}$&$Ae^{L_{N-1}}x_{N-1}^2$&$Ae^{L_{N-1}}/x_{N-1}$\\\bottomrule
\end{tabular}\end{center}
Mục tiêu gốc $E=w_0(Ae^{L_0}-y_0)^2+\cdots+w_{N-1}(Ae^{L_{N-1}}-y_{N-1})^2$. Tính mọi dòng bằng cùng một bộ tham số rồi mới cộng; chạy chu trình dưới đây.
\paragraph{Output.} Vector $(A,b_1,\ldots,b_q)$, công thức $g$, bảng vòng lặp, SSE gốc, lý do dừng, dự đoán tùy chọn. Thứ tự cơ sở quyết định ý nghĩa từng tham số.

\section{Chu trình LM: một vòng nhận gì, tính gì, chuyển gì sang vòng sau?}
\label{sec:ls-lm-tool}
\paragraph{Khởi tạo.} Nhập tham số đầu thì dùng đúng bộ đó. Để trống: nếu mọi $y$ cùng dấu khác 0, khởi tạo từ khớp log; trường hợp còn lại dùng trung bình có trọng số làm biên độ (nếu bằng 0 lấy giá trị khởi tạo nội bộ 1), các hệ số mũ bằng 0. Đây chỉ là khởi tạo, không đổi mục tiêu SSE gốc.

Tool đặt $s_y=\max_{w_i>0}|y_i|$ (bằng 0 thì lấy 1), $w_{\max}=\max w_i$, $\alpha=A/s_y$, $\rho_i=\sqrt{w_i/w_{\max}}$. Tham số nội bộ $p=(\alpha,b_1,\ldots,b_q)$. Tại các dòng có trọng số dương:
\[
r_i=\rho_i(\alpha e^{L_i}-y_i/s_y),\quad
J_i=\rho_i(e^{L_i},\alpha e^{L_i}\psi_1(x_i),\ldots,\alpha e^{L_i}\psi_q(x_i)).
\]
Dòng $w_i=0$ có phần dư nội bộ bằng 0. $F=r_0^2+\cdots+r_{N-1}^2$ là mục tiêu nội bộ; SSE có trọng số gốc là $E=s_y^2w_{\max}F$. Tham số hiển thị đổi lại $A=s_y\alpha$.
\begin{enumerate}
\item Nhận $p_k,r_k,J_k,F_k,\lambda_k$ từ vòng trước; ban đầu $\lambda_0=10^{-3}$.
\item Tính $h=J_k^Tr_k$, với $h_j=J_{0j}r_0+\cdots+J_{N-1,j}r_{N-1}$. Nếu $\max_j|h_j|\le\tau$, dừng trước khi tạo bước thử mới.
\item Tính $d_j=\sqrt{J_{0j}^2+\cdots+J_{N-1,j}^2}$, nếu bằng 0 thay 1; giải bước
\[
\begin{bmatrix}J_k\\\sqrt{\lambda_k}\operatorname{diag}(d_j)\end{bmatrix}\Delta p
\approx\begin{bmatrix}-r_k\\0\end{bmatrix}.
\]
\item Tạo $p^{\rm thử}=p_k+\Delta p$, tính lại mô hình, phần dư, Jacobian và $F^{\rm thử}$ trên toàn bảng.
\item Chỉ nhận nếu bước hữu hạn và $F^{\rm thử}<F_k$. Khi nhận, chuyển toàn bộ bộ mới sang vòng sau, $\lambda\leftarrow\max(\lambda/3,10^{-15})$. Khi từ chối, giữ bộ cũ, $\lambda\leftarrow10\lambda$, vẫn lưu bước thử.
\item Sau bước nhận còn kiểm đồng thời $\|\Delta p\|_2/(1+\|p_{k+1}\|_2)\le\tau$ và $|F_k-F_{k+1}|\le\tau(1+F_k)$. Nếu chưa đạt thì tiếp tục. Hết vòng chưa đạt phải báo chưa hội tụ.
\end{enumerate}
\paragraph{Bảng tổng quát.} Chia thành hai bảng cùng khóa vòng $k$:
\begin{center}\small\begin{tabular}{cllll}\toprule
Vòng&Tham số cũ&Tham số thử&$\lambda$ dùng&Quyết định\\\midrule
1&$p_0$&$p_0+\Delta p_0$&$10^{-3}$&Nhận/từ chối\\
$k+1$&$p_k$&$p_k+\Delta p_k$&$\lambda_k$&So mục tiêu mới/cũ\\\bottomrule
\end{tabular}\end{center}
\begin{center}\small\begin{tabular}{cllll}\toprule
Vòng&SSE trước&SSE thử&$\|J^Tr\|_\infty$&$\|\Delta p\|_2$\\\midrule
1&$s_y^2w_{\max}F_0$&$s_y^2w_{\max}F^{\rm thử}$&Gradient trước bước&Bước nội bộ\\
$k+1$&$s_y^2w_{\max}F_k$&$s_y^2w_{\max}F^{\rm thử}$&Gradient trước bước&Bước nội bộ\\\bottomrule
\end{tabular}\end{center}
Mở chi tiết để xem $J,r$ dùng tạo bước. Không đưa tham số thử bị từ chối sang vòng sau. Đạt tiêu chuẩn số chưa chứng minh cực tiểu toàn cục.

\section{Output: bảng sai số tổng quát và kết luận bài khớp}
\label{sec:ls-output}
Sau khi khôi phục tham số, thế lại mọi $x_i$ bằng mô hình gốc:
\begin{center}\small\begin{tabular}{clllll}\toprule
Dòng&$y_i$&$g_i$&$e_i=y_i-g_i$&$e_i^2$&$w_ie_i^2$\\\midrule
0&$y_0$&$g(x_0)$&$y_0-g(x_0)$&$e_0^2$&$w_0e_0^2$\\
$i$&$y_i$&$g(x_i)$&$y_i-g(x_i)$&$e_i^2$&$w_ie_i^2$\\
$N-1$&$y_{N-1}$&$g(x_{N-1})$&$y_{N-1}-g(x_{N-1})$&$e_{N-1}^2$&$w_{N-1}e_{N-1}^2$\\\midrule
Tổng&&&&$\mathrm{SSE}_y$&$E_y$\\\bottomrule
\end{tabular}\end{center}
\begin{align*}
\mathrm{SSE}_y&=\sum_ie_i^2=e_0^2+e_1^2+\cdots+e_{N-1}^2,\\
E_y&=\sum_iw_ie_i^2=w_0e_0^2+\cdots+w_{N-1}e_{N-1}^2,\\
\mathrm{MSE}_y&=\mathrm{SSE}_y/N,\quad \mathrm{RMSE}_y=\sqrt{\mathrm{SSE}_y/N},\\
\mathrm{RMSE}_w&=\sqrt{E_y/(w_0+w_1+\cdots+w_{N-1})}.
\end{align*}
Bài biến đổi còn có $\widehat V_i$ và phần dư $V_i-\widehat V_i$ trên thang đang khớp. Không coi SSE gốc là mục tiêu đã cực tiểu nếu tool đang khớp log/nghịch đảo/mũ hóa. $R^2$ nếu có không phải cận sai số. Sai số thống kê chia $N-p$ khác RMSE chia $N$.

Nếu cơ sở thiếu hạng, mặc định báo tham số chưa duy nhất; chỉ khi đã chủ động chọn SVD và quy tắc chuẩn nhỏ nhất mới nhận nghiệm kiểu đó. Điểm dự đoán phải thuộc miền mô hình khôi phục. Một điểm dự đoán sai miền không làm dữ liệu khớp trước đó tự thay đổi.

\paragraph{Bài thi cần ghi.} Tên mô hình và cơ sở $\to$ miền áp dụng $\to$ bảng biến đổi $\to$ các tích và tổng $\to$ hệ/bài tối ưu $\to$ tham số khôi phục $\to$ hàm $g$ $\to$ sai số đúng thang $\to$ dự đoán. Với SSE phi tuyến thêm mọi bước thử và lý do dừng. Các ví dụ số đã kiểm ở \texttt{verification/spline\_ls\_examples.py}; đề thật ở Phụ lục \ref{app:exam}.
'''
parts.append(TAIL)
if '--write-ls' in sys.argv:
    source='\n\n'.join(parts).replace(r'\section{',r'\examplebreak'+'\n'+r'\section{')
    source=source.replace(r'\paragraph{',r'\subsubsection*{')
    (CH/'04_binh_phuong_toi_thieu.tex').write_text(source,encoding='utf-8')
print('Generated GUI input tables for',len(GROUPS),'groups.',
      'Rebuilt LS chapter.' if '--write-ls' in sys.argv else 'Kept editable LS chapter unchanged.')
