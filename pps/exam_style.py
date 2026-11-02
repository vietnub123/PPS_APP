"""Dàn ý bài giải; chỉ mô tả lựa chọn đã chạy, không thay dữ liệu/bộ giải.

GUI, HTML và sổ tay dùng cùng một danh mục. Các bảng số và nhật ký vẫn
được lấy từ Report của thuật toán, không tính lại bằng một mô hình khác.
"""


def outline(tool, method, values=None):
    values = values or {}
    if tool in ('Nội suy đa thức', 'Newton'):
        newton = method == 'Newton' or tool == 'Newton'
        if newton:
            equal = (method=='Mốc cách đều' if tool=='Newton' else
                     values.get('newton_nodes', 'Mốc cách đều') == 'Mốc cách đều')
            direction = values.get('direction', 'Tiến')
            construction = ('sai phân' if equal else 'tỉ sai phân') + '; lấy đường hệ số Newton ' + direction.lower()
        else:
            construction = {
                'Lagrange': 'các tích W_i và mẫu d_i; lấy hệ số y_i/d_i',
                'Gauss I': 'bảng sai phân; kết nạp mốc quanh tâm theo thứ tự 0, +1, −1, +2, −2, …',
                'Gauss II': 'bảng sai phân; kết nạp mốc quanh tâm theo thứ tự 0, −1, +1, −2, +2, …',
                'Stirling': 'bảng sai phân; cấp lẻ lấy trung bình hai ô kề tâm, cấp chẵn lấy một ô giữa',
                'Bessel': 'bảng sai phân; ghép hai mốc giữa, cấp chẵn lấy trung bình hai ô đối xứng',
            }.get(method, 'bảng hệ số theo công thức đã chọn')
        steps = [
            'Công bố tập mốc thực dùng và ID nguồn; kiểm tra x phân biệt, điều kiện lưới và số mốc của phương pháp.',
            'Đặt biến và gốc: với mốc cách đều dùng t=(x−x_gốc)/h; với Lagrange/Newton bất kỳ giữ biến x.',
            'Lập ' + construction + '. Ghi rõ nguồn của từng hệ số và mẫu chia.',
            'Viết đa thức dưới dạng tổng các hệ số nhân cơ sở; khai triển từng tích và cộng theo cột khi cần dạng chính tắc.',
            'Thế điểm tính, cộng đủ các hạng; tính đạo hàm trên cùng đa thức. Nếu đổi biến, P^(r)(x)=Q^(r)(t)/h^r.',
            'Thế lại các mốc và đối chiếu cách đánh giá; kết luận giá trị, đạo hàm và phạm vi sai số.',
        ]
        output = 'Tập mốc, bảng hệ số, đa thức, giá trị tại điểm tính và đạo hàm được yêu cầu; cận sai số chỉ khi có giả thiết bổ sung.'
    elif tool == 'Spline':
        boundary = {
            'Tuyến tính': 'không cần điều kiện biên bổ sung',
            'Bậc hai — biên trái': 'một đạo hàm đầu trái; truyền đạo hàm sang phải',
            'Bậc hai — biên phải': 'một đạo hàm đầu phải; truyền đạo hàm sang trái',
            'Cubic tự nhiên': 'S″(a)=S″(b)=0',
            'Cubic kẹp': 'hai giá trị S′(a), S′(b) được nhập',
            'Cubic đạo hàm bậc hai': 'hai giá trị S″(a), S″(b) được nhập',
            'Cubic hỗn hợp': 'đúng phía, cấp và giá trị đạo hàm đã chọn ở mỗi đầu',
            'Cubic tuần hoàn': 'giá trị hai đầu bằng nhau; ghép S′ và S″ ở hai đầu',
            'Cubic not-a-knot': 'đạo hàm bậc ba liên tục tại mốc thứ hai và áp chót; xử lý riêng bảng ít mốc',
            'Bậc 4 — đạo hàm trái': 'ba giá trị S′, S″, S‴ ở đầu trái; truyền các đạo hàm sang phải',
            'Biên tổng quát': 'p−1 điều kiện độc lập đúng phía và cấp trong JSON; không tự thêm biên tự nhiên',
        }[method]
        steps = [
            'Sắp cặp theo x, giữ ID nguồn; đặt h_i=x_(i+1)−x_i và δ_i=(y_(i+1)−y_i)/h_i.',
            'Công bố bậc spline và điều kiện biên: ' + boundary + '.',
            'Đặt u=x−x_i trên từng đoạn; lập điều kiện nội suy, ghép đạo hàm đến cấp p−1 và điều kiện biên.',
            'Thực hiện truy hồi hoặc giải đúng hệ đã lập. Với cubic moment, tìm M_i=S″(x_i) rồi khôi phục từng mảnh.',
            'Viết S_i(x) cùng miền [x_i,x_(i+1)]; xác định mảnh chứa điểm tính trước khi thế số, đạo hàm hoặc tích phân.',
            'Kiểm tra giá trị tại mốc, độ khớp đạo hàm và điều kiện biên; kết luận đúng miền nội suy đã nhập.',
        ]
        output = 'Điều kiện biên, hệ/truy hồi, hệ số và công thức mọi mảnh, giá trị/đạo hàm/tích phân được yêu cầu, phần dư kiểm tra.'
    elif tool == 'Bình phương tối thiểu':
        transformations = {
            'Tuyến tính theo cơ sở': 'z=y, g(x)=c_0φ_0(x)+…+c_(p−1)φ_(p−1)(x); các cơ sở lấy đúng ô nhập',
            'Lũy thừa': 'z=ln|y|, u=ln x, z≈c_0+c_1u; khôi phục A=s·exp(c_0), b=c_1',
            'Hàm mũ': 'z=ln|y|, z≈c_0+c_1φ_1(x)+…; khôi phục A=s·exp(c_0)',
            'A*b^x': 'z=ln|y|, z≈c_0+c_1x; khôi phục A=s·exp(c_0), B=exp(c_1)>0',
            'Log của tổ hợp cơ sở': 'z=exp(y), z≈c_0φ_0(x)+…; khôi phục g(x)=ln(c_0φ_0(x)+…)',
            '1/(a+b*x)': 'z=1/y, z≈a+bx; khôi phục g(x)=1/(a+bx)',
            'x/(a+b*x)': 'z=1/y, u=1/x, z≈c_0+c_1u; khôi phục a=c_1, b=c_0',
            'a+b*ln(x)': 'z=y, u=ln x, z≈a+bu; không đổi thang tung độ',
            'Lũy thừa — SSE thang y': 'g(x)=A·exp(b ln x)=A x^b; tối thiểu SSE trên y bằng LM',
            'Hàm mũ — SSE thang y': 'g(x)=A·exp(b_1φ_1(x)+…); tối thiểu SSE trên y bằng LM',
        }
        nonlinear = 'SSE thang y' in method
        steps = [
            'Công bố N quan sát, trọng số và mô hình. Kiểm tra miền, dấu và hạng; không tự lọc dòng để ép phép biến đổi hợp lệ.',
            'Viết phép biến đổi và ánh xạ tham số: ' + transformations[method] + '.',
        ]
        if nonlinear:
            steps += [
                'Công bố tham số đầu. Mỗi bước thử lập dự đoán, phần dư, Jacobian và hệ tăng cường LM với damping λ.',
                'Ghi tham số cũ/đề xuất, SSE trước/sau, λ và quyết định nhận hoặc từ chối. Giữ cả các bước thử bị từ chối.',
                'Kiểm tra điều kiện dừng thực tế; kết luận phụ thuộc điểm đầu, không suy ra cực tiểu toàn cục.',
            ]
        else:
            steps += [
                'Lập Φ_ij=φ_j(x_i), bảng các tích và các tổng; viết J=Σw_i(Σc_jφ_j(x_i)−z_i)².',
                'Từ ∂J/∂c_j=0 suy ra (ΦᵀWΦ)c=ΦᵀWz. Trình bày hệ tổng quát rồi hệ đã thế số.',
                'Tính nghiệm bằng bộ giải đã chọn: Gauss trên hệ chuẩn, QR trên thiết kế có trọng số hoặc SVD. Nhật ký phải đúng bộ giải.',
            ]
        steps += ['Khôi phục tham số và hàm g theo biến gốc; lập r_i=y_i−g(x_i), tính SSE, RMSE và mục tiêu trên thang khớp riêng biệt.']
        output = 'Hàm g(x), tham số gốc, bảng thiết kế/tổng, hệ và nhật ký bộ giải, phần dư và sai số có định nghĩa rõ.'
    elif tool == 'Nội suy ngược':
        direct = method.startswith('Hàm ngược')
        bisect = method == 'Chia đôi đa thức'
        steps = [
            'Công bố mức y*, các mốc được chọn và nhánh/khoảng nghiệm; kiểm tra trường hợp trùng mốc, nghiệm nhiều nhánh và dữ liệu phẳng.',
            ('Đổi vai x và y trên nhánh đã chọn; lập đa thức x≈Q(y) bằng ' + method.split('—')[-1].strip() + '.' if direct else
             'Giữ toàn bộ tập mốc đã chọn; dựng đa thức thuận p. Lặp tiến lấy gốc đầu tập, lặp lùi lấy gốc cuối tập; khoảng nghiệm có thể nằm giữa.'),
        ]
        if direct:
            steps += ['Thế y* vào Q; trình bày các tích/hệ số và tổng từng hạng. Không gọi đây là nghiệm chính xác của p(x)=y*.',
                      'Kiểm tra miền nhánh và báo ngoại suy nếu mức đích nằm ngoài dữ liệu được chọn.']
        elif bisect:
            steps += ['Đặt F(x)=p(x)−y*; kiểm tra dấu tại hai đầu. Mỗi vòng tính c=(a+b)/2, F(c) và giữ nửa đoạn còn đổi dấu.',
                      'Ghi a, b, c, phần dư và độ rộng từng vòng; trả về kết quả khi đạt điều kiện dừng hoặc trạng thái chưa đạt.']
        else:
            steps += ['Đặt t=(x−x_gốc)/h, t_0 theo quy tắc khởi tạo; tách hạng tuyến tính để viết t_(k+1)=H(t_k), cố định các sai phân.',
                      'Mỗi vòng ghi t_k, từng tích và đóng góp phi tuyến, H(t_k), x_(k+1), độ đổi theo x và phần dư |p(x)−y*|.',
                      'Dừng thực hành cần đạt cả độ đổi theo x và phần dư. Chế độ có cận co còn kiểm tra miền bất biến, q<1 và cận sai số; giữ nhật ký thất bại.']
        output = 'Nghiệm x xấp xỉ hoặc lý do chưa đạt, tập mốc/gốc thực dùng, bảng hệ số, toàn bộ vòng lặp và tiêu chí dừng.'
    elif tool == 'Chọn mốc':
        steps = ([
            'Cho bậc n và đoạn [a,b]; cần sinh N=n+1 mốc.',
            'Tính θ_k=(2k+1)π/(2N), k=0,…,N−1; đặt x_k=(a+b)/2+(b−a)cos θ_k/2.',
            'Sắp mốc tăng và giữ ánh xạ với chỉ số k ban đầu; đánh giá hàm tại các mốc này nếu cần bảng y.',
        ] if method == 'Chebyshev' else [
            'Đọc cặp x,y, giữ ID nguồn; kiểm tra cặp hợp lệ và yêu cầu điểm/số mốc.',
            ('Chia các nhánh đơn điệu và tìm các khoảng chứa mức y*; công bố mọi lựa chọn, không tự gộp nhánh.' if method == 'Mốc nội suy ngược' else
             'Trên lưới đều chọn một cửa sổ liên tiếp gần điểm tính; công bố các mốc và kiểm tra đủ số lượng.'),
            'Xuất các mốc đã chọn và ID nguồn; dùng tập này làm đầu vào riêng cho phương pháp nội suy được quyết định sau đó.',
        ])
        output = 'Các mốc/nhánh, thứ tự và ID nguồn; bước chọn mốc chưa phải lời giải nội suy.'
    elif tool == 'Đạo hàm & Horner':
        steps = ([
            'Đọc hệ số theo bậc giảm, giữ các hệ số 0 giữa/cuối; viết lại P(x) và điểm c.',
            'Lập bảng ngang: hàng A_j; hàng c·b_(j−1) dịch sang phải một ô; hàng cộng b_j=A_j+c·b_(j−1).',
            'Phần tử cuối là số dư s_0=P(c); các phần tử trước tạo thương Q_1.',
            'Chia tiếp thương cho x−c, lấy s_r; P^(r)(c)=r!s_r. Công bố số dư và thương của từng lượt.',
            'Kết luận giá trị và các đạo hàm; đây là tính hữu hạn, không có điều kiện hội tụ.',
        ] if method == 'Horner' else [
            'Chọn p+1 mốc gần điểm tính, giữ ID nguồn; xác định cấp đạo hàm r và đa thức bậc không quá p.',
            'Đặt tọa độ chuẩn hóa quanh điểm tính, lập các trọng số đạo hàm từ điều kiện chính xác trên đơn thức.',
            'Lập bảng w_i, y_i, w_i y_i; cộng đủ mọi hạng và đổi đơn vị đạo hàm nếu có chuẩn hóa.',
            'Kiểm tra tính chính xác trên các đơn thức và công bố mốc thực dùng; kết luận đạo hàm của mô hình, không tự nhận cận sai số hàm thật.',
        ])
        output = 'Giá trị/đạo hàm, bảng nhân–cộng hoặc trọng số và đối chiếu; đạo hàm vượt bậc đa thức bằng 0.'
    elif tool == 'Tích phân':
        if method == 'Tích phân kép':
            steps = ['Công bố hình chữ nhật, hàm hai biến, quy tắc và n trên mỗi trục; kiểm tra miền hàm.',
                     'Lập hai lưới và trọng số một chiều; trọng số tại (i,j) là tích w_i v_j.',
                     'Cộng từng hàng rồi cộng các hàng: I≈h_x h_y Σ_iΣ_j w_i v_j f(x_i,y_j).',
                     'Chia đôi bước ở cả hai trục; ghi n, I và Runge từng vòng. Đối chiếu thêm lưới không lồng nhau khi cần.',
                     'Kết luận xấp xỉ và ước lượng Runge; điều kiện trơn của hàm vẫn phải được xét.']
        else:
            rule = {'Hình thang':'h[y_0+2y_1+…+2y_(n−1)+y_n]/2',
                    'Simpson':'h[y_0+4y_1+2y_2+4y_3+…+4y_(n−1)+y_n]/3, n chẵn',
                    'Trung điểm':'h[f(a+h/2)+f(a+3h/2)+…+f(b−h/2)]',
                    'Newton-Cotes':'h[w_0y_0+w_1y_1+…+w_ny_n], n chia hết cho bậc khối'}[method]
            steps = ['Xác định nguồn Hàm/Bảng, hai cận, n và điều kiện miền; nếu đảo cận thì đổi dấu kết quả.',
                     'Lập lưới đúng quy tắc và bảng x_i, y_i, w_i; h=(b−a)/n. Với trung điểm, dữ liệu phải ở tâm mỗi ô.',
                     'Viết công thức và thế các hạng: I_h≈'+rule+'.',
                     'Nếu nhập ε và M, chọn n từ cận lý thuyết. Nếu chỉ nhập ε, tăng lưới và kiểm tra Runge cùng lưới đối chiếu.',
                     'Công bố kết quả ở lưới được trả về, các lượt chia lưới và sai số; Runge là ước lượng, cận M có giả thiết riêng.']
        output = 'Tích phân xấp xỉ, lưới/trọng số, các lượt tinh chỉnh và ước lượng/cận sai số được phân biệt rõ.'
    elif tool == 'Phương trình vi phân':
        if method.startswith('Adams'):
            update = 'Khởi tạo s−1 bước bằng RK4; từ đủ lịch sử, dự báo AB_s rồi giải phương trình AM_(s+1) với dự báo làm điểm đầu.'
        elif method in ('Euler ẩn', 'Hình thang'):
            update = ('Giải R(v)=v−u_i−h f(t_(i+1),v)=0 bằng bộ giải hệ ẩn.' if method == 'Euler ẩn' else
                      'Giải R(v)=v−u_i−h[f(t_i,u_i)+f(t_(i+1),v)]/2=0 bằng bộ giải hệ ẩn.')
        else:
            update = 'Công bố bảng A,b,c. Mỗi bước tính lần lượt K_j=f(t_i+c_jh,u_i+hΣ_(l<j)a_jl K_l), rồi u_(i+1)=u_i+hΣ_j b_jK_j.'
        steps = ['Viết hệ u′=f(t,u), u(a)=u_0; trong ô nhập, biến độc lập là t và các trạng thái là x,y,z.',
                 'Lập lưới t_i=a+ih; h phải đúng chiều và kết thúc đúng ở b. Công bố bộ hệ số của phương pháp.',
                 update,
                 'Ghi các tầng/dự báo/hiệu chỉnh thực sự được tính. Bước ẩn kiểm tra phần dư và Jacobian; đánh giá của bộ giải không đồng nghĩa một vòng Newton.',
                 'Lập bảng nghiệm qua mọi t_i, kèm phần dư bước ẩn. Kết luận trên lưới h; dung sai hệ ẩn không phải cận sai số nghiệm ODE.']
        output = 'Nghiệm tại các mốc, bảng hệ số/tầng RK hoặc dự báo–hiệu chỉnh, phần dư và thông tin kiểm tra bước ẩn.'
    elif tool == 'Bài toán biên':
        steps = ['Viết −(p u′)′+qu='+('λr u' if method == 'Trị riêng' else 'f')+' trên [a,b]; công bố lưới và quy ước dấu.',
                 'Tính p tại nửa bước, q tại mốc; lập các hàng sai phân ở mốc trong từ thông lượng hai mặt ô.']
        if method == 'Trị riêng':
            steps += ['Dùng u(a)=u(b)=0; kiểm tra p>0, r>0 và dựng K v=λ R v trên các mốc trong.',
                      'Đổi sang ma trận đối xứng R^(−1/2) K R^(−1/2), tính các trị riêng nhỏ nhất và đổi lại vectơ.',
                      'Khôi phục hai biên 0, chuẩn hóa max|u|=1 đúng như tool; công bố từng trị riêng và vectơ riêng trên lưới.']
        else:
            steps += ['Thay αu′+βu=γ ở mỗi đầu; trường hợp α=0 là Dirichlet, trường hợp α≠0 dùng phương trình nửa ô.',
                      'Công bố các đường chéo và vế phải; giải hệ băng đã lập, giữ đủ các hàng biên.',
                      'Lập bảng u_i, thế lại hệ và báo phần dư. Phần dư đại số không đồng nghĩa sai số so với nghiệm liên tục.']
        output = 'Hệ rời rạc, nghiệm trên lưới hoặc các cặp trị riêng–vectơ riêng và thông tin chuẩn hóa/kiểm tra.'
    else:
        raise ValueError('Chưa có dàn ý trình bày cho '+str((tool, method)))
    return {'steps': steps, 'output': output}


