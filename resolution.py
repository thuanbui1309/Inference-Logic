from itertools import groupby
from typing import List
from parser import Parser
from converter import CNFConverter

class Resolution:
    def __init__(self, filename: str):
        """
        Initialize the TruthTable with literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        self.literals = set()
        self.kb = []
        self.query = []

        self.parse(filename)

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

            for clause in expression:
                self.kb.append(Parser.extract_literals_with_signed(clause))

    def extract_query(self, query: str) -> None:
        """
        Extract and process the query from the given string.

        :param query: The string containing the query.
        """
        # Extract query
        query = self.extract_expression(query)[0]
        query = Parser.find_all_words(query)
        query = CNFConverter.convert_sentence(query)
        query = CNFConverter.move_negations_inwards(["~", "("] + query + [")"])
        query = CNFConverter.convert_sentence(query)

        # Convert each single query into a group of AND clauses
        query = [list(group) for key, group in groupby(query, lambda x: x == '&') if not key]

        # Store converted expression into total knowledge base
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

        return None
    
    def complement_literal_exist(self, literal: list[int, int], clause: list[list[int, int]]):
        for i in range(len(clause)):
            if literal[0] == clause[i][0] and literal[1] != clause[i][1]:
                return i
            
        return -1
    
    def verify_converted_clause(self, clause):
        """
        Verify and simplify a clause:
        - Remove duplicates.
        - Handle tautologies (e.g., both `p` and `~p` in the same clause).
        """
        literals = {}
        for literal, sign in clause:
            if literal in literals:
                if literals[literal] != sign:
                    return []  # Tautology detected
            else:
                literals[literal] = sign

        # Rebuild the clause without duplicates
        return [(literal, sign) for literal, sign in literals.items()]

    
    def resolve(self, clause, kb):        
        for i in range(len(clause)):
            for j in range(len(kb)):
                literal_idx = self.complement_literal_exist(clause[i], kb[j])
                if literal_idx != -1:

                    converted_clause = self.verify_converted_clause(clause[:i] + clause[i+1:] + kb[j][:literal_idx] + kb[j][literal_idx+1:])

                    if len(converted_clause) == 0:
                        return True
                    
                    resolved = self.resolve(converted_clause, kb[:j] + kb[j+1:])

                    if resolved:
                        return True

        return False

    def infer(self) -> None:
        """
        Run the truth table algorithm to determine if the knowledge base entails the query.
        """
        for clause in self.query:
            if not self.resolve(clause, self.kb):
                print("NO")
                return
        print("YES")