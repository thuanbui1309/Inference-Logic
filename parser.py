import re

class Parser:
    @staticmethod
    def find_all_words(expression: str) -> list[str]:
        """
        Find all words (tokens) in the expression.

        :param expression: The input expression as a string.
        :return: A list of tokens found in the expression.
        """
        token_pattern = r'[a-zA-Z0-9]+|[<=>]+|[~&()]|\|\|'
        return re.findall(token_pattern, expression)

    @staticmethod
    def find_start_parenthesis(sentence: list[str], start_index: int) -> int:
        """
        Find the index of the matching opening parenthesis.

        :param sentence: The list of tokens representing the sentence.
        :param start_index: The starting index to search for the opening parenthesis.
        :return: The index of the matching opening parenthesis, or -1 if not found.
        """
        count = 0
        for i in range(start_index - 1, -1, -1):
            if sentence[i] == ')':
                count += 1
            elif sentence[i] == '(':
                if count == 0:
                    return i
                count -= 1
        return -1

    @staticmethod
    def find_end_parenthesis(sentence: list[str], start_index: int) -> int:
        """
        Find the index of the matching closing parenthesis.

        :param sentence: The list of tokens representing the sentence.
        :param start_index: The starting index to search for the closing parenthesis.
        :return: The index of the matching closing parenthesis, or -1 if not found.
        """
        count = 0
        for i in range(start_index + 1, len(sentence)):
            if sentence[i] == '(':
                count += 1
            elif sentence[i] == ')':
                if count == 0:
                    return i
                count -= 1
        return -1

    @staticmethod
    def add_parentheses_if_needed(clause: list[str]) -> list[str]:
        """
        Add parentheses around the clause if it contains more than one element
        and is not already enclosed by matching parentheses.

        :param clause: The list of tokens representing the clause.
        :return: The clause with added parentheses if needed.
        """
        if len(clause) > 2 and not (clause[0] == '(' and Parser.find_end_parenthesis(clause, 0) == len(clause) - 1):
            clause = ['('] + clause + [')']
        return clause

    @staticmethod
    def remove_paratheses_if_needed(clause: list[str]) -> list[str]:
        """
        Remove parentheses around the clause if it contains more than one element
        and is already enclosed by matching parentheses.

        :param clause: The list of tokens representing the clause.
        :return: The clause with removed parentheses if needed.
        """
        if len(clause) > 2 and clause[0] == '(' and Parser.find_end_parenthesis(clause, 0) == len(clause) - 1:
            clause = clause[1:-1]
        return clause
    
    @staticmethod
    def extract_literals(expression: list[str]) -> list[str]:
        """
        Extract the literals from the expression.

        :param expression: The list of tokens representing the expression.
        :return: A list of literals found in the expression.
        """
        literals = []
        for i in range(len(expression)):
            if expression[i] not in ["~", "&", "||", "(", ")", "=>", "<=>"]:
                literals.append(expression[i])
        return literals
    
    @staticmethod
    def extract_literals_with_signed(expression: list[str]) -> list[tuple[str, bool]]:
        """
        Extract the literals and their signs from the expression.

        :param expression: The list of tokens representing the expression.
        :return: A list of tuples where each tuple contains a literal and a boolean indicating if it is negated.
        """
        literals = []
        for i in range(len(expression)):
            if expression[i] not in ["~", "&", "||", "(", ")", "=>", "<=>"]:
                if i - 1 >= 0 and expression[i-1] == "~":
                    literals.append((expression[i], True))
                else:
                    literals.append((expression[i], False))
        return literals

    @staticmethod
    def extract_clauses(expression: list[str]) -> tuple[list[list[str]], list[str]]:
        """
        Extract clauses from the expression.

        :param expression: The list of tokens representing the expression.
        :return: A tuple containing a list of clauses and a list of operations.
        """
        if expression[0] == '(' and Parser.find_end_parenthesis(expression, 0) == len(expression) - 1:
            expression = expression[1:-1]

        found_literals = Parser.extract_literals(expression)
        recent_clause_idx = 0
        index = 0
        clauses = []
        operations = [None, None]

        while True:
            if index >= len(expression) - 1:
                recent_clause = expression[recent_clause_idx:index + 1]
                clauses.append(recent_clause)
                break

            elif expression[index] in found_literals:
                recent_clause_idx = index
                index += 1
            
            elif expression[index] == "~":
                if expression[index + 1] == "(":
                    end_parenthesis = Parser.find_end_parenthesis(expression, index + 1)
                    recent_clause_idx = index
                    index = end_parenthesis + 1
                elif expression[index + 1] in found_literals:
                    recent_clause_idx = index
                    index += 2

            elif expression[index] in ["&", "||"]:
                recent_clause = expression[recent_clause_idx:index]
                clauses.append(recent_clause)
                operations.insert(-1, expression[index])
                recent_clause_idx = index + 1
                index += 1

            elif expression[index] == "(":
                end_parentheis = Parser.find_end_parenthesis(expression, index)
                recent_clause_idx = index
                index = end_parentheis + 1

        return clauses, operations

    @staticmethod
    def organize_sentence(clauses: list[list[str]], operations: list[str]) -> tuple[list[list[str]], list[list[str]]]:
        """
        Organize the sentence into OR and AND clauses.

        :param clauses: The list of clauses.
        :param operations: The list of operations.
        :return: A tuple containing a list of OR clauses and a list of AND clauses.
        """
        or_clauses = []
        and_clauses = []

        for i in range(len(clauses)):
            if operations[i] == "&" or operations[i+1] == "&":
                and_clauses.append(clauses[i])
            else:
                or_clauses.append(clauses[i])

        return or_clauses, and_clauses

    @staticmethod
    def reconstruct_clause(clause: list[list[str]], operation: str) -> list[str]:
        """
        Reconstruct the clause with the given operation.

        :param clause: The list of clauses to be reconstructed.
        :param operation: The operation to be used for reconstruction.
        :return: The reconstructed clause as a list of tokens.
        """
        if len(clause) == 0:
            return clause
        
        if len(clause) == 1:
            return clause[0]

        reconstruced_clause = []

        for i in range(len(clause)):
            reconstruced_clause += clause[i]
            if i != len(clause) - 1:
                reconstruced_clause += operation

        return reconstruced_clause

    @staticmethod
    def is_horn_form(tell_part: str) -> bool:
        """
        Check if the given knowledge base is in Horn form.

        :param tell_part: String representation of the knowledge base, clauses separated by ";".
        :return: True if all clauses are in Horn form, False otherwise.
        """
        clauses = tell_part.split(";")
        
        for clause in clauses:
            clause = clause.strip()
            
            if "<=>" in clause:
                return False
            
            if "=>" in clause:
                parts = clause.split("=>")
                if len(parts) != 2:
                    print("Error: More than one '=>' found in a clause.")
                    return False
                
                premises, conclusion = parts
                premises = premises.strip()
                conclusion = conclusion.strip()

                conclusion_literals = conclusion.split()
                if conclusion.startswith("~") or len(conclusion_literals) > 1:
                    print("Error: Conclusion must contain exactly 1 positive literal.")
                    return False
            else:
                literals = clause.split("||")
                literals = [lit.strip() for lit in literals]
                
                positive_literals = [lit for lit in literals if not lit.startswith("~")]
                negative_literals = [lit for lit in literals if lit.startswith("~")]
                
                if len(positive_literals) > 1:
                    print("Error: At most 1 positive literal is allowed in a clause.")
                    return False
        return True

    @staticmethod
    def disjunction_to_implication(disjunction: str) -> str:
        """
        Convert a disjunction expression to an implication.

        :param disjunction: The disjunction expression as a string.
        :return: The implication expression as a string.
        """
        terms = [term.strip() for term in disjunction.split("||")]

        negations = [term[1:] for term in terms if term.startswith("~")]
        non_negations = [term for term in terms if not term.startswith("~")]

        left_side = " & ".join(negations)
        right_side = " || ".join(non_negations)

        return (f"{left_side} => {right_side}")