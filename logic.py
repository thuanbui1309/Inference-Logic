class Literal:
    def __init__(self, name: str):
        """
        Constructor for the Literal class.
        
        Parameters:
        name (str): The name of the literal.
        """
        self.name = name
        self.value = None
    
    def __and__(self, other: 'Literal') -> bool:
        """
        Logical AND operation between two literals.
        
        Parameters:
        other (Literal): The other literal to perform the operation with.
        
        Returns:
        bool: The result of the AND operation.
        """
        return self.value and other.value

    def __or__(self, other: 'Literal') -> bool:
        """
        Logical OR operation between two literals.
        
        Parameters:
        other (Literal): The other literal to perform the operation with.
        
        Returns:
        bool: The result of the OR operation.
        """
        return self.value or other.value

    def __invert__(self) -> bool:
        """
        Logical NOT operation on the literal.
        
        Returns:
        bool: The result of the NOT operation.
        """
        return not self.value
    
    def __rshift__(self, other: 'Literal') -> bool:
        """
        Logical implication operation between two literals.
        
        Parameters:
        other (Literal): The other literal to perform the operation with.
        
        Returns:
        bool: The result of the implication operation.
        """
        return not self.value or other.value

    def iff(self, other: 'Literal') -> bool:
        """
        Logical biconditional (if and only if) operation between two literals.
        
        Parameters:
        other (Literal): The other literal to perform the operation with.
        
        Returns:
        bool: The result of the biconditional operation.
        """
        return (not self.value or other.value) and (not other.value or self.value)
    
    def __hash__(self) -> int:
        """
        Returns the hash value of the literal based on its name.
        
        Returns:
        int: The hash value of the literal.
        """
        return hash(self.name)

    def set_value(self, value: bool) -> None:
        """
        Sets the truth value of the literal.
        
        Parameters:
        value (bool): The truth value to set.
        """
        self.value = value

    def evaluate(self) -> bool:
        """
        Evaluates the truth value of the literal.
        
        Returns:
        bool: The truth value of the literal.
        """
        return self.value
        
class Operation:
    def __init__(self, name: str, premises: list[Literal]):
        """
        Constructs all the necessary attributes for the operation object.
        
        Parameters:
        name (str): The name of the operation.
        premises (List[Literal]): The premises involved in the operation.
        """
        self.name = name
        self.premises = premises

    def evaluate(self) -> bool:
        """
        Evaluates the result of the logical operation based on its premises.
        
        Returns:
        bool: The result of the logical operation.
        
        Raises:
        ValueError: If the operation name is unknown.
        """
        if self.name == '&':
            return all(premise.evaluate() for premise in self.premises)
        elif self.name == '||':
            return any(premise.evaluate() for premise in self.premises)
        elif self.name == '~':
            return not self.premises[0].evaluate()
        elif self.name == '=>':
            return not self.premises[0].evaluate() or self.premises[1].evaluate()
        elif self.name == '<=>':
            return self.premises[0].evaluate() == self.premises[1].evaluate()
        else:
            raise ValueError(f"Unknown operation: {self.name}")