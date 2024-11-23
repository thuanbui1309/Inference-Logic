from itertools import groupby, product
from typing import Generator, List, Dict
from parser import Parser
from converter import CNFConverter

class TruthTable:
    def __init__(self, filename: str):
        """
        Initialize the TruthTable with literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        self.literals = set()
        self.kb = []
        self.query = []

        self.parse(filename)
    
    def evaluate_expression(self, expression: List[List[str]], assignment: Dict[str, bool]) -> bool:
        """
        Evaluate whether an expression is True or False.
        An expression contains clauses operated by AND.
        Eg. (a || b) & (c || d)
        An expression is True when all clauses inside it are True.

        :param expression: The expression to evaluate.
        :param assignment: The truth assignment for literals.
        :return: True if the expression is True, False otherwise.
        """
        for clause in expression:
            clause_value = self.evaluate_clause(clause, assignment)
            if not clause_value:
                return False
            
        return True

    def evaluate_clause(self, clause: List[str], assignment: Dict[str, bool]) -> bool:
        """
        Evaluate whether a clause is True or False.
        A clause contains literals operated by OR.
        Eg. a || ~b
        A clause is True when at least one literal is True.

        :param clause: The clause to evaluate.
        :param assignment: The truth assignment for literals.
        :return: True if the clause is True, False otherwise.
        """
        for literal in clause:
            if literal[1] == True:
                literal_value = not assignment[literal[0]]
            else:
                literal_value = assignment[literal[0]]

            if literal_value:
                return True
            
        return False
    
    def evaluate_kb(self, kb: List[List[List[str]]], assignment: Dict[str, bool]) -> bool:
        """
        Evaluate whether the knowledge base (kb) is True or False.
        A kb contains different expressions.
        A kb is True when all expressions are True.

        :param kb: The knowledge base to evaluate.
        :param assignment: The truth assignment for literals.
        :return: True if the knowledge base is True, False otherwise.
        """
        for expression in kb:
            expression_value = self.evaluate_expression(expression, assignment)
            if not expression_value:
                return False
            
        return True

    def extract_expression(self, expressions: str) -> List[str]:
        """
        Extract all expressions inside the whole expressions.

        :param expressions: The string containing multiple expressions.
        :return: A list of individual expressions.
        """
        expressions = expressions.split(";")
        expressions = [item.strip() for item in expressions if item.strip()]

        return expressions

    def extract_knowledge_base(self, knowledge_base: str) -> None:
        """
        Extract and process the knowledge base from the given string.

        :param knowledge_base: The string containing the knowledge base.
        """
        knowledge_base = self.extract_expression(knowledge_base)

        for expression in knowledge_base:
            # Turn expression into a list of strings
            expression = Parser.find_all_words(expression)
            expression = CNFConverter.convert_sentence(expression)
            [self.literals.add(item) for item in Parser.extract_literals(expression)]
            expression = [list(group) for key, group in groupby(expression, lambda x: x == '&') if not key]

            # Store converted expression into total knowledge base
            knowledge_base_clause = []
            for clause in expression:
                knowledge_base_clause.append(Parser.extract_literals_with_signed(clause))

            self.kb.append(knowledge_base_clause)

    def extract_query(self, query: str) -> None:
        """
        Extract and process the query from the given string.

        :param query: The string containing the query.
        """
        # Extract query
        query = self.extract_expression(query)[0]
        query = Parser.find_all_words(query)
        query = CNFConverter.convert_sentence(query)
        query = [list(group) for key, group in groupby(query, lambda x: x == '&') if not key]

        # Store converted query
        for clause in query:
            self.query.append(Parser.extract_literals_with_signed(clause))

    def parse(self, filename: str) -> None:
        """
        Parse the file to extract literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        with open(filename, 'r') as f:
            file_content = f.readlines()
            kb_sentences = file_content[1]
            query_sentence = file_content[3]
            self.extract_knowledge_base(kb_sentences)
            self.extract_query(query_sentence)

            # for item in self.kb:
            #     print(item)

    def generate_truth_assignments(self) -> Generator[Dict[str, bool], None, None]:
        """
        Generate all possible combinations of truth values for literals.

        :yield: A dictionary representing a truth assignment.
        """
        literals_list = list(self.literals)
        for values in product([True, False], repeat=len(literals_list)):
            assignment = {literal: value for literal, value in zip(literals_list, values)}
            yield assignment

    def infer(self) -> None:
        """
        Run the truth table algorithm to determine if the knowledge base entails the query.
        """
        valid_cases = 0
        for assignment in self.generate_truth_assignments():
            kb_value = self.evaluate_kb(self.kb, assignment)
            query_value = self.evaluate_expression(self.query, assignment)

            if kb_value and query_value:
                valid_cases += 1

        if valid_cases > 0:
            print(f"YES: {valid_cases}")
        else:
            print("NO")