def apply_exam_style(report, tool, method, values, xtext, ytext, field_specs):
    """Thêm đường dẫn suy luận và dàn bố cục cho cả báo cáo cũ/rich.

    Không thay Report.value, các bảng hiện có, nhật ký, mốc hay tham số.
    """
    from .inverse_presentation import _Writer
    recipe = outline(tool, method, values)
    inputs = [(label, values.get(key, default)) for key, label, default, *_ in field_specs
              if str(values.get(key, default)).strip()]
    entry = {'kind': 'panel', 'title': 'Dữ liệu → lập luận → kết quả', 'children': []}
    children = entry['children']
    if (xtext is not None and ytext is not None and len(xtext)>0 and len(ytext)>0
            and tool not in ('Phương trình vi phân', 'Bài toán biên')):
        children.append({'kind':'text', 'text':'Các cặp x,y lấy từ bảng đã nhập; tập thực dùng và ID nguồn được công bố trong phần tính.'})
    children.append({'kind':'text', 'text':'; '.join(str(k)+': '+str(v) for k,v in inputs)+'.'})
    children.append({'kind':'details','title':'Cách lập bài và thứ tự các bước','open':False,
                     'children':[{'kind':'text', 'text':f'B{i}. {step}'} for i,step in enumerate(recipe['steps'],1)]})
    children.append({'kind':'text','text':'Output cần đọc: '+recipe['output']})
    presentation = report.presentation
    key = 'worked_layout' if 'worked_layout' in presentation else 'inverse_layout' if 'inverse_layout' in presentation else None
    if key:
        layout = presentation[key]
        if presentation.get('exam_style'): return report
        # Kết quả tóm tắt của các presenter cũ chuyển xuống sau phép tính.
        summaries=[node for node in layout if node.get('title') in ('Kết quả','Kết quả của lượt tính')]
        layout[:]=[node for node in layout if node not in summaries]+summaries
        layout.insert(0, entry)
        # Tái tạo bản text từ cùng cây, không thêm một bản số liệu song song.
        writer = object.__new__(_Writer)
        writer.report=report; writer.layout=layout
        presentation['blocks']=[]
        writer.finish()
    else:
        saved = dict(presentation)
        writer = _Writer(report, 'summary')
        writer.layout.append(entry)
        with writer.group('section','1. Phương trình và công thức áp dụng'):
            for title, formulas in saved.get('formulas', []):
                if title=='Kết quả': continue
                writer.text(title)
                for formula in formulas: writer.formula(formula, formula)
        with writer.group('section','2. Bảng tính và các bước thực hiện'):
            indexes=list(range(len(report.tables)))
            if tool=='Phương trình vi phân':
                def priority(i):
                    title=report.tables[i][0]
                    if 'Bảng hệ số' in title or 'Trọng số RK' in title or 'Hệ số Adams' in title:return 0
                    if 'tầng RK' in title:return 1
                    if 'Dự báo AB' in title:return 2
                    if 'Nghiệm trên lưới' in title:return 4
                    return 3
                indexes.sort(key=priority)
            elif tool=='Bài toán biên' and method=='Trị riêng':
                indexes.sort(key=lambda i:0 if report.tables[i][0].startswith('Toán tử') else 1)
            for i in indexes:
                title=report.tables[i][0]
                if 'kiểm tra' in title.casefold() or 'phần dư' in title.casefold() or 'Giá trị lưới 2D' in title:
                    with writer.details(title): writer.stack[-1].append({'kind':'table','index':i})
                else: writer.stack[-1].append({'kind':'table','index':i})
        with writer.group('section','3. Kết luận và sai số'):
            for title, formulas in saved.get('formulas', []):
                if title=='Kết quả':
                    for formula in formulas: writer.formula(formula,formula)
            for line in report.lines:
                if line: writer.text(line)
            for line in saved.get('after_tables_text', []): writer.text(line)
        writer.finish()
        presentation['worked_layout']=presentation.pop('inverse_layout')
        presentation['worked_tables']=presentation.pop('inverse_tables')
        for name, value in saved.items():
            if name not in ('formulas','blocks','plain_formulas'): presentation.setdefault(name,value)
    presentation['exam_style']={'version':1, 'tool':tool, 'method':method, **recipe}
    return report
