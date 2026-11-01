"""Vết tính và lời giải nội suy/đạo hàm/Horner theo đặc tả đã duyệt.

Các số trung gian là Decimal đang dùng trong phép tính, không đọc lại từ
chuỗi đã làm tròn. Cây bố cục dùng chung cho Tk, văn bản và HTML ngoại tuyến.
"""
from decimal import Decimal, localcontext
import math

import numpy as np

from . import common
from .worked_report import ReportBuilder


ZERO = Decimal(0)
ONE = Decimal(1)
CENTRAL = ('Gauss I', 'Gauss II', 'Stirling', 'Bessel')
SUB = str.maketrans('0123456789-','₀₁₂₃₄₅₆₇₈₉₋')
SUP = str.maketrans('0123456789-','⁰¹²³⁴⁵⁶⁷⁸⁹⁻')


def decimal(value):
    return value if isinstance(value, Decimal) else Decimal(str(float(value)))


def product_jet(roots, target, order=0):
    """Đạo hàm thật của tích, kể cả khi target trùng một/vài nghiệm."""
    values = [ONE] + [ZERO] * order
    for degree, root in enumerate(roots, 1):
        factor = target-root
        for k in range(min(order, degree), 0, -1):
            values[k] = factor*values[k] + k*values[k-1]
        values[0] *= factor
    return values


def _multiply(coefficients, root):
    out = [ZERO] * (len(coefficients)+1)
    for j, value in enumerate(coefficients):
        out[j] -= root*value
        out[j+1] += value
    return out


def _power_text(coefficients, variable, digits):
    pieces = []
    for degree in range(len(coefficients)-1, -1, -1):
        value = coefficients[degree]
        if not value:
            continue
        text = common.fmt(abs(value), digits)
        body = text if not degree else ('' if value.copy_abs() == 1 else text+'·')+variable+(f'^{degree}' if degree > 1 else '')
        pieces.append(('-' if value < 0 else '+', body))
    if not pieces:
        return '0'
    return ('−' if pieces[0][0] == '-' else '')+pieces[0][1]+''.join(' '+sign+' '+body for sign, body in pieces[1:])


def _factor_text(roots, variable, w, fallback):
    if not roots:
        return '1'
    if len(roots) > 8:
        return fallback
    return '·'.join(variable if not root else f'({variable}{"−" if root>0 else "+"}{w.number(abs(root))})' for root in roots)


def _formula_title(w, title, latex, plain):
    """Giữ tên mục công thức cho người đọc và các bản tích hợp cũ."""
    w.formula(latex, plain)
    w.report.presentation['formulas'][-1] = (title, [latex])


def _indexed(source, order, center, divided=False):
    if divided:
        return 'f[x'+str(source).translate(SUB)+',…,x'+str(source+order).translate(SUB)+']' if order else 'y'+str(source).translate(SUB)
    index = source-center
    return 'Δ'+str(order).translate(SUP)+'y'+str(index).translate(SUB) if order else 'y'+str(index).translate(SUB)


def interpolation_trace(x, y, method, target, derivative, precision):
    """Tạo đúng các hạng của phương pháp và thực hiện phép thế trên chúng."""
    with localcontext() as context:
        context.prec = precision
        xx, yy = list(map(decimal, x)), list(map(decimal, y))
        m = len(xx)
        normalized = method not in ('Lagrange', 'Newton bất kỳ', 'Newton bất kỳ lùi')
        center = (m//2 if method == 'Gauss II' else (m-1)//2) if method in CENTRAL else (m-1 if method == 'Newton lùi' else 0)
        h = (xx[-1]-xx[0])/(m-1) if normalized and m > 1 else ONE
        origin = xx[center] if normalized else ZERO
        z = decimal(target) if target is not None else None
        tau = (z-origin)/h if z is not None and normalized else z
        divided = method.startswith('Newton bất kỳ')
        columns = [yy]
        operations = []
        for k in range(1, m):
            previous = columns[-1]
            column = []
            for i in range(m-k):
                numerator = previous[i+1]-previous[i]
                denominator = xx[i+k]-xx[i] if divided else ONE
                value = numerator/denominator
                column.append(value)
                if m <= 12:
                    operations.append((k, i, previous[i+1], previous[i], numerator,
                                       denominator, value))
            columns.append(column)
        terms = []
        factorial = ONE
        for k in range(m):
            if k:
                factorial *= k
            operands, sources = [], []
            if method == 'Lagrange':
                roots = xx[:k]+xx[k+1:]
                denominator = math.prod((xx[k]-v for v in roots), start=ONE)
                sigma = yy[k]
                beta = sigma/denominator
                source = 'y'+str(k).translate(SUB)
            else:
                denominator = factorial if normalized else ONE
                if method == 'Stirling':
                    i = center-k//2
                    sources = [i-1, i] if k % 2 else [i]
                    if not k:
                        roots = []
                    elif k % 2:
                        roots = [ZERO]+[decimal(v) for j in range(1, (k+1)//2) for v in (j, -j)]
                    else:
                        roots = [ZERO, ZERO]+[decimal(v) for j in range(1, k//2) for v in (j, -j)]
                elif method == 'Bessel':
                    i = center-k//2
                    sources = [i] if k % 2 else [i, i+1]
                    roots = [decimal(v) for j in range(k//2) for v in (-j, j+1)]
                    if k % 2:
                        roots.append(Decimal('0.5'))
                elif method in ('Gauss I', 'Gauss II'):
                    i = center-(k//2 if method == 'Gauss I' else (k+1)//2)
                    sources = [i]
                    order = [0]
                    for radius in range(1, m):
                        offsets = (radius, -radius) if method == 'Gauss I' else (-radius, radius)
                        order.extend(v for v in offsets if 0 <= center+v < m)
                    roots = [decimal(v) for v in order[:k]]
                else:
                    backward = method.endswith('lùi')
                    sources = [m-k-1 if backward else 0]
                    roots = ([decimal(-j if backward else j) for j in range(k)] if normalized
                             else (xx[::-1] if backward else xx)[:k])
                operands = [columns[k][i] for i in sources]
                sigma = sum(operands, ZERO)/len(operands)
                beta = sigma/denominator
                names = [_indexed(i, k, center if method in CENTRAL else 0, divided) for i in sources]
                source = '('+' + '.join(names)+')/2' if len(names) == 2 else names[0]
            values = product_jet(roots, tau, derivative if derivative < m else 0) if tau is not None else None
            value = beta*values[0] if values is not None else None
            slope = (beta*values[derivative]/h**derivative if derivative < m else ZERO) if values is not None else None
            if values is not None and not normalized and derivative:
                slope = beta*values[derivative] if derivative < m else ZERO
            terms.append({'k':k, 'source':source, 'source_rows':sources, 'operands':operands,
                          'sigma':sigma, 'denominator':denominator, 'beta':beta,
                          'roots':roots, 'jet':values, 'value':value, 'derivative':slope})
        values = {0:sum((t['value'] for t in terms), ZERO)} if target is not None else {}
        if target is not None and derivative:
            values[derivative] = sum((t['derivative'] for t in terms), ZERO)
        grid_deviation = max((abs(v-(xx[0]+i*h)) for i,v in enumerate(xx)), default=ZERO) if normalized else ZERO
        node_checks=[]
        if m<=33:
            for xv,yv in zip(xx,yy):
                point=(xv-origin)/h if normalized else xv
                actual=sum((t['beta']*product_jet(t['roots'],point)[0] for t in terms),ZERO)
                node_checks.append((xv,yv,actual,abs(actual-yv)))
        partition=sum((t['jet'][0]/t['denominator'] for t in terms),ZERO) if method=='Lagrange' and target is not None else None
        return {'kind':'polynomial_interpolation', 'method':method, 'status':'completed', 'failure':None,
                'x':xx, 'y':yy, 'degree':m-1, 'normalized':normalized, 'origin':origin,
                'center':center, 'h':h, 'target':z, 'tau':tau, 'order':derivative,
                'columns':columns, 'operations':operations, 'terms':terms, 'values':values,
                'precision':precision, 'grid_deviation':grid_deviation, 'comparison':[],
                'node_checks':node_checks,'partition_of_unity':partition}


def _basis(term, data, w):
    k = term['k']
    method = data['method']
    variable = 't' if data['normalized'] else 'x'
    if method == 'Stirling' and k <= 8:
        if not k:
            return '1'
        count = (k-1)//2 if k % 2 else k//2-1
        return ('t' if k % 2 else 't²')+''.join(f'(t²−{j*j})' for j in range(1,count+1))
    if method == 'Bessel' and k <= 8:
        factors = ''.join(('t(t−1)' if not j else f'(t+{j})(t−{j+1})') for j in range(k//2))
        return ('(t−1/2)' if k % 2 else '')+factors or '1'
    if method == 'Lagrange':
        fallback = f'∏(x−x_j), j≠{k}'
    elif method == 'Stirling':
        fallback = (f't·∏(t²−j²), j=1..{(k-1)//2}' if k % 2 else f't²·∏(t²−j²), j=1..{k//2-1}')
    elif method == 'Bessel':
        fallback = ('(t−1/2)·' if k % 2 else '')+f'∏[(t+j)(t−j−1)], j=0..{k//2-1}'
    elif method == 'Newton tiến':
        fallback = f'∏(t−j), j=0..{k-1}'
    elif method == 'Newton lùi':
        fallback = f'∏(t+j), j=0..{k-1}'
    else:
        fallback = f'∏({variable}−r_j), j=0..{k-1}; r: theo thứ tự kết nạp'
    return _factor_text(term['roots'], variable, w, fallback)


def _method_formula(w, data):
    method = data['method']
    formulas = {
        'Lagrange':(r'P(x)=\sum_{i=0}^{n}\frac{y_i}{\prod_{j\ne i}(x_i-x_j)}\prod_{j\ne i}(x-x_j)',
                    'P(x)=Σ D_i W_i(x), D_i=y_i/∏_(j≠i)(x_i−x_j), W_i=∏_(j≠i)(x−x_j).'),
        'Newton bất kỳ':(r'P(x)=\sum_{k=0}^{n}f[x_0,\ldots,x_k]\prod_{j=0}^{k-1}(x-x_j)',
                           'P(x)=Σ f[x_0,…,x_k]·∏_(j=0)^(k−1)(x−x_j); không chia k!.'),
        'Newton bất kỳ lùi':(r'P(x)=\sum_{k=0}^{n}f[x_{n-k},\ldots,x_n]\prod_{j=0}^{k-1}(x-x_{n-j})',
                               'P(x)=Σ f[x_(n−k),…,x_n]·∏_(j=0)^(k−1)(x−x_(n−j)); không chia k!.'),
        'Newton tiến':(r'P(x_0+th)=\sum_{k=0}^{n}\frac{\Delta^k y_0}{k!}\prod_{j=0}^{k-1}(t-j)',
                         'P(x_0+th)=Σ Δ^k y_0·∏_(j=0)^(k−1)(t−j)/k!.'),
        'Newton lùi':(r'P(x_n+th)=\sum_{k=0}^{n}\frac{\Delta^k y_{n-k}}{k!}\prod_{j=0}^{k-1}(t+j)',
                        'P(x_n+th)=Σ Δ^k y_(n−k)·∏_(j=0)^(k−1)(t+j)/k!; Δ^k y_(n−k)=∇^k y_n.'),
        'Gauss I':(r'Q(t)=\sum_{k=0}^{n}\frac{\Delta^k y_{-\lfloor k/2\rfloor}}{k!}B_k(t)',
                    'Q(t)=Σ Δ^k y_(−floor(k/2)) B_k(t)/k!; kết nạp 0,+1,−1,+2,−2,…'),
        'Gauss II':(r'Q(t)=\sum_{k=0}^{n}\frac{\Delta^k y_{-\lceil k/2\rceil}}{k!}B_k(t)',
                     'Q(t)=Σ Δ^k y_(−ceil(k/2)) B_k(t)/k!; kết nạp 0,−1,+1,−2,+2,…'),
    }
    if method in formulas:
        latex, plain = formulas[method]
        _formula_title(w, 'Công thức '+method, latex, plain)
    elif method == 'Stirling':
        w.formula(r'Q(t)=y_0+S_o(t)+S_e(t)', 'Q(t)=y_0+S_lẻ(t)+S_chẵn(t).')
        w.formula(r'S_o(t)=\sum_{r=0}^{N-1}\frac{\Delta^{2r+1}y_{-r-1}+\Delta^{2r+1}y_{-r}}{2(2r+1)!}\,t\prod_{j=1}^{r}(t^2-j^2)',
                  'Hạng lẻ 2r+1: trung bình Δ^(2r+1)y_(−r−1), Δ^(2r+1)y_(−r), chia (2r+1)!, nhân t·∏(t²−j²), j=1..r.')
        w.formula(r'S_e(t)=\sum_{r=1}^{N}\frac{\Delta^{2r}y_{-r}}{(2r)!}\,t^2\prod_{j=1}^{r-1}(t^2-j^2)',
                  'Hạng chẵn 2r: Δ^(2r)y_(−r)/(2r)! nhân t²·∏(t²−j²), j=1..r−1.')
    else:
        w.formula(r'Q(t)=\sum_{r=0}^{N}\left[\frac{\Delta^{2r}y_{-r}+\Delta^{2r}y_{-r+1}}{2(2r)!}E_r(t)+\frac{\Delta^{2r+1}y_{-r}}{(2r+1)!}(t-\frac{1}{2})E_r(t)\right]',
                  'Bessel: hạng chẵn lấy trung bình hai sai phân, hạng lẻ lấy một sai phân và nhân thêm (t−1/2).')
        w.formula(r'E_0=1,\qquad E_r(t)=\prod_{j=0}^{r-1}(t+j)(t-j-1)',
                  'E_0=1; E_r=∏[(t+j)(t−j−1)], j=0..r−1; số mốc=2N+2.')
    w.text('Tích rỗng bằng 1. Mỗi hạng được lấy đủ đến bậc tối đa; hệ số bằng 0 vẫn được giữ trong bảng.')


def _numeric_expression(w, data):
    """Ghép từ chính beta/roots trong vết tính; không dùng hệ số float cũ."""
    from .math_view import split_equation
    variable = 't' if data['normalized'] else 'x'
    if len(data['x']) > 17:
        w.formula(r'Q(t)=\sum_{k=0}^{n}\beta_k B_k(t)' if data['normalized'] else r'P(x)=\sum_{k=0}^{n}\beta_k B_k(x)',
                  'Đa thức được xác định đầy đủ bởi tất cả β_k và B_k trong bảng; không tự giảm bậc để khai triển.')
        return
    terms, coefficients = [], [ZERO]*len(data['x'])
    for term in data['terms']:
        if not term['beta']:
            continue
        k=term['k']
        if data['method']=='Stirling' and k:
            count=(k-1)//2 if k%2 else k//2-1
            factors=('t' if k%2 else 't^2')+''.join(rf'(t^2-{j*j})' for j in range(1,count+1))
        elif data['method']=='Bessel':
            factors=(r'(t-\frac{1}{2})' if k%2 else '')+''.join(('t(t-1)' if not j else rf'(t+{j})(t-{j+1})') for j in range(k//2))
        else:
            factors = ''.join(variable if not r else rf'({variable}{"-" if r>0 else "+"}{w.tex(abs(r))})' for r in term['roots'])
        if data['normalized'] and k>1:
            coefficient=rf'\frac{{{w.tex(abs(term["sigma"]))}}}{{{k}!}}'
        elif data['method']=='Lagrange' and term['denominator']!=1:
            coefficient=rf'\frac{{{w.tex(abs(term["sigma"]))}}}{{{w.tex(abs(term["denominator"]))}}}'
        else:
            coefficient=w.tex(abs(term['beta']))
        body = coefficient+(r'\,'+factors if factors else '')
        terms.append(('-' if term['beta'] < 0 else '+', body))
        basis = [ONE]
        for root in term['roots']:
            basis = _multiply(basis, root)
        for k, value in enumerate(basis):
            coefficients[k] += term['beta']*value
    rhs = (('-' if terms[0][0] == '-' else '')+terms[0][1]+''.join(' '+s+' '+body for s,body in terms[1:])) if terms else '0'
    lhs = 'Q(t)' if data['normalized'] else 'P(x)'
    plain = lhs+' = '+' + '.join(f'({w.number(t["beta"])})·{_basis(t,data,w)}' for t in data['terms'])
    for i, latex in enumerate(split_equation(lhs, rhs, width=78)):
        w.formula(latex, plain if not i else 'Tiếp các hạng của cùng đa thức.')
    data['power_coefficients'] = coefficients
    if data['normalized']:
        label = 'P(x_n+th)' if data['method'] == 'Newton lùi' else 'P(x_0+th)'
        # Dạng tích là kết quả chính; dạng khai triển theo t để kiểm tay.
        from .math_view import poly_latex
        from numpy.polynomial import Polynomial
        as_float = np.asarray([float(v) for v in coefficients])
        if np.all(np.isfinite(as_float)):
            for latex in split_equation(label, poly_latex(Polynomial(as_float), 't'), width=78):
                _formula_title(w, 'Đa thức theo biến t', latex,
                               label+' = '+_power_text(coefficients, 't', w.digits))


def present_interpolation(report, x, y, method, target, derivative, original_rows, used_ids):
    precision = report.value.precision
    data = interpolation_trace(x, y, method, target, derivative, precision)
    data['input_rows'] = original_rows
    data['used_ids'] = list(map(int, used_ids))
    legacy = {k:report.presentation[k] for k in ('difference', 'after_tables', 'after_tables_text', 'compact_polynomial') if k in report.presentation}
    # Phép đánh giá Newton lồng hiện có là đối chiếu ổn định, không thay công
    # thức đã chọn. Lệch do nhận lưới gần đều hoặc triệt tiêu được công khai.
    if target is not None:
        for order, value in data['values'].items():
            stable = decimal(report.value.deriv(order)(target))
            gap = abs(stable-value)
            scale = max(abs(stable), abs(value), Decimal('1e-300'))
            data['comparison'].append({'order':order, 'formula':value, 'stable':stable, 'gap':gap,
                                       'passed':gap <= Decimal('1e-10')*scale+Decimal('1e-25')})
    w = ReportBuilder(report, display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution'] = data
    terms, m = data['terms'], len(x)
    normalized = data['normalized']
    with localcontext() as context:
        context.prec = precision
        with w.group('section', 'Kết quả của lượt tính'):
            if target is None:
                w.text(f'Đã dựng {method} từ {m} mốc; bậc không quá {m-1}. Chưa nhập điểm nên chưa thế giá trị.')
            else:
                for order, value in data['values'].items():
                    label = 'P' if not order else rf'P^{{({order})}}'
                    w.formula(rf'{label}({w.tex(data["target"])})={w.tex(value)}',
                              f'P^({order})({w.number(data["target"])}) = {w.number(value)}')
            w.text('Kết quả của đa thức nội suy trên tập mốc công bố dưới đây. Chưa có cận sai số với hàm thật nếu chưa biết đạo hàm cao hơn.', 'muted')
        with w.group('section', '1. Đọc dữ liệu, chọn mốc và kiểm tra điều kiện'):
            with w.group('columns'):
                with w.group('panel', 'Yêu cầu và điều kiện áp dụng'):
                    w.text(f'Phương pháp {method}; dùng {m}/{len(original_rows)} mốc, bậc tối đa {m-1}; cấp đạo hàm yêu cầu {derivative}.')
                    w.text('Các cặp hữu hạn, x phân biệt và được sắp tăng; ID dòng nguồn bắt đầu từ 0. Không tự bỏ hoặc gộp mốc.')
                    if m < len(original_rows):
                        w.text('Lưới đều: chọn cửa sổ liên tiếp có tâm gần điểm tính nhất, hòa chọn bên trái. Mốc bất kỳ: chọn các mốc gần điểm tính nhất rồi sắp tăng.')
                    else:
                        w.text('Dùng toàn bộ tập mốc đã nhập; không tự giảm bậc.')
                    if method == 'Stirling':
                        w.text(f'Số mốc lẻ 2N+1={m}, N={(m-1)//2}; gốc là mốc giữa. Khoảng |t|≤1/4 là gợi ý thuận lợi, không phải điều kiện cấm.')
                    elif method == 'Bessel':
                        w.text(f'Số mốc chẵn 2N+2={m}, N={(m-2)//2}; gốc là mốc trái của cặp giữa.')
                    if normalized and m > 1:
                        gaps = [data['x'][i+1]-data['x'][i] for i in range(m-1)]
                        data['grid_steps'] = gaps
                        w.text('Đã kiểm tra các bước: rtol=10⁻⁸, atol=0 theo bước h, không theo độ lớn x. h trình bày lấy từ hai đầu của tập chọn.')
                        w.text(f'h={w.number(data["h"])}; độ lệch lớn nhất so với x_đầu+i·h: {w.number(data["grid_deviation"])}.')
                    elif m == 1:
                        w.text('Một mốc cho đa thức hằng; không cần bước lưới hay đổi biến.')
                    else:
                        w.text('Mốc bất kỳ: không yêu cầu cách đều.')
                with w.group('panel', 'Tập mốc thực sự sử dụng'):
                    offset = data['center'] if method in CENTRAL else 0
                    w.table('Mốc tính và ánh xạ nguồn', ['ID nguồn', 'j', 'x_j', 'y_j', '|x_j−z|'],
                            ((used_ids[i], i-offset, decimal(x[i]), decimal(y[i]), abs(decimal(x[i])-data['target']) if target is not None else None) for i in range(m)))
            if m < len(original_rows) or used_ids != list(range(m)):
                with w.details('Toàn bộ dữ liệu nhập và thứ tự dòng nguồn'):
                    w.table('Dữ liệu nguồn', ['ID nguồn', 'x', 'y'], original_rows)
            if target is not None and not x[0] <= target <= x[-1]:
                w.text('Điểm tính nằm ngoài đoạn của tập mốc đã chọn: đang ngoại suy.', 'warning')
        with w.group('section', '2. Ký hiệu, đổi biến và công thức'):
            if normalized and m > 1:
                origin_label = 'x_n' if method == 'Newton lùi' else 'x_0'
                w.formula(rf'{origin_label}={w.tex(data["origin"])},\quad h={w.tex(data["h"])},\quad t=\frac{{x-{origin_label}}}{{h}}',
                          f'{origin_label}={w.number(data["origin"])}; h={w.number(data["h"])}; t=(x−{origin_label})/h; Q(t)=P({origin_label}+ht).')
                if target is not None:
                    w.formula(rf'\bar t=\frac{{{w.tex(data["target"])}-({w.tex(data["origin"])})}}{{{w.tex(data["h"])}}}={w.tex(data["tau"])}',
                              f'Tại z={w.number(data["target"])}, t_z={w.number(data["tau"])}.')
                if method in CENTRAL:
                    w.text('Chỉ số j đếm quanh gốc giữa, không phải ID dòng của toàn bộ bảng nhập.')
            _method_formula(w, data)
            if method in ('Gauss I', 'Gauss II'):
                c = data['center'];order = [0]
                for radius in range(1, m):
                    order.extend(v for v in ((radius,-radius) if method == 'Gauss I' else (-radius,radius)) if 0 <= c+v < m)
                w.table('Thứ tự kết nạp và nhân tử', ['lượt', 'j quanh gốc', 'ID nguồn', 'x_j'],
                        ((rank,j,used_ids[c+j],x[c+j]) for rank,j in enumerate(order)))
                w.formula(r'B_0=1,\quad B_{k+1}(t)=B_k(t)(t-r_k)', 'r_k là độ lệch j trong thứ tự kết nạp; B_(k+1)=B_k(t−r_k).')
        with w.group('section', '3. Lập bảng trung gian theo từng cấp'):
            if method != 'Lagrange':
                divided = method.startswith('Newton bất kỳ')
                if divided:
                    w.formula(r'D_{i,0}=y_i,\quad D_{i,k}=\frac{D_{i+1,k-1}-D_{i,k-1}}{x_{i+k}-x_i}',
                              'Tỉ sai phân: cấp k lấy hiệu hai ô cấp k−1 rồi chia (x_(i+k)−x_i). Không chia thêm k!.')
                else:
                    w.formula(r'\Delta^0y_i=y_i,\quad \Delta^ky_i=\Delta^{k-1}y_{i+1}-\Delta^{k-1}y_i',
                              'Sai phân: Δ^0y_i=y_i; Δ^ky_i=Δ^(k−1)y_(i+1)−Δ^(k−1)y_i.')
                w.text('Mỗi ô cùng hàng mốc bắt đầu. Ô trống ngoài tam giác không phải số 0; các ô dùng trong công thức được đánh dấu.')
                offset = data['center'] if method in CENTRAL else 0
                used = [(i,k+2) for t in terms for i in t['source_rows'] for k in [t['k']]]
                w.table('Bảng tỉ sai phân' if divided else 'Bảng sai phân tiến đầy đủ',
                        ['j','xⱼ','yⱼ']+[('D' if divided else 'Δ')+str(k).translate(SUP) for k in range(1,m)],
                        ((i-offset,x[i],y[i])+tuple(data['columns'][k][i] if i < m-k else None for k in range(1,m)) for i in range(m)),
                        used_cells=used)
                if data['operations']:
                    with w.details('Từng phép tính trong các cấp của bảng'):
                        w.table('Lập từng ô', ['k','i bắt đầu','ô phải cấp k−1','ô trái cấp k−1','hiệu','mẫu chia','ô cấp k'],data['operations'])
                else:
                    w.text('Bảng lớn giữ đầy đủ mọi cấp và mọi ô; mỗi cấp k có m−k phép tính theo truy hồi trên. Bản xem giới hạn cột có ghi rõ; bản xuất giữ đủ.', 'muted')
            else:
                w.text('Dựng W_i=∏_(j≠i)(x−x_j), d_i=∏_(j≠i)(x_i−x_j), D_i=y_i/d_i. Dấu của mỗi hiệu được giữ nguyên.')
                w.table('Mẫu số và hệ số Lagrange', ['i','xᵢ','yᵢ','dᵢ','Dᵢ'],
                        ((t['k'],x[t['k']],t['sigma'],t['denominator'],t['beta']) for t in terms))
                if not legacy.get('compact_polynomial'):
                    with w.details('Bảng tích, thương và hệ số khai triển Lagrange'):
                        w.text('Bảng tích dùng hệ số bậc tăng từ hệ số tự do; bảng thương/hệ số cuối dùng bậc giảm, theo nhãn của bảng gốc.')
                        w.stack[-1].append({'kind':'table','index':0})
        with w.group('section', '4. Lấy hệ số, ghép từng hạng và dựng đa thức'):
            w.text('Duyệt hạng k=0,…,n, lấy đúng ô nguồn, chia đúng mẫu một lần, nhân cơ sở rồi cộng. Đây là các bước tính hữu hạn, không phải vòng hội tụ.')
            w.table('Các hạng của công thức đã chọn', ['k','nguồn σₖ','các ô nguồn','σₖ','mẫu chia','βₖ','Bₖ'],
                    ((t['k'],t['source'],'; '.join(w.number(v) for v in t['operands']),t['sigma'],t['denominator'],t['beta'],_basis(t,data,w)) for t in terms),
                    text_columns=(1,2,6))
            _numeric_expression(w, data)
            if method != 'Lagrange' and len(report.tables) > 1 and not legacy.get('compact_polynomial'):
                with w.details('Bảng tích khai triển — hệ số theo bậc giảm dần'):
                    w.text('Các tích cơ sở chưa chia giai thừa và chưa nhân sai phân; không chia k! thêm lần nữa khi đã dùng β_k.')
                    w.stack[-1].append({'kind':'table','index':1})
        if target is not None:
            with w.group('section', '5. Thế số và cộng kết quả'):
                with w.group('columns'):
                    with w.group('panel', 'Giá trị của đa thức'):
                        total = ZERO;rows = []
                        for t in terms:
                            total += t['value'];rows.append((t['k'],t['jet'][0],t['value'],total))
                        w.table('Đóng góp từng hạng vào P(z)', ['k','Bₖ tại điểm tính','βₖ Bₖ','tổng'],rows)
                        w.formula(rf'P({w.tex(data["target"])})={w.tex(total)}',f'P({w.number(data["target"])})={w.number(total)}.')
                    if derivative:
                        with w.group('panel', f'Đạo hàm cấp {derivative} theo x'):
                            if normalized:
                                w.formula(rf'P^{{({derivative})}}(z)=\frac{{Q^{{({derivative})}}(\bar t)}}{{h^{{{derivative}}}}}',
                                          f'Đạo hàm theo x: chia đạo hàm theo t cho h^{derivative}.')
                            total = ZERO;rows = []
                            for t in terms:
                                raw = t['jet'][derivative] if derivative < m else ZERO
                                total += t['derivative'];rows.append((t['k'],raw,t['beta']*raw,t['derivative'],total))
                            order_label='′' if derivative==1 else '″' if derivative==2 else '⁽'+str(derivative).translate(SUP)+'⁾'
                            w.table('Đóng góp từng hạng vào đạo hàm', ['k','Bₖ'+order_label, 'βₖ·Bₖ'+order_label, 'đóng góp theo x','tổng'],rows)
                            if normalized:
                                raw_total=sum((row[2] for row in rows),ZERO)
                                data['raw_derivative']=raw_total
                                w.formula(rf'Q^{{({derivative})}}(\bar t)={w.tex(raw_total)}',
                                          f'Đạo hàm theo t: Q^({derivative})(t_z)={w.number(raw_total)}.')
                                w.formula(rf'P^{{({derivative})}}({w.tex(data["target"])})=\frac{{{w.tex(raw_total)}}}{{({w.tex(data["h"])})^{{{derivative}}}}}={w.tex(total)}',
                                          f'Đổi sang x: P^({derivative})({w.number(data["target"])})={w.number(raw_total)}/({w.number(data["h"])})^{derivative}={w.number(total)}.')
                            else:
                                w.formula(rf'P^{{({derivative})}}({w.tex(data["target"])})={w.tex(total)}',f'P^({derivative})({w.number(data["target"])})={w.number(total)}.')
                            if derivative >= m:
                                w.text('Cấp đạo hàm vượt bậc tối đa của mô hình nên bằng 0; điều này không chứng minh đạo hàm hàm thật bằng 0.')
                if derivative:
                    with w.details('Thuật toán đạo hàm cơ sở tích, kể cả tại nghiệm của tích'):
                        w.text('Khởi tạo g_0=1, g_l=0 (l>0). Khi nhân (t−r), cập nhật từ cấp cao xuống thấp: g_l←(t_z−r)g_l+l·g_(l−1), rồi g_0←(t_z−r)g_0. Không chia cho t_z−r nên không lỗi khi trùng mốc.')
                        for t in terms:
                            w.text(f'k={t["k"]}: {_basis(t,data,w)}; đạo hàm cơ sở cấp {derivative} = '+w.number(t['jet'][derivative] if derivative < m else ZERO)+'.')
        with w.group('section', '6. Đối chiếu và phạm vi kết luận'):
            if data['node_checks']:
                maximum=max(row[3] for row in data['node_checks'])
                w.text('Sai lệch lớn nhất P(x_i)−y_i theo chính công thức đã chọn: '+w.number(maximum)+'.')
                with w.details('Kiểm tra đa thức tại từng mốc đã chọn'):
                    w.table('Đối chiếu điều kiện nội suy',['x_i','y_i','P(x_i)','|P(x_i)−y_i|'],data['node_checks'])
            if data['partition_of_unity'] is not None:
                w.text('Kiểm tra cơ sở Lagrange: ΣL_i(z)='+w.number(data['partition_of_unity'])+' (giá trị cần là 1).')
            if data['comparison']:
                w.table('Công thức đã chọn và Horner Newton ổn định trên các mốc nhập', ['cấp','tổng theo công thức','Horner Newton','độ chênh','đối chiếu'],
                        ((r['order'],r['formula'],r['stable'],r['gap'],r['passed']) for r in data['comparison']))
                if not all(r['passed'] for r in data['comparison']):
                    data['status'] = 'numerical_warning'
                    w.text('Hai cách tính lệch đáng kể: có thể do lưới chỉ gần đều trong dung sai hoặc triệt tiêu ở bậc cao. Chưa coi các chữ số của tổng hạng là được bảo đảm; kiểm tra tập mốc và đổi đơn vị khi cần.', 'warning')
            w.text(f'Tính trung gian với {precision} chữ số; số trong bảng chỉ làm tròn khi hiển thị. Dạng tích là mô hình chính, không bắt buộc khai triển theo x.', 'muted')
            w.text('Nếu dữ liệu chính xác và |f^(m)|≤M_m trên đoạn chứa m mốc và điểm tính: |f(z)−P(z)|≤M_m·|∏(z−x_i)|/m!. Chưa được cho M_m thì chưa có cận sai số hàm thật.')
            w.text('Sai lệch tại mốc chỉ kiểm tra nội suy; không là cận giữa mốc. Đạo hàm cần cận riêng, không đạo hàm phần dư chứa ξ như hằng số. Nhiều mốc/bậc cao có thể khuếch đại nhiễu.', 'muted')
    w.finish()
    report.presentation.update(legacy)
    return report


def present_horner(report, original, target, order, passes):
    """Dựng lời giải từ đúng các lượt nhân/cộng đã tạo ra số dư."""
    data = {'kind':'horner', 'status':'completed', 'failure':None,
            'coefficients':list(map(decimal, original)), 'target':decimal(target),
            'order':order, 'degree':len(passes[0]['input'])-1, 'passes':passes}
    w = ReportBuilder(report, display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution'] = data
    with w.group('section','Kết quả'):
        for p in passes:
            w.formula(rf'P^{{({p["r"]})}}({w.tex(data["target"])})={w.tex(p["derivative"])}',
                      f'P^({p["r"]})({w.number(data["target"])})={w.number(p["derivative"])}.')
        if order > data['degree']:
            w.text(f'Mọi đạo hàm cấp lớn hơn {data["degree"]} đều bằng 0, gồm cấp {order} đã yêu cầu.')
    with w.group('section','1. Đọc đa thức và yêu cầu'):
        w.text('Hệ số đầu vào theo bậc giảm: '+', '.join(w.number(v) for v in original)+'. Giữ các số 0 ở giữa/cuối vì chúng xác định đúng lũy thừa.')
        w.text('P(x) = '+_power_text(list(reversed(data['coefficients'])), 'x', w.digits))
        w.text(f'Điểm c={w.number(data["target"])}; lấy đạo hàm đến cấp {order}; bậc thực={data["degree"]}.')
        if len(original) != data['degree']+1:
            w.text('Các hệ số 0 đầu dãy không tăng bậc thực; bản nhập vẫn được giữ ở trên.')
    with w.group('section','2. Công thức Horner và ý nghĩa các lượt'):
        w.formula(r'b_0=A_0,\qquad b_j=A_j+c\,b_{j-1}', 'b_0=A_0; b_j=A_j+c·b_(j−1).')
        w.formula(r'Q_r(x)=(x-c)Q_{r+1}(x)+s_r,\quad Q_0=P', 'Mỗi lượt chia Q_r cho x−c, giữ thương Q_(r+1) cho lượt sau, số dư là s_r.')
        w.formula(r'P(x)=\sum_{r=0}^{n}s_r(x-c)^r,\qquad P^{(r)}(c)=r!s_r', 'Chia lặp tạo hệ số Taylor s_r; đạo hàm cấp r bằng r!·s_r, không phải chỉ số dư.')
        w.text('Lượt r+1 tính s_r. Đây là phép tính hữu hạn; không cần dung sai hay điều kiện hội tụ.')
    with w.group('section','3. Các lượt chia Horner — từng phép nhân và cộng'):
        for start in range(0,len(passes),2):
            with w.group('columns'):
                for p in passes[start:start+2]:
                    with w.group('panel',f'Lượt {p["r"]+1}: Q_{p["r"]}, lấy s_{p["r"]}'):
                        w.table('Nhân–cộng trong lượt '+str(p['r']+1), ['j','bậc','Aⱼ','bⱼ₋₁','c·bⱼ₋₁','bⱼ'],
                                ((s['j'],len(p['input'])-1-s['j'],s['input'],s['previous'],s['product'],s['accumulated']) for s in p['steps']))
                        w.text('Thương theo bậc giảm: '+(', '.join(w.number(v) for v in p['quotient']) or '0')+'.')
                        w.formula(rf's_{{{p["r"]}}}={w.tex(p["remainder"])},\quad P^{{({p["r"]})}}(c)={p["r"]}!\,s_{{{p["r"]}}}={w.tex(p["derivative"])}',
                                  f's_{p["r"]}={w.number(p["remainder"])}; {p["r"]}!·s_{p["r"]}={w.number(p["derivative"])}.')
                        if p['quotient']:
                            w.text('Bỏ phần tử số dư; dùng toàn bộ dãy thương này làm hệ số A_j ở lượt sau.')
                        else:
                            w.text('Đã đến đa thức hằng; không cần chia tiếp để lấy các đạo hàm bằng 0.')
    with w.group('section','4. Tổng kết và kiểm tra'):
        w.table('Số dư và đạo hàm', ['r','s_r','r!','P^(r)(c)'],
                ((p['r'],p['remainder'],p['factorial'],p['derivative']) for p in passes))
        w.text('Mỗi dãy b bỏ phần tử cuối là thương; phần tử cuối là số dư. Đẳng thức chia Q_r=(x−c)Q_(r+1)+s_r đúng tại từng lượt.')
        if len(passes) == data['degree']+1:
            w.text('Đã có đủ hệ số Taylor: '+', '.join(f's_{p["r"]}={w.number(p["remainder"])}' for p in passes)+'.')
        w.text('Phép tính dùng hệ số đầy đủ, bảng làm tròn ở khâu hiển thị. Kết quả thuộc đa thức đã nhập; độ chính xác của hệ số dữ liệu được xét riêng.', 'muted')
    return w.finish()


def present_derivative(report, data):
    w = ReportBuilder(report, display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution'] = data
    z,p,s = data['target'],data['degree'],data['order']
    with w.group('section','Kết quả đạo hàm từ bảng'):
        w.formula(rf'f^{{({s})}}({w.tex(z)})\approx P^{{({s})}}({w.tex(z)})={w.tex(data["value"])}',
                  f'f^({s})({w.number(z)}) ≈ P^({s})({w.number(z)}) = {w.number(data["value"])}.')
        w.text('Đây là đạo hàm của đa thức nội suy trên tập mốc được chọn. Chưa có cận sai số với hàm thật nếu thiếu giả thiết đạo hàm cao hơn.', 'muted')
    with w.group('section','1. Chọn mốc và xác định bài toán'):
        with w.group('columns'):
            with w.group('panel','Thông số và quy tắc chọn'):
                w.text(f'Bậc p={p}, dùng p+1={p+1} mốc, cấp đạo hàm s={s}, điểm z={w.number(z)}.')
                w.text('Tìm mốc gần z nhất, hòa chọn bên trái; lấy cửa sổ liên tiếp p+1 mốc quanh hàng đó và dịch vào bảng nếu chạm biên. Trên lưới không đều, đây không nhất thiết là các mốc gần nhất.')
                w.text(f'Hàng gần nhất trong dãy x đã sắp: {data["nearest"]}; cửa sổ bắt đầu {data["start"]}; ID nguồn: {data["used_ids"]}.')
                w.text('Trọng số Lagrange dùng được cho mốc bất kỳ; không ép lưới đều.')
            with w.group('panel','Các cặp dùng trong công thức'):
                w.table('Tập mốc đạo hàm', ['i','ID nguồn','x_i','y_i'],
                        ((i,data['used_ids'][i],x,y) for i,(x,y) in enumerate(zip(data['x'],data['y']))))
        if z < data['x'][0] or z > data['x'][-1]:
            w.text('Điểm tính ngoài đoạn của tập đã chọn: đạo hàm của đa thức ngoại suy.', 'warning')
    with w.group('section','2. Dẫn công thức từ nội suy Lagrange'):
        w.formula(r'L_i(x)=\prod_{j\ne i}\frac{x-x_j}{x_i-x_j},\quad w_i=L_i^{(s)}(z)',
                  'L_i(x)=∏_(j≠i)(x−x_j)/(x_i−x_j); w_i=L_i^(s)(z).')
        w.formula(r'P^{(s)}(z)=\sum_{i=0}^{p}w_i y_i', 'Lấy đạo hàm từng đa thức cơ sở rồi cộng w_i·y_i.')
        w.text('Đặt x=z+u. a_l là hệ số u^l của ∏_(j≠i)(z−x_j+u), chưa nhân l!. Khi nhân (v+u), cập nhật l từ s xuống 1: a_l←v·a_l+a_(l−1), rồi a_0←v·a_0. Mẫu d_i=∏_(j≠i)(x_i−x_j).')
        w.formula(r'w_i=\frac{s!\,a_s}{d_i}', 'w_i=s!·a_s/d_i. Không chia cho z−x_j nên dùng được khi điểm tính trùng mốc.')
        if p in (1,2):
            h=(data['x'][-1]-data['x'][0])/p
            even=all(v==data['x'][0]+i*h for i,v in enumerate(data['x']))
            position=next((i for i,v in enumerate(data['x']) if v==z),None)
            familiar={
                (1,1,0):(r'D=\frac{y_1-y_0}{h}', 'Hai điểm tiến: D=(y_1−y_0)/h.', 'M₂·h/2'),
                (1,1,1):(r'D=\frac{y_1-y_0}{h}', 'Hai điểm lùi: D=(y_1−y_0)/h.', 'M₂·h/2'),
                (2,1,0):(r'D=\frac{-3y_0+4y_1-y_2}{2h}', 'Ba điểm tiến: D=(−3y_0+4y_1−y_2)/(2h).', 'M₃·h²/3'),
                (2,1,1):(r'D=\frac{y_2-y_0}{2h}', 'Ba điểm giữa: D=(y_2−y_0)/(2h).', 'M₃·h²/6'),
                (2,1,2):(r'D=\frac{3y_2-4y_1+y_0}{2h}', 'Ba điểm lùi: D=(3y_2−4y_1+y_0)/(2h).', 'M₃·h²/3'),
                (2,2,1):(r'D=\frac{y_0-2y_1+y_2}{h^2}', 'Ba điểm giữa cấp 2: D=(y_0−2y_1+y_2)/h².', 'M₄·h²/12'),
            }
            canonical=familiar.get((p,s,position)) if even else None
            if canonical:
                latex,plain,bound=canonical
                w.formula(latex,plain)
                w.text(f'Lưới này cho công thức quen thuộc với h={w.number(h)}. Cận sai số tương ứng là {bound}, chỉ khi M là cận đạo hàm đúng cấp trên đoạn liên quan; chưa có M thì chưa có cận số.')
    with w.group('section','3. Dựng từng trọng số'):
        first = data['weights_trace'][0]
        w.text(f'Ví dụ i=0: d_0={w.number(first["denominator"])}; hệ số a_{s}={w.number(first["coefficient"])}; {s}!={w.number(first["factorial"])}; w_0={w.number(first["weight"])}.')
        with w.details('Từng phép nhân cơ sở để tạo trọng số — đầy đủ các mốc'):
            for trace in data['weights_trace']:
                w.table(f'Lập trọng số i={trace["i"]}', ['j','v=z−x_j','mẫu tích lũy']+[f'a_{k}' for k in range(s+1)],
                        ((row['j'],row['factor'],row['denominator'],*row['coefficients']) for row in trace['steps']))
    with w.group('section','4. Nhân trọng số với tung độ và cộng'):
        w.table('Trọng số và đóng góp đạo hàm', ['i','x_i','y_i','d_i','a_s','w_i','w_i y_i','tổng'],
                ((t['i'],data['x'][t['i']],data['y'][t['i']],t['denominator'],t['coefficient'],t['weight'],t['contribution'],t['total']) for t in data['weights_trace']))
        if len(data['x']) <= 9:
            w.text('Thế số: '+ ' + '.join(f'({w.number(t["weight"])})·({w.number(data["y"][t["i"]])})' for t in data['weights_trace'])+' = '+w.number(data['value'])+'.')
    with w.group('section','5. Kiểm tra moment và kết luận sai số'):
        w.formula(r'\sum_i w_i(x_i-z)^r=s!\ (r=s),\qquad =0\ (0\leq r\leq p,\ r\ne s)',
                  'Moment quanh z: tổng w_i(x_i−z)^r bằng s! khi r=s, bằng 0 với các r khác từ 0 đến p.')
        w.table('Đối chiếu độ chính xác trên đa thức bậc ≤p', ['r','moment tính','giá trị cần','độ lệch','đạt'],
                ((r['r'],r['value'],r['expected'],r['gap'],r['passed']) for r in data['moments']))
        w.text('Độ lệch moment được so với thang của các hạng ở độ chính xác trung gian; không dùng một ngưỡng tuyệt đối cho mọi đơn vị. Kiểm tra này không chứng minh dữ liệu không nhiễu.')
        w.text('Nếu f đủ trơn và |f^(p+1)|≤M_(p+1) trên đoạn chứa z và các mốc, cận Taylor: |f^(s)(z)−Σw_i f(x_i)|≤M_(p+1)/(p+1)!·Σ|w_i|·|x_i−z|^(p+1). Đây có thể là cận thô; chưa biết M thì chưa có cận số.')
        w.text('Nếu |δy_i|≤η_i thì sai số do dữ liệu ≤Σ|w_i|η_i. Không đạo hàm phần dư chứa ξ như hằng số; giảm bước có thể khuếch đại nhiễu.', 'muted')
    return w.finish()


def present_selection(report,x,y,target,count,equal,chosen,source_ids):
    data={'kind':'node_selection','status':'completed','failure':None,'target':target,'count':count,
          'equal_grid':equal,'used_ids':[int(source_ids[i]) for i in chosen]}
    w=ReportBuilder(report,display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution']=data
    with w.group('section','1. Xác định dữ liệu và cách chọn'):
        w.text(f'Có {len(x)} cặp đã sắp tăng x, cần chọn {count} mốc quanh z={w.number(target)}. Giữ nguyên từng cặp và ID nguồn bắt đầu từ 0.')
        if equal:
            w.text('Lưới đều: duyệt các cửa sổ liên tiếp đủ K mốc, tính tâm (x_trái+x_phải)/2 và khoảng cách đến z; chọn khoảng cách nhỏ nhất, hòa chọn cửa sổ bên trái.')
            scores=[(j,j+count-1,(x[j]+x[j+count-1])/2,abs((x[j]+x[j+count-1])/2-target)) for j in range(len(x)-count+1)]
            data['window_scores']=scores
            with w.details('Quá trình duyệt toàn bộ cửa sổ'):
                w.table('Các cửa sổ ứng viên',['hàng đầu','hàng cuối','tâm cửa sổ','|tâm−z|'],scores,
                        used_cells=[(int(chosen[0]),j) for j in range(4)])
        else:
            w.text('Mốc bất kỳ: xếp theo |x_i−z| tăng, hòa theo thứ tự x tăng; lấy K mốc đầu rồi sắp tập chọn tăng x. Dùng Lagrange hoặc Newton tỉ sai phân cho tập này.')
            ranking=np.argsort(abs(x-target),kind='stable')
            with w.details('Thứ tự khoảng cách của các mốc'):
                w.table('Xếp hạng mốc',['hạng','ID nguồn','x','y','|x−z|'],
                        ((rank,int(source_ids[i]),x[i],y[i],abs(x[i]-target)) for rank,i in enumerate(ranking)))
    with w.group('section','2. Tập mốc được chọn'):
        w.table('Mốc dùng cho bước tính tiếp',['ID nguồn','x','y','|x−z|'],
                ((int(source_ids[i]),x[i],y[i],abs(x[i]-target)) for i in chosen))
        w.text('Dãy x: '+' '.join(w.number(x[i]) for i in chosen))
        w.text('Dãy y: '+' '.join(w.number(y[i]) for i in chosen))
        w.text(f'Tập chọn cho đa thức bậc không quá {count-1}; số mốc không phải số vòng hội tụ.')
        if target<x[chosen[0]] or target>x[chosen[-1]]:
            w.text('Điểm tính ngoài đoạn của tập chọn: nếu đánh giá đa thức thì là ngoại suy.', 'warning')
    return w.finish()


def present_chebyshev(report,degree,a,b,angles,raw,sort_order):
    data={'kind':'chebyshev_nodes','status':'completed','failure':None,'degree':degree,
          'a':a,'b':b,'angles':list(angles),'raw_nodes':list(raw),'sort_order':list(map(int,sort_order))}
    w=ReportBuilder(report,display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution']=data
    with w.group('section','1. Bài toán chọn mốc'):
        w.text(f'Sinh m=n+1={degree+1} nghiệm Chebyshev trên [{w.number(a)}, {w.number(b)}] cho đa thức bậc không quá n={degree}.')
        w.formula(r'\theta_i=\frac{(2i+1)\pi}{2(n+1)},\quad x_i=\frac{a+b}{2}+\frac{b-a}{2}\cos\theta_i',
                  'θ_i=(2i+1)π/[2(n+1)]; x_i=(a+b)/2+(b−a)/2·cos θ_i, i=0,…,n.')
        w.text('Đây là mốc nghiệm, không phải mốc cực trị: không chứa hai đầu đoạn. Chỉ dùng khi được quyền chọn nơi lấy dữ liệu.')
    with w.group('section','2. Tính từng góc, mốc và sắp tăng'):
        w.table('Mốc Chebyshev — đầy đủ các lượt',['thứ tự tăng','i theo công thức','θᵢ (radian)','cos θᵢ','xᵢ'],
                ((rank,int(i),angles[i],np.cos(angles[i]),raw[i]) for rank,i in enumerate(sort_order)))
        w.text('Đã kiểm tra các mốc còn phân biệt trong độ chính xác biểu diễn; không tự gộp mốc.')
    with w.group('section','3. Lấy tung độ và phạm vi sai số'):
        w.text('Phải tính hoặc đo y tại chính các x mới. Không ghép các tung độ của bảng cũ vào bộ mốc mới; chưa có y thì chưa dựng được đa thức nội suy.', 'warning')
        w.formula(r'\|f-P\|_\infty\leq\frac{M_m(b-a)^m}{2^{2m-1}m!},\quad m=n+1',
                  'Nếu |f^(m)|≤M_m trên [a,b], cận giá trị ≤M_m(b−a)^m/[2^(2m−1)m!]. Chưa biết M_m thì chưa có cận số.')
        w.text('Tính tối ưu ở đây là chuẩn của tích mốc monic; không phải lời hứa sai số thực nhỏ nhất cho mọi hàm.', 'muted')
    return w.finish()


def present_fill_missing(report,x,original,result,selected,predicted,degree,tolerance,scale,model):
    data={'kind':'fill_missing','status':'completed','failure':None,'degree':degree,
          'selected_ids':list(map(int,selected)),'predicted':list(predicted),'tolerance':tolerance}
    w=ReportBuilder(report,display_digits=common.DISPLAY_DIGITS)
    report.presentation['worked_solution']=data
    with w.group('section','1. Giả thiết và các mốc đã biết'):
        w.text(f'Đề cho giả thiết bậc ≤{degree}; dùng {degree+1} mốc đã biết đầu tiên theo thứ tự nhập, ID={data["selected_ids"]}. Không tự coi mọi bảng dữ liệu là đa thức bậc này.')
        w.table('Mốc xác định mô hình',['ID nguồn','x','y'],((int(i),x[i],original[i]) for i in selected))
    with w.group('section','2. Dựng đa thức Newton và đánh giá'):
        w.text('Giữ dạng Newton lồng, đổi biến u=(x−origin)/scale để hạn chế triệt tiêu. origin='+w.number(model.origin)+'; scale='+w.number(model.scale)+'.')
        w.formula(r'P(x)=c_0+(u-u_0)[c_1+(u-u_1)[\cdots]]',
                  'Horner Newton: bắt đầu v=c_n; k=n−1 xuống 0, v=c_k+(u−u_k)v. Hệ số đi cùng đúng thứ tự mốc.')
        w.table('Hệ số và thứ tự mốc Newton',['k','x_k','u_k','c_k'],
                ((k,node,u,c) for k,(node,u,c) in enumerate(zip(model.raw_nodes,model.nodes,model.coefficients))))
    with w.group('section','3. Đối chiếu mọi tung độ đã biết'):
        w.table('Kiểm tra tương thích bậc',['ID nguồn','x','y đã biết','P(x)','sai lệch'],
                ((i,xv,yv,pv,abs(pv-yv)) for i,(xv,yv,pv) in enumerate(zip(x,original,predicted)) if np.isfinite(yv)))
        w.text('Điều kiện đang dùng: max sai lệch ≤ tolerance·max|y_đã_biết| = '+w.number(tolerance)+'·'+w.number(scale)+'. Nếu mâu thuẫn, dừng và báo sai giả thiết bậc; không chuyển ngầm sang bình phương tối thiểu.')
    with w.group('section','4. Điền các giá trị còn thiếu'):
        w.table('Bảng hoàn chỉnh và nguồn giá trị',['ID nguồn','x','y','nguồn'],
                ((i,xv,yv,'giữ dữ liệu' if np.isfinite(original[i]) else 'P(x), điền theo giả thiết bậc') for i,(xv,yv) in enumerate(zip(x,result))),text_columns=(3,))
        w.text('Kết quả phụ thuộc giả thiết bậc và dung sai dữ liệu được công bố. Chữ số hiển thị không phải cận sai số của hàm thật.', 'muted')
    return w.finish()
