"""Mô hình nội suy ngược: hệ số hữu tỷ và phép tính Decimal tách khỏi trình bày."""
from decimal import Decimal, localcontext
from fractions import Fraction
import math

from .polynomial_model import working_precision


def evaluate(coefficients, value):
    result=coefficients[0]*0
    for coefficient in reversed(coefficients):result=coefficient+value*result
    return result


def compose_interval(coefficients, center, radius):
    result=[coefficients[-1]]
    for coefficient in reversed(coefficients[:-1]):
        nxt=[coefficients[0]*0]*(len(result)+1)
        for i,v in enumerate(result):
            nxt[i]+=center*v;nxt[i+1]+=radius*v
        nxt[0]+=coefficient;result=nxt
    return result


def rational(value):
    return value if isinstance(value,Fraction) else Fraction(str(value))


def decimal(value):
    return Decimal(value.numerator)/Decimal(value.denominator) if isinstance(value,Fraction) else Decimal(str(value))


def difference_table(nodes,values,divided=False):
    """Mỗi ô chỉ tính một lần; giữ các toán hạng để truy lại phép tính."""
    columns=[list(map(rational,values))];steps=[]
    nodes=list(map(rational,nodes))
    for order in range(1,len(nodes)):
        previous=columns[-1];column=[]
        for i in range(len(previous)-1):
            numerator=previous[i+1]-previous[i]
            denominator=nodes[i+order]-nodes[i] if divided else Fraction(1)
            if not denominator:raise ValueError(f'Mẫu số tỷ sai phân bằng 0 tại hàng {i}, cấp {order}.')
            value=numerator/denominator;column.append(value)
            steps.append({'i':i,'order':order,'left':previous[i],'right':previous[i+1],
                          'node_left':nodes[i],'node_right':nodes[i+order],
                          'numerator':numerator,'denominator':denominator,'value':value})
        columns.append(column)
    return columns,steps


def expand_newton(nodes,coefficients):
    result=[coefficients[-1]]
    for k in range(len(coefficients)-2,-1,-1):
        nxt=[Fraction(0)]*(len(result)+1)
        for i,v in enumerate(result):nxt[i]-=nodes[k]*v;nxt[i+1]+=v
        nxt[0]+=coefficients[k];result=nxt
    while len(result)>1 and not result[-1]:result.pop()
    return result


def derivative(coefficients):
    return [k*v for k,v in enumerate(coefficients) if k] or [Fraction(0)]


def multiply_intervals(first,second):
    products=[a*b for a in first for b in second]
    return min(products),max(products)


def polynomial_range(coefficients,a,b):
    """Bao hữu tỷ: cực trị bậc thấp, đơn điệu đã chứng minh, hoặc cận hệ số."""
    coefficients=list(coefficients)
    while len(coefficients)>1 and not coefficients[-1]:coefficients.pop()
    if len(coefficients)<=3:
        values=[evaluate(coefficients,a),evaluate(coefficients,b)]
        if len(coefficients)==3 and coefficients[2]:
            vertex=-coefficients[1]/(2*coefficients[2])
            if a<=vertex<=b:values.append(evaluate(coefficients,vertex))
        return min(values),max(values)
    # Chặn đạo hàm trên cả đoạn trước khi dùng tính đơn điệu. Không suy
    # ra đơn điệu từ vài mẫu; truy hồi giảm bậc nên luôn kết thúc.
    slope_lo,slope_hi=polynomial_range(derivative(coefficients),a,b)
    if slope_lo>=0 or slope_hi<=0:
        ends=[evaluate(coefficients,a),evaluate(coefficients,b)]
        return min(ends),max(ends)
    center=(a+b)/2;radius=(b-a)/2
    shifted=compose_interval(coefficients,center,radius)
    deviation=sum(map(abs,shifted[1:]),Fraction(0))
    return shifted[0]-deviation,shifted[0]+deviation


