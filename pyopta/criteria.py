from Operator import *


class Criteria:
    """
    The Criteria class serves as a way to define a set of criteria that can be used 
    to filter and compare data. It takes an operator and a value as inputs and then 
    performs various operations based on the operator. 
    
    The perform_operation method checks which operator is being used and then calls 
    the corresponding method to perform the operation. The different methods perform 
    various types of comparisons, such as equality, inequality, less than, 
    greater than, between, etc. 
    
    The purpose of this class is to provide a flexible and extensible way to define 
    criteria for filtering and comparing data.
    """

    def __init__(self, operator, value):
        self.operator = operator
        self.value = value

    def perform_operation(self, value):
        if self.operator == Operator.EQ:
            return self.eq(value) 
        elif self.operator == Operator.NEQ:
            return self.neq(value)
        elif self.operator == Operator.LT:
            return self.lt(value) 
        elif self.operator == Operator.LTE:
            return self.lte(value)
        elif self.operator == Operator.GT:
            return self.gt(value) 
        elif self.operator == Operator.GTE:
            return self.gte(value)
        elif self.operator == Operator.BW:
            return self.bw(value)
        elif self.operator == Operator.IN:
            return self.inn(value)
        elif self.operator == Operator.NIN:
            return self.nin(value)
        elif self.operator == Operator.QIN:
            return self.qin(value)
        elif self.operator == Operator.QNIN:
            return self.qnin(value)

    def eq(self, value):
        return value == self.value
    
    def neq(self, value):
        return value != self.value
    
    def lt(self, value):
        return float(value) < float(self.value)

    def lte(self, value):
        return float(value) <= float(self.value)

    def gt(self, value):
        return float(value) > float(self.value)

    def gte(self, value):
        return float(value) >= float(self.value)

    def bw(self, value):
        return float(self.value[0]) <= float(value) <= float(self.value[1])

    def inn(self, value):
        return value in self.value
    
    def nin(self, value):
        return value not in self.value
    
    def qin(self, value):
        for q in value:
            if q.qualifier_id in self.value:
                return True
        return False
    
    def qnin(self, value):
        for q in value:
            if q.qualifier_id in self.value:
                return False
        return True