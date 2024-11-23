from itertools import groupby
from typing import List, Tuple
from parser import Parser
from converter import CNFConverter

class DPLL:
    def __init__(self, filename: str):
        """
        Initialize the TruthTable with literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        """
        self.literals = set()
        self.kb = []
        self.assignments = {}
        self.parse(filename)

    def parse(self, filename: str) -> None:
        """
        Parse the file to extract literals, knowledge base, and query.

        :param filename: The file containing the knowledge base and query.
        :return: None
        """
        with open(filename, 'r') as f:
            file_content = f.readlines()
            kb_sentences = file_content[1]
            query_sentence = file_content[3]
            self.extract_knowledge_base(kb_sentences)
            self.extract_query(query_sentence)

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
        :return: None
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
        :return: None
        """
        # Extract query
        query = self.extract_expression(query)[0]
        query = Parser.find_all_words(query)
        query = CNFConverter.convert_sentence(query)
        query = CNFConverter.move_negations_inwards(["~", "("] + query + [")"])
        query = CNFConverter.convert_sentence(query)

        # Convert each single query into a group of AND clauses
        query = [list(group) for key, group in groupby(query, lambda x: x == '&') if not key]

        # Add negated query to knowledge base (for checking entailment)
        for clause in query:
            negated_clause = [(literal, not sign) for literal, sign in Parser.extract_literals_with_signed(clause)]
            self.kb.append(negated_clause)

    def perform_unit_propagation(self, kb: List[List[Tuple[str, bool]]]) -> Tuple[List[List[Tuple[str, bool]]], str]:
        """
        Perform unit propagation on the knowledge base.

        :param kb: The knowledge base to process.
        :return: Updated knowledge base and SAT/UNSAT status.
        """
        while True:
            unit_clause_idx = -1
            for i in range(len(kb)):
                if len(kb[i]) == 1:
                    unit_clause_idx = i
                    break

            if unit_clause_idx == -1:
                return kb, "UNDETERMINED"

            unit_clause_literal, unit_clause_sign = kb.pop(unit_clause_idx)[0]
            self.assignments[unit_clause_literal] = unit_clause_sign

            # Remove all clauses satisfied by the literal
            kb = [clause for clause in kb if (unit_clause_literal, unit_clause_sign) not in clause]

            # Remove the negated literal (~literal) from other clauses
            negated_literal = (unit_clause_literal, not unit_clause_sign)

            for clause in kb:
                if negated_literal in clause:
                    clause.remove(negated_literal)

            if [] in kb:
                return kb, "UNSAT"
            elif len(kb) == 0:
                return kb, "SAT"

    def is_pure_literal(self, literal: Tuple[str, bool], kb: List[List[Tuple[str, bool]]]) -> bool:
        """
        Check if a literal is pure (only appears in one polarity in KB).

        :param literal: The literal to check.
        :param kb: The knowledge base.
        :return: True if the literal is pure, False otherwise.
        """
        literal_status = None

        for clause in kb:
            for clause_literal in clause:
                if literal[0] == clause_literal[0]:
                    if literal_status is None:
                        literal_status = clause_literal[1]
                    else:
                        if literal_status != clause_literal[1]:
                            return False

        return True

    def perform_pure_literal_elimination(self, kb: List[List[Tuple[str, bool]]]) -> List[List[Tuple[str, bool]]]:
        """
        Perform pure literal elimination on the knowledge base.

        :param kb: The knowledge base to process.
        :return: Updated knowledge base.
        """
        all_literals = {literal for clause in kb for literal, _ in clause}
        pure_literals = {literal for literal in all_literals if self.is_pure_literal((literal, True), kb)}

        for literal in pure_literals:
            self.assignments[literal] = True
            kb = [clause for clause in kb if (literal, True) not in clause]

        return kb

    def perform_branching(self, kb: List[List[Tuple[str, bool]]]) -> Tuple[List[List[Tuple[str, bool]]], bool]:
        """
        Perform branching on the knowledge base as the last step of the DPLL algorithm.

        :param kb: The knowledge base to process.
        :return: (kb, status): Updated KB and status (True if SAT, False if UNSAT).
        """
        # Check if KB is empty or contains an empty clause
        if len(kb) == 0:
            return [], True
        if [] in kb:
            return kb, False

        # Pick a literal for branching (choose the first literal in the first clause)
        chosen_literal = kb[0][0][0]

        # Assume the literal is True
        new_kb = [clause.copy() for clause in kb]
        new_kb = [clause for clause in new_kb if (chosen_literal, False) not in clause]
        for clause in new_kb:
            if (chosen_literal, True) in clause:
                clause.remove((chosen_literal, True))

        result_kb, result_status = self.perform_branching(new_kb)
        if result_status:
            self.assignments[chosen_literal] = True
            return result_kb, result_status

        # Assume the literal is False
        new_kb = [clause.copy() for clause in kb]
        new_kb = [clause for clause in new_kb if (chosen_literal, True) not in clause]
        for clause in new_kb:
            if (chosen_literal, False) in clause:
                clause.remove((chosen_literal, False))

        result_kb, result_status = self.perform_branching(new_kb)
        if result_status:
            self.assignments[chosen_literal] = False
            return result_kb, result_status

        return kb, False  # UNSAT if both branches fail

    def infer(self) -> None:
        """
        Perform DPLL inference.

        :return: None
        """
        # Perform Unit Propagation
        self.kb, status = self.perform_unit_propagation(self.kb)
        if status == "UNSAT":
            print("NO")
            return
        elif status == "SAT":
            print("YES")
            return

        # Perform Pure Literal Elimination
        self.kb = self.perform_pure_literal_elimination(self.kb)

        if len(self.kb) == 0:
            print("YES")
            return

        # Perform Branching
        _, status = self.perform_branching(self.kb)
        if status:
            print("YES")
        else:
            print("NO")