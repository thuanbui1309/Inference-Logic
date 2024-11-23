from parser import Parser

class CNFConverter:
    @staticmethod
    def eliminate_biconditional(sentence: list[str]) -> list[str]:
        """Eliminate biconditional operators from the sentence."""
        while "<=>" in sentence:
            i = sentence.index("<=>") # Find the index of the biconditional operator
            start_parenthesis = Parser.find_start_parenthesis(sentence, i)
            
            if start_parenthesis == -1:
                # No parentheses around the expressions, split the sentence
                # eg. (a <=> b) becomes (~a || b) & (~b || a)
                first_part = sentence[:i]
                second_part = sentence[i + 1:]

                # Avoid unnecessary parentheses
                first_part = Parser.add_parentheses_if_needed(first_part)
                second_part = Parser.add_parentheses_if_needed(second_part)

                sentence = (
                    ['(', '~'] + first_part + ['||'] + second_part + [')', '&'] +
                    ['(', '~'] + second_part + ['||'] + first_part + [')']
                )
            else:
                # Parentheses around the expressions, split the clause
                # eg. (a <=> b) & c becomes ((~a || b) & (~b || a)) & c
                first_part = sentence[start_parenthesis+1:i]
                end_parenthesis = Parser.find_end_parenthesis(sentence, start_parenthesis)
                second_part = sentence[i + 1:end_parenthesis]

                # Avoid unnecessary parentheses
                first_part = Parser.add_parentheses_if_needed(first_part)
                second_part = Parser.add_parentheses_if_needed(second_part)
            
                # Replace the biconditional operator with its CNF equivalent
                sentence = (
                    sentence[:start_parenthesis] +
                    ['('] +
                    ['(', '~'] + first_part + ['||'] + second_part + [')'] +
                    ['&'] +
                    ['(', '~'] + second_part + ['||'] + first_part + [')'] +
                    [')'] +
                    sentence[end_parenthesis+1:]
                )

        return sentence

    @staticmethod
    def eliminate_implication(sentence: list[str]) -> list[str]:
        """Eliminate implication operators from the sentence."""
        while "=>" in sentence:
            i = sentence.index("=>")
            start_parenthesis = Parser.find_start_parenthesis(sentence, i)

            if start_parenthesis == -1:
                # No parentheses around the expressions, split the sentence
                # eg. a => b becomes ~a || b
                first_part = sentence[:i]
                second_part = sentence[i + 1:]

                # Avoid unnecessary parentheses
                first_part = Parser.add_parentheses_if_needed(first_part)
                second_part = Parser.add_parentheses_if_needed(second_part)

                sentence = ['~'] + first_part + ['||'] + second_part
            else:
                # Parentheses around the expressions, split the clause
                # eg. (a <=> b) & c becomes ((~a || b) & (~b || a)) & c
                first_part = sentence[start_parenthesis+1:i]
                end_parenthesis = Parser.find_end_parenthesis(sentence, start_parenthesis)
                second_part = sentence[i + 1:end_parenthesis]

                # Avoid unnecessary parentheses
                first_part = Parser.add_parentheses_if_needed(first_part)
                second_part = Parser.add_parentheses_if_needed(second_part) 
            
                # Replace the biconditional operator with its CNF equivalent
                sentence = (
                    sentence[:start_parenthesis] +
                    ['(', '~'] + first_part + ['||'] + second_part + [')'] +
                    sentence[end_parenthesis+1:]
                )

        return sentence

    @staticmethod
    def apply_de_morgan(sentence: list[str]) -> list[str]:
        """Apply De Morgan's laws to the sentence."""
        if len(sentence) == 0:
            return sentence
        
        if sentence[0] == "(" and Parser.find_end_parenthesis(sentence, 0) == len(sentence) - 1:
            sentence = sentence[1:len(sentence)-1]

        if len(sentence) == 1:
            return ['~'] + sentence
        
        if sentence[0] == "~":
            if len(sentence[1:len(sentence)]) == 1:
                return sentence[1:len(sentence)]
            elif sentence[1] == "(":
                end_clause_index = Parser.find_end_parenthesis(sentence, 1)
                if end_clause_index == len(sentence) - 1:
                    return sentence[1:end_clause_index+1]
                else:
                    return sentence[1:end_clause_index+1] + CNFConverter.apply_de_morgan(sentence[end_clause_index+1:len(sentence)])
                    
        converted_clauses = []
        start_clause_index = 0   

        if "||" in sentence:
            for i in range(len(sentence)):
                if sentence[i] == "||":
                    start_parenthesis_idx = Parser.find_start_parenthesis(sentence, i)
                    if start_parenthesis_idx == -1:
                        sub_clause = sentence[start_clause_index:i]
                        converted_sub_clause = CNFConverter.apply_de_morgan(sub_clause)

                        if len(converted_clauses) != 0:
                            converted_clauses += ["&"]
                        start_clause_index = i + 1

                        converted_clauses += Parser.add_parentheses_if_needed(converted_sub_clause)
                elif i == len(sentence) - 1 and start_clause_index != 0:
                    sub_clause = sentence[start_clause_index:]
                    converted_sub_clause = CNFConverter.apply_de_morgan(sub_clause)
                    if len(converted_clauses) != 0:
                        converted_clauses += ["&"]
                    
                    converted_clauses += Parser.add_parentheses_if_needed(converted_sub_clause)

        if "&" in sentence:
            start_clause_index = 0
            for i in range(len(sentence)):
                if sentence[i] == "&":
                    start_parenthesis_idx = Parser.find_start_parenthesis(sentence, i)
                    if start_parenthesis_idx == -1:
                        sub_clause = sentence[start_clause_index:i]
                        converted_sub_clause = CNFConverter.apply_de_morgan(sub_clause)

                        if len(converted_clauses) != 0:
                            converted_clauses += ["||"]
                        start_clause_index = i + 1

                        converted_clauses += Parser.add_parentheses_if_needed(converted_sub_clause)
                elif i == len(sentence) - 1 and start_clause_index != 0:
                    sub_clause = sentence[start_clause_index:]
                    converted_sub_clause = CNFConverter.apply_de_morgan(sub_clause)
                    if len(converted_clauses) != 0:
                        converted_clauses += ["||"]
                    
                    converted_clauses += Parser.add_parentheses_if_needed(converted_sub_clause)

        return converted_clauses
        
    @staticmethod
    def move_negations_inwards(sentence: list[str]) -> list[str]:
        """Move negations inwards in the sentence."""
        valid = False
        while not valid:
            valid = True

            for i in range(len(sentence)):
                if sentence[i] == '~': 
                    if sentence[i+1] == '(':
                        valid = False
                        end_parenthesis = Parser.find_end_parenthesis(sentence, i + 1)
                        converted_clause = CNFConverter.apply_de_morgan(sentence[i+1:end_parenthesis+1])

                        if len(sentence[:i]) != 0 or end_parenthesis < len(sentence) - 1:
                            converted_clause = Parser.add_parentheses_if_needed(converted_clause)

                        sentence = sentence[:i] + converted_clause + sentence[end_parenthesis+1:]
                        break

                    elif sentence[i+1] == '~':
                        valid = False
                        if len(sentence[i+2:len(sentence)]) == 1:
                            sentence = sentence[:i] + sentence[i+2]
                        else:
                            if sentence[i+2] == '(':
                                end_parenthesis = Parser.find_end_parenthesis(sentence, i + 2)
                                sub_clause = sentence[i+2:end_parenthesis+1]

                                if len(sentence[:i]) != 0 or end_parenthesis < len(sentence) - 1:
                                    sub_clause = Parser.add_parentheses_if_needed(sub_clause)
                                    sentence = sentence[:i] + sub_clause + sentence[end_parenthesis+1:]
                            else:
                                sentence = sentence[:i] + [sentence[i+2]] + sentence[i+2:]
                        break
            
        return sentence

    @staticmethod
    def distribute_or_over_and(sentence: list[str]) -> list[str]:
        """Distribute OR over AND in the sentence."""
        if len(sentence) <= 2:
            return sentence

        include_outermost_parenthesis = False
        if sentence[0] == '(' and Parser.find_end_parenthesis(sentence, 0) == len(sentence) - 1:
            include_outermost_parenthesis = True
            sentence = sentence[1:-1]

        clauses, operations = Parser.extract_clauses(sentence)
        clauses = [CNFConverter.distribute_or_over_and(clause) for clause in clauses]

        if operations.count("&") == len(operations) - 2:
            for i in range(len(clauses)):
                if len(clauses[i]) > 2:
                    sub_operations = Parser.extract_clauses(clauses[i])[1]

                    if sub_operations.count("&") == len(sub_operations) - 2:
                        clauses[i] = clauses[i][1:-1]
            
            if include_outermost_parenthesis:
                return Parser.add_parentheses_if_needed(Parser.reconstruct_clause(clauses, ["&"]))
            else:
                return Parser.reconstruct_clause(clauses, ["&"])
            
        elif operations.count("||") == len(operations) - 2:
            valid = False
            while not valid:
                valid = True
                
                for i in range(len(clauses)):
                    if len(clauses[i]) > 2:
                        sub_clauses, sub_operations = Parser.extract_clauses(clauses[i])

                        if sub_operations.count("||") == len(sub_operations) - 2:
                            valid = False
                            clauses.pop(i)

                            for sub_clause in sub_clauses:
                                clauses.insert(i, sub_clause)
                            break
                            
                        elif sub_operations.count("&") == len(sub_operations) - 2:
                            valid = False
                            if len(clauses) == 2:
                                clauses.pop(i)
                                distributing_clause = clauses.pop(0)
                            else:
                                clauses.pop(i)
                                distributing_clause = clauses.pop(i%len(clauses))

                            distributed_sub_clauses = []
                            for sub_clause in sub_clauses:
                                distributed_sub_clauses.append(["("] + sub_clause + ['||'] + distributing_clause + [")"])

                            clauses.append(CNFConverter.distribute_or_over_and(["("] + Parser.reconstruct_clause(distributed_sub_clauses, ["&"]) + [")"]))

                            if len(clauses) == 1:
                                clauses[0] = Parser.remove_paratheses_if_needed(clauses[0])

                            if include_outermost_parenthesis:
                                return Parser.add_parentheses_if_needed(CNFConverter.distribute_or_over_and(Parser.reconstruct_clause(clauses, ["&"])))
                            else:
                                return CNFConverter.distribute_or_over_and(Parser.reconstruct_clause(clauses, ["&"]))
                            
            return Parser.add_parentheses_if_needed(Parser.reconstruct_clause(clauses, ["||"]))

        else:
            or_clauses, and_clauses = Parser.organize_sentence(clauses, operations)
            sentence = ["("] + Parser.reconstruct_clause(and_clauses, "&") + [")", "||"] + Parser.reconstruct_clause(or_clauses, ["||"])
            return CNFConverter.distribute_or_over_and(sentence)

    @staticmethod
    def convert_sentence(sentence: list[str]) -> list[str]:
        # print(sentence)
        """Convert the sentence to CNF."""
        if sentence[0] == '(' and Parser.find_end_parenthesis(sentence, 0) == len(sentence) - 1:
            sentence = sentence[1:-1]

        sentence = CNFConverter.eliminate_biconditional(sentence) # Eliminate the biconditional operator
        sentence = CNFConverter.eliminate_implication(sentence)   # Eliminate the implication operator
        sentence = CNFConverter.move_negations_inwards(sentence)  # Move negations inwards
        sentence = CNFConverter.distribute_or_over_and(sentence)  # Distribute OR over AND
        
        return sentence