def certify(model,lo,hi,t0):
    ranges=[];high_lo=high_hi=Fraction(0)
    product_range=None
    for order in range(2,len(model.differences)):
        if order==2:
            product_range=polynomial_range([Fraction(0),Fraction(1 if model.backward else -1),Fraction(1)],lo,hi)
        else:
            shift=order-1 if model.backward else -(order-1)
            product_range=multiply_intervals(product_range,(lo+shift,hi+shift))
        factor=model.differences[order]/math.factorial(order)
        term_range=multiply_intervals(product_range,(factor,factor))
        ranges.append({'order':order,'lower':term_range[0],'upper':term_range[1]})
        high_lo+=term_range[0];high_hi+=term_range[1]
    numerator=(model.target_exact-model.y0_exact-high_hi,model.target_exact-model.y0_exact-high_lo)
    image=tuple(sorted(v/model.d1_exact for v in numerator))
    dphi=derivative(model.phi_exact)
    derivative_image=polynomial_range(dphi,lo,hi)
    derivative_candidates=[]
    if len(dphi)<=3:
        candidates=[lo,hi]
        if len(dphi)==3 and dphi[2]:
            vertex=-dphi[1]/(2*dphi[2])
            if lo<=vertex<=hi:candidates.append(vertex)
        derivative_candidates=[(point,evaluate(dphi,point)) for point in candidates]
    else:
        slopes=polynomial_range(derivative(dphi),lo,hi)
        if slopes[0]>=0 or slopes[1]<=0:
            derivative_candidates=[(point,evaluate(dphi,point)) for point in (lo,hi)]
    q=max(map(abs,derivative_image))
    witnesses=[(point,evaluate(model.phi_exact,point)) for point in (lo,(lo+hi)/2,hi)]
    image_state='verified' if lo<=image[0]<=image[1]<=hi else 'not_verified'
    if any(not lo<=value<=hi for _,value in witnesses):image_state='disproved'
    derivative_state='verified' if q<1 else 'not_verified'
    if any(abs(evaluate(dphi,point))>=1 for point in (lo,hi)):derivative_state='disproved'
    return {'initial_state':'verified' if lo<=t0<=hi else 'disproved',
            'image_state':image_state,'derivative_state':derivative_state,
            'image':image,'image_numerators':numerator if model.d1_exact>0 else numerator[::-1],
            'derivative_image':derivative_image,
            'q':q if derivative_state=='verified' else None,'estimated_q':q,
            'term_ranges':ranges,'phi_derivative':dphi,'derivative_candidates':derivative_candidates,
            'arithmetic':'exact_rational','machine_rounding_certified':False,
            'verified':lo<=t0<=hi and image_state=='verified' and derivative_state=='verified'}


class InverseMap:
    def __init__(self,x,y,target,backward=False,precision=50,table=None):
        exponents=[Decimal(str(abs(float(v)))).adjusted() for v in y if v!=0]
        spread=max(exponents)-min(exponents) if exponents else 0
        self.precision=max(working_precision(x),precision,spread+2*len(x)+30)
        self.backward=backward
        self.x_exact=list(map(rational,x));self.y_exact=list(map(rational,y))
        self.h_exact=self.x_exact[1]-self.x_exact[0]
        self.origin_exact=self.x_exact[-1] if backward else self.x_exact[0]
        self.target_exact=rational(target)
        self.columns,self.difference_steps=table if table is not None else difference_table(self.x_exact,self.y_exact)
        self.coefficient_indices=[(len(x)-k-1 if backward else 0,k) for k in range(len(x))]
        self.differences=[self.columns[k][i] for i,k in self.coefficient_indices]
        self.y0_exact=self.differences[0];self.d1_exact=self.differences[1]
        if not self.d1_exact:raise ValueError('Sai phân cấp một tại gốc bằng 0.')
        scaled=[v/math.factorial(k) for k,v in enumerate(self.differences)]
        while len(scaled)>1 and not scaled[-1]:scaled.pop()
        self.polynomial_exact=expand_newton([Fraction(-k if backward else k) for k in range(len(scaled))],scaled)
        phi=[-v/self.d1_exact for v in self.polynomial_exact]
        phi[0]+=self.target_exact/self.d1_exact
        if len(phi)<2:phi.append(Fraction(0))
        phi[1]+=1
        while len(phi)>1 and not phi[-1]:phi.pop()
        self.phi_exact=phi
        with localcontext() as ctx:
            ctx.prec=self.precision
            self.h=decimal(self.h_exact);self.origin=decimal(self.origin_exact)
            self.target=decimal(self.target_exact);self.y0=decimal(self.y0_exact);self.d1=decimal(self.d1_exact)
            self.polynomial=list(map(decimal,self.polynomial_exact));self.phi=list(map(decimal,self.phi_exact))

    def initial(self):return (self.target-self.y0)/self.d1

    def contributions(self,t):
        basis=Decimal(1);terms=[]
        for order in range(1,len(self.differences)):
            basis*= (t+(order-1) if self.backward else t-(order-1))/order
            if order>=2:terms.append({'order':order,'basis':basis,'coefficient':self.differences[order],
                                     'factors':[t+k if self.backward else t-k for k in range(order)],
                                     'value':decimal(self.differences[order])*basis})
        return terms

    def step(self,t):return (self.target-self.y0-sum((term['value'] for term in self.contributions(t)),Decimal(0)))/self.d1

    def residual(self,t):return abs(evaluate(self.polynomial,t)-self.target)

    def location(self,t):return self.origin+self.h*t
