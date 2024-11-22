import re

class Parser:
    @staticmethod
    def find_all_words(expression: str) -> list[str]:
        """
            Find all words (tokens) in the expression.
        """
        token_pattern = r'[a-zA-Z0-9]+|[<=>]+|[~&()]|\|\|'
        return re.findall(token_pattern, expression)

    @staticmethod
    def find_start_parenthesis(sentence: list[str], start_index: int) -> int:
        """
            Find the index of the matching opening parenthesis.
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
        """
        if len(clause) > 2 and not (clause[0] == '(' and Parser.find_end_parenthesis(clause, 0) == len(clause) - 1):
            clause = ['('] + clause + [')']
        return clause

    @staticmethod
    def remove_paratheses_if_needed(clause: list[str]) -> list[str]:
        """
            Remove parentheses around the clause if it contains more than one element
            and is already enclosed by matching parentheses.
        """
        if len(clause) > 2 and clause[0] == '(' and Parser.find_end_parenthesis(clause, 0) == len(clause) - 1:
            clause = clause[1:-1]
        return clause
    
    @staticmethod
    def extract_literals(expression: list[str]) -> list[str]:
        """
            Extract the literal from the expression.
        """
        literals = []
        for i in range(len(expression)):
            if expression[i] not in ["~", "&", "||", "(", ")", "=>", "<=>"]:
                literals.append(expression[i])

        return literals
    
    @staticmethod
    def extract_literals_with_signed(expression: list[str]) -> list[(str, bool)]:
        """
            Extract the literals and its signs from the expression.
        """
        literals = []
        for i in range(len(expression)):
            # print(expression[i])
            if expression[i] not in ["~", "&", "||", "(", ")", "=>", "<=>"]:
                if i - 1 >= 0 and expression[i-1] == "~":
                    literals.append((expression[i], True))
                else:
                    literals.append((expression[i], False))

        return literals

    @staticmethod
    def extract_clauses(expression: list[str]) -> list[str]:
        """
            Extract clauses from the expression.
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
    def organize_sentence(clauses: list[str], operations: list[str]) -> list[str]:
        """
            Organize the sentence into OR and AND clauses.
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
    def reconstruct_clause(clause: list[str], operation) -> list[str]:
        """
            Reconstruct the clause with the given operation.
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
        # Tách từng mệnh đề
        clauses = tell_part.split(";")
        
        for clause in clauses:
            clause = clause.strip()
            
            # Kiểm tra các phép không hợp lệ (<=> không được phép trong Horn Form)
            if "<=>" in clause:
                return False
            
            if "=>" in clause:
                # Phân tách premise và conclusion
                parts = clause.split("=>")
                if len(parts) != 2:
                    return False  # Sai cú pháp nếu có nhiều hơn 1 "=>"
                
                premises, conclusion = parts
                premises = premises.strip()
                conclusion = conclusion.strip()

                # Kiểm tra conclusion (chỉ chứa 1 literal dương)
                conclusion_literals = conclusion.split()
                if conclusion.startswith("~") or len(conclusion_literals) > 1:
                    return False
            else:
                # Nếu không có "=>", kiểm tra dạng disjunction
                literals = clause.split("||")  # Tách literal theo phép OR
                literals = [lit.strip() for lit in literals]  # Loại bỏ khoảng trắng thừa
                
                # Phân loại literal dương và âm
                positive_literals = [lit for lit in literals if not lit.startswith("~")]
                negative_literals = [lit for lit in literals if lit.startswith("~")]
                
                # Điều kiện:
                # - Tối đa một literal dương
                if len(positive_literals) > 1:
                    return False
        return True

    @staticmethod
    def disjunction_to_implication(disjunction):
        """
        Chuyển đổi biểu thức disjunction thành implication.
        """
        # Tách các literals
        terms = [term.strip() for term in disjunction.split("||")]

        # Phân loại phủ định và không phủ định
        negations = [term[1:] for term in terms if term.startswith("~")]
        non_negations = [term for term in terms if not term.startswith("~")]

        # Vế trái: Phủ định của tất cả các negations
        left_side = " & ".join(negations)

        # Vế phải: Một hoặc nhiều literals không phủ định
        right_side = " || ".join(non_negations)

        # Kết quả
        return (f"{left_side} => {right_side}")

        #đang sai