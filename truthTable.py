import re
import itertools
from logic import *
from typing import Generator

class TruthTable:
    def __init__(self, filename: str) -> None:
        """
        Initialize the TruthTable with literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        self.literals: dict[str, Literal] = {}
        self.kb: list[Operation] = []
        self.query: Operation = None

        self.parse(filename)

    def parse_literals(self, knowledge_base: str) -> dict[str, Literal]:
        """
        Parse literals from the knowledge base string.

        :param knowledge_base: The knowledge base string.
        :return literals: A dictionary of literals.
        """
        literals = {}
        for lit in re.findall(r'[a-zA-Z]', knowledge_base):
            if lit not in literals:
                literals[lit] = Literal(lit)

        return literals
    
    def find_end_parenthesis(self, sentence: str, start_index: int) -> int:
        """
        Find the index of the matching closing parenthesis.

        :param sentence: The sentence containing parentheses.
        :param start_index: The index of the opening parenthesis.
        :return: The index of the matching closing parenthesis.
        """
        count = 0
        for i in range(start_index + 1, len(sentence)):
            if sentence[i] == '(':
                count += 1
            if sentence[i] == ')':
                if count == 0:
                    return i
                count -= 1

        return -1
    
    def find_all_words(self, expression: str) -> list[str]:
        """
        Find all words (tokens) in the expression.

        :param expression: The expression to tokenize.
        :return: A list of tokens.
        """
        token_pattern = r'[a-zA-Z]+|[<=>]+|[~&()]|\|\|'
        return re.findall(token_pattern, expression)

    def parse_sentence(self, sentence: str) -> Operation:
        """
        Parse a sentence into an Operation object.

        :param sentence: The sentence to parse.
        :return: The parsed Operation object.
        """
        # Remove outermost parentheses if they exist
        if sentence[0] == '(' and self.find_end_parenthesis(sentence, 1) == len(sentence) - 1:
            sentence = sentence[1:-1]

        # If there is only 1 element, it is a literal
        if len(sentence) == 1:
            return self.literals[sentence[0]]
        
        # If sentence starts with a negation
        if sentence[0] == '~':
            print("Negation")
            # If there are only 2 elements, it is a negation of a literal
            if len(sentence) == 2:
                return Operation('~', [self.literals[sentence[1]]])
            
            # If after negation is a parenthesis, it might be a negation of a clause or the whole sentence
            if sentence[1] == '(':
                end_parenthesis_index = self.find_end_parenthesis(sentence, 1)

                # If the negation is the negation of the whole sentence
                if end_parenthesis_index == len(sentence) - 1:
                    return Operation('~', [self.parse_sentence(sentence[2:])])
                # If the negation is the negation of a clause inside this sentence
                # That means there is another clause after this clause
                else:
                    next_operation = sentence[end_parenthesis_index + 1]
                    next_clause = sentence[end_parenthesis_index + 2:]
                    premises = [
                        Operation('~', [self.parse_sentence(sentence[2:end_parenthesis_index])]),
                        self.parse_sentence(next_clause)
                    ]

                    return Operation(next_operation, premises)
                
            # If none of the above, sentence starts with a negation of a literal and an operation
            first_literal = sentence[1]
            operation = sentence[2]
            next_clause = sentence[3:]
            premises = [
                Operation('~', [self.literals[first_literal]]),
                self.parse_sentence(next_clause)
            ]
            return Operation(operation, premises)

        # If sentence starts with a parenthesis
        # Because we have removed outermost parentheses, this means there are 2 clauses in this sentence
        if sentence[0] == "(":
            end_parenthesis_index = self.find_end_parenthesis(sentence, 0)     
            first_clause = sentence[0:end_parenthesis_index + 1]
            next_operation = sentence[end_parenthesis_index + 1]
            next_clause = sentence[end_parenthesis_index + 2:]

            premises = [
                self.parse_sentence(first_clause),
                self.parse_sentence(next_clause)
            ]

            return Operation(next_operation, premises)
        
        # If none of the above, sentence starts with a literal
        first_literal = sentence[0]
        operation = sentence[1]
        next_clause = sentence[2:]

        return Operation(operation, [self.literals[first_literal], self.parse_sentence(next_clause)])

    def parse_knowledge_base(self, kb: str) -> list[Operation]:
        """
        Parse the knowledge base into a list of Operation objects.

        :param kb: The knowledge base string.
        :return: A list of parsed Operation objects.
        """
        kb_content = kb.strip()[:-1].split(";")

        kb = []
        for expression in kb_content:
            sentence = self.find_all_words(expression)
            kb.append(self.parse_sentence(sentence))

        return kb

    def parse(self, filename: str) -> None:
        """
        Parse the file to extract literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        with open(filename, 'r') as f:
            file_content = f.readlines()
            self.literals = self.parse_literals(file_content[1])
            self.kb = self.parse_knowledge_base(file_content[1])
            self.query = self.parse_sentence(self.find_all_words(file_content[3]))

    def generate_truth_assignments(self) -> Generator[dict, None, None]:
        """
        Generate all possible combinations of truth values for literals.

        :yield: A dictionary representing a truth assignment.
        """
        literals = list(self.literals.values())
        for values in itertools.product([True, False], repeat=len(literals)):
            assignment = {literal: value for literal, value in zip(literals, values)}
            yield assignment

    def run(self) -> None:
        """
        Run the truth table algorithm to determine if the knowledge base entails the query.
        """
        is_entail = True
        entailment_count = 0

        for assignment in self.generate_truth_assignments():
            # Set truth values for each literal based on current assignment
            for literal, value in assignment.items():
                literal.set_value(value)

            # Evaluate knowledge base and query with current assignment
            kb_result = all(statement.evaluate() for statement in self.kb)
            query_result = self.query.evaluate()

            if kb_result:
                if not query_result:
                    is_entail = False
                    break
                
                entailment_count += 1

        if is_entail:
            print(f"YES: {entailment_count}")
        else:
            print("NO")