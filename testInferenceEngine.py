import unittest
from unittest.mock import patch
from io import StringIO
from parser import Parser
from converter import CNFConverter
from forwardChaining import ForwardChaining
from backwardChaining import BackwardChaining
from resolution import Resolution
from dpll import DPLL
from truthTable import TruthTable


class TestMapSolver(unittest.TestCase):

    def setUp(self):
        # Test FC and BC Implication Horn Form
        self.file_horn_1 = "test_HornKB.txt"
        self.file_horn_2 = "test_case/test_Horn_Implication_1.txt"
        self.file_horn_3 = "test_case/test_Horn_Implication_2.txt"
        self.file_horn_4 = "test_case/test_Horn_Implication_3.txt"
        self.file_horn_5 = "test_case/test_Horn_Implication_4.txt"

        # Test FC and BC Disjunction Horn Form
        self.file_horn_6 = "test_case/test_Horn_Disjunction_1.txt"
        self.file_horn_7 = "test_case/test_Horn_Disjunction_2.txt"
        
        # Test FC and BC Mix Horn Form
        self.file_horn_8 = "test_case/test_Horn_Mix_1.txt"
        self.file_horn_9 = "test_case/test_Horn_Mix_2.txt"
        self.file_horn_10 = "test_case/test_Horn_Mix_3.txt"
        self.file_horn_11 = "test_case/test_Horn_Mix_4.txt"
        self.file_horn_12 = "test_case/test_Horn_Mix_5.txt"

        #Test Generic  
        self.file_generic_1 = "test_case/test_Generic_1.txt"
        self.file_generic_2 = "test_case/test_Generic_2.txt"
        self.file_generic_3 = "test_case/test_Generic_3.txt"
        self.file_generic_4 = "test_case/test_Generic_4.txt"
        self.file_generic_5 = "test_case/test_Generic_5.txt"
        self.file_generic_6 = "test_case/test_Generic_6.txt"
        self.file_generic_7 = "test_case/test_Generic_7.txt"
        self.file_generic_8 = "test_case/test_Generic_8.txt"
        self.file_generic_9 = "test_case/test_Generic_9.txt"
        self.file_generic_10 = "test_case/test_Generic_10.txt"
    
    # Test parser
    def test_findAllWords_returnCorrectList(self):
        clause_1 = "(a <=> (c => ~d)) & b & (b => a)"
        clause_2 = "~d & (~g => ~f)"
        clause_3 = "p2&p1&p3=>d"

        output_1 = Parser.find_all_words(clause_1)
        output_2 = Parser.find_all_words(clause_2)
        output_3 = Parser.find_all_words(clause_3)

        expected_output_1 = ['(', 'a', '<=>', '(', 'c', '=>', '~', 'd', ')', ')', '&', 'b', '&', '(', 'b', '=>', 'a', ')']
        expected_output_2 = ['~', 'd', '&', '(', '~', 'g', '=>', '~', 'f', ')']
        expected_output_3 = ['p2', '&', 'p1', '&', 'p3', '=>', 'd']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)

    def test_findStartParenthesis_returnCorrectIndex(self):
        sentence_1 = ['(', 'a', '=>', 'b', ')']
        sentence_2 = ['(', 'a', '=>', '(', 'b', '=>', 'c', ')', ')']
        sentence_3 = ['a', '=>', '(', 'b', '=>', 'c', ')']

        output_1 = Parser.find_start_parenthesis(sentence_1, 3)
        output_2 = Parser.find_start_parenthesis(sentence_2, 7)
        output_3 = Parser.find_start_parenthesis(sentence_3, 5)

        self.assertEqual(output_1, 0)
        self.assertEqual(output_2, 3)
        self.assertEqual(output_3, 2)

    def test_findEndParenthesis_returnCorrectIndex(self):
        sentence_1 = ['(', 'a', '=>', 'b', ')']
        sentence_2 = ['(', 'a', '=>', '(', 'b', '=>', 'c', ')', ')']
        sentence_3 = ['a', '=>', '(', 'b', '=>', 'c', ')']

        output_1 = Parser.find_end_parenthesis(sentence_1, 0)
        output_2 = Parser.find_end_parenthesis(sentence_2, 0)
        output_3 = Parser.find_end_parenthesis(sentence_3, 2)

        self.assertEqual(output_1, 4)
        self.assertEqual(output_2, 8)
        self.assertEqual(output_3, 6)

    def test_addParenthesesIfNeeded_returnCorrectClause(self):
        clause_1 = ['a', '=>', 'b']
        clause_2 = ['(', 'a', '=>', 'b', ')']
        clause_3 = ['a']

        output_1 = Parser.add_parentheses_if_needed(clause_1)
        output_2 = Parser.add_parentheses_if_needed(clause_2)
        output_3 = Parser.add_parentheses_if_needed(clause_3)

        self.assertEqual(output_1, ['(', 'a', '=>', 'b', ')'])
        self.assertEqual(output_2, ['(', 'a', '=>', 'b', ')'])
        self.assertEqual(output_3, ['a'])

    def test_removeParenthesesIfNeeded_returnCorrectClause(self):
        clause_1 = ['(', 'a', '=>', 'b', ')']
        clause_2 = ['a', '=>', 'b']
        clause_3 = ['(', 'a', ')']

        output_1 = Parser.remove_paratheses_if_needed(clause_1)
        output_2 = Parser.remove_paratheses_if_needed(clause_2)
        output_3 = Parser.remove_paratheses_if_needed(clause_3)

        self.assertEqual(output_1, ['a', '=>', 'b'])
        self.assertEqual(output_2, ['a', '=>', 'b'])
        self.assertEqual(output_3, ['a'])

    def test_extractLiterals_returnCorrectList(self):
        expression_1 = ['a', '=>', 'b']
        expression_2 = ['~', 'a', '||', 'b']
        expression_3 = ['(', 'a', '&', 'b', ')']

        output_1 = Parser.extract_literals(expression_1)
        output_2 = Parser.extract_literals(expression_2)
        output_3 = Parser.extract_literals(expression_3)

        self.assertEqual(output_1, ['a', 'b'])
        self.assertEqual(output_2, ['a', 'b'])
        self.assertEqual(output_3, ['a', 'b'])

    def test_extractLiteralsWithSigned_returnCorrectList(self):
        expression_1 = ['a', '=>', 'b']
        expression_2 = ['~', 'a', '||', 'b']
        expression_3 = ['(', 'a', '&', 'b', ')']

        output_1 = Parser.extract_literals_with_signed(expression_1)
        output_2 = Parser.extract_literals_with_signed(expression_2)
        output_3 = Parser.extract_literals_with_signed(expression_3)

        self.assertEqual(output_1, [('a', False), ('b', False)])
        self.assertEqual(output_2, [('a', True), ('b', False)])
        self.assertEqual(output_3, [('a', False), ('b', False)])

    def test_extractClauses_returnCorrectList(self):
        expression_1 = ['a', '||', 'b']
        expression_2 = ['~', 'a', '||', 'b']
        expression_3 = ['(', 'a', '&', 'b', ')']
        expression_4 = ['(', 'a', '||', 'b', ')', '&', '(', 'c', '||', 'd', ')']
        expression_5 = ['(', '~', 'a', '&', 'b', ')', '||', '(', 'c', '&', 'd', ')']

        output_1 = Parser.extract_clauses(expression_1)
        output_2 = Parser.extract_clauses(expression_2)
        output_3 = Parser.extract_clauses(expression_3)
        output_4 = Parser.extract_clauses(expression_4)
        output_5 = Parser.extract_clauses(expression_5)

        self.assertEqual(output_1, ([['a'], ['b']], [None, '||', None]))
        self.assertEqual(output_2, ([['~', 'a'], ['b']], [None, '||', None]))
        self.assertEqual(output_3, ([['a'], ['b']], [None, '&', None]))
        self.assertEqual(output_4, ([['(', 'a', '||', 'b', ')'], ['(', 'c', '||', 'd', ')']], [None, '&', None]))
        self.assertEqual(output_5, ([['(', '~', 'a', '&', 'b', ')'], ['(', 'c', '&', 'd', ')']], [None, '||', None]))  
    
    def test_organizeSentence_returnCorrectTuple(self):
        clauses_1 = [['a'], ['b']]
        operations_1 = [None, '&', None]
        clauses_2 = [['a'], ['b']]
        operations_2 = [None, '||', None]
        clauses_3 = [['a'], ['b'], ['c']]
        operations_3 = [None, '&', '||', None]

        output_1 = Parser.organize_sentence(clauses_1, operations_1)
        output_2 = Parser.organize_sentence(clauses_2, operations_2)
        output_3 = Parser.organize_sentence(clauses_3, operations_3)

        self.assertEqual(output_1, ([], [['a'], ['b']]))
        self.assertEqual(output_2, ([['a'], ['b']], []))
        self.assertEqual(output_3, ([['c']], [['a'], ['b']]))

    def test_reconstructClause_returnCorrectList(self):
        clause_1 = [['a'], ['b']]
        operation_1 = ['&']
        clause_2 = [['a'], ['b']]
        operation_2 = ['||']
        clause_3 = [['a'], ['b'], ['c']]
        operation_3 = ['&']

        output_1 = Parser.reconstruct_clause(clause_1, operation_1)
        output_2 = Parser.reconstruct_clause(clause_2, operation_2)
        output_3 = Parser.reconstruct_clause(clause_3, operation_3)

        self.assertEqual(output_1, ['a', '&', 'b'])
        self.assertEqual(output_2, ['a', '||', 'b'])
        self.assertEqual(output_3, ['a', '&', 'b', '&', 'c'])

    def test_isHornForm_returnCorrectBoolean(self):
        tell_part_1 = "a => b; c"
        tell_part_2 = "a <=> b"
        tell_part_3 = "~a || b"

        output_1 = Parser.is_horn_form(tell_part_1)
        output_2 = Parser.is_horn_form(tell_part_2)
        output_3 = Parser.is_horn_form(tell_part_3)

        self.assertTrue(output_1)
        self.assertFalse(output_2)
        self.assertTrue(output_3)

    def test_disjunction_to_implication(self):
        cases = [
            ("~a || b", "a => b"),
            ("~a || ~b || c", "a & b => c"),
        ]
        for disjunction, expected_output in cases:
            output = Parser.disjunction_to_implication(disjunction)
            if expected_output is False:
                self.assertFalse(output)
            else:
                self.assertEqual(output, expected_output)

    # Test CNF Converter
    def test_eliminateBiconditional_returnCorrectClause(self):
        clause_1 = Parser.find_all_words("a <=> b")
        clause_2 = Parser.find_all_words("(a <=> b) & c")
        clause_3 = Parser.find_all_words("(a <=> b) <=> (c <=> d)")
        clause_4 = Parser.find_all_words("a & (b <=> c)")
        clause_5 = Parser.find_all_words("(a <=> b) <=> (c <=> d)")

        output_1 = CNFConverter.eliminate_biconditional(clause_1)
        output_2 = CNFConverter.eliminate_biconditional(clause_2)
        output_3 = CNFConverter.eliminate_biconditional(clause_3)
        output_4 = CNFConverter.eliminate_biconditional(clause_4)
        output_5 = CNFConverter.eliminate_biconditional(clause_5)

        expected_output_1 = ['(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')']
        expected_output_2 = ['(', '(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')', ')', '&', 'c']
        expected_output_3 = ['(', '~', '(', '(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')', ')', '||', '(', '(', '~', 'c', '||', 'd', ')', '&', '(', '~', 'd', '||', 'c', ')', ')', ')', '&', '(', '~', '(', '(', '~', 'c', '||', 'd', ')', '&', '(', '~', 'd', '||', 'c', ')', ')', '||', '(', '(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')', ')', ')']
        expected_output_4 = ['a', '&', '(', '(', '~', 'b', '||', 'c', ')', '&', '(', '~', 'c', '||', 'b', ')', ')']
        expected_output_5 = ['(', '~', '(', '(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')', ')', '||', '(', '(', '~', 'c', '||', 'd', ')', '&', '(', '~', 'd', '||', 'c', ')', ')', ')', '&', '(', '~', '(', '(', '~', 'c', '||', 'd', ')', '&', '(', '~', 'd', '||', 'c', ')', ')', '||', '(', '(', '~', 'a', '||', 'b', ')', '&', '(', '~', 'b', '||', 'a', ')', ')', ')']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)
        self.assertEqual(output_4, expected_output_4)
        self.assertEqual(output_5, expected_output_5)
        
    def test_eliminateImplication_returnCorrectClause(self):
        clause_1 = Parser.find_all_words("a => b")
        clause_2 = Parser.find_all_words("(a => b) & c")
        clause_3 = Parser.find_all_words("(a => b) => (c => d)")
        clause_4 = Parser.find_all_words("a => (b & c)")
        clause_5 = Parser.find_all_words("(a & b) => (c || d)")

        output_1 = CNFConverter.eliminate_implication(clause_1)
        output_2 = CNFConverter.eliminate_implication(clause_2)
        output_3 = CNFConverter.eliminate_implication(clause_3)
        output_4 = CNFConverter.eliminate_implication(clause_4)
        output_5 = CNFConverter.eliminate_implication(clause_5)

        expected_output_1 = ['~', 'a', '||', 'b']
        expected_output_2 = ['(', '~', 'a', '||', 'b', ')', '&', 'c']
        expected_output_3 = ['~', '(', '~', 'a', '||', 'b', ')', '||', '(', '~', 'c', '||', 'd', ')']
        expected_output_4 = ['~', 'a', '||', '(', 'b', '&', 'c', ')']
        expected_output_5 = ['~', '(', 'a', '&', 'b', ')', '||', '(', 'c', '||', 'd', ')']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)
        self.assertEqual(output_4, expected_output_4)
        self.assertEqual(output_5, expected_output_5)
    
    def test_move_negations_inwards(self):
        clause_1 = Parser.find_all_words("~(a & b)")
        clause_2 = Parser.find_all_words("~(a || b)")
        clause_3 = Parser.find_all_words("~(~a & b)")
        clause_4 = Parser.find_all_words("~(a & ~b)")
        clause_5 = Parser.find_all_words("~(~a || ~b)")

        output_1 = CNFConverter.move_negations_inwards(clause_1)
        output_2 = CNFConverter.move_negations_inwards(clause_2)
        output_3 = CNFConverter.move_negations_inwards(clause_3)
        output_4 = CNFConverter.move_negations_inwards(clause_4)
        output_5 = CNFConverter.move_negations_inwards(clause_5)

        expected_output_1 = ['~', 'a', '||', '~', 'b']
        expected_output_2 = ['~', 'a', '&', '~', 'b']
        expected_output_3 = ['a', '||', '~', 'b']
        expected_output_4 = ['~', 'a', '||', 'b']
        expected_output_5 = ['a', '&', 'b']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)
        self.assertEqual(output_4, expected_output_4)
        self.assertEqual(output_5, expected_output_5)

    def test_distribute_or_over_and(self):
        clause_1 = Parser.find_all_words("a || (b & c)")
        clause_2 = Parser.find_all_words("(a & b) || c")
        clause_3 = Parser.find_all_words("(a || b) & c")
        clause_4 = Parser.find_all_words("a & (b || c)")
        clause_5 = Parser.find_all_words("(a || b) & (c || d)")

        output_1 = CNFConverter.distribute_or_over_and(clause_1)
        output_2 = CNFConverter.distribute_or_over_and(clause_2)
        output_3 = CNFConverter.distribute_or_over_and(clause_3)
        output_4 = CNFConverter.distribute_or_over_and(clause_4)
        output_5 = CNFConverter.distribute_or_over_and(clause_5)

        expected_output_1 = ['(', 'b', '||', 'a', ')', '&', '(', 'c', '||', 'a', ')']
        expected_output_2 = ['(', 'a', '||', 'c', ')', '&', '(', 'b', '||', 'c', ')']
        expected_output_3 = ['(', 'a', '||', 'b', ')', '&', 'c']
        expected_output_4 = ['a', '&', '(', 'b', '||', 'c', ')']
        expected_output_5 = ['(', 'a', '||', 'b', ')', '&', '(', 'c', '||', 'd', ')']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)
        self.assertEqual(output_4, expected_output_4)
        self.assertEqual(output_5, expected_output_5)

    def test_convert_sentence(self):
        clause_1 = Parser.find_all_words("a")
        clause_2 = Parser.find_all_words("(a => b) & c")
        clause_3 = Parser.find_all_words("~(A || (B & ~C)) || D")
        clause_4 = Parser.find_all_words("((A || B) => C) & (D || ~(E => F))")
        clause_5 = Parser.find_all_words("(a & b) => (c || d)")

        output_1 = CNFConverter.convert_sentence(clause_1)
        output_2 = CNFConverter.convert_sentence(clause_2)
        output_3 = CNFConverter.convert_sentence(clause_3)
        output_4 = CNFConverter.convert_sentence(clause_4)
        output_5 = CNFConverter.convert_sentence(clause_5)

        expected_output_1 = ['a']
        expected_output_2 = ['(', '~', 'a', '||', 'b', ')', '&', 'c']
        expected_output_3 = ['(', '~', 'A', '||', 'D', ')', '&', '(', 'C', '||', '~', 'B', '||', 'D', ')']
        expected_output_4 = ['(', '~', 'A', '||', 'C', ')', '&', '(', '~', 'B', '||', 'C', ')', '&', '(', 'E', '||', 'D', ')', '&', '(', '~', 'F', '||', 'D', ')']
        expected_output_5 = ['(', '~', 'b', '||', '~', 'a', '||', 'd', '||', 'c', ')']

        self.assertEqual(output_1, expected_output_1)
        self.assertEqual(output_2, expected_output_2)
        self.assertEqual(output_3, expected_output_3)
        self.assertEqual(output_4, expected_output_4)
        self.assertEqual(output_5, expected_output_5)

    # Test Truth Table
    def test_truth_table(self):
        cases = [
            # Test Horn Form
            (self.file_horn_1, "YES: 3"),
            (self.file_horn_2, "YES: 14"),
            (self.file_horn_3, "YES: 2"),

            #Test Generic
            (self.file_generic_1, "YES: 3"),
            (self.file_generic_2, "YES: 9"),
            (self.file_generic_3, "YES: 3"),
            (self.file_generic_4, "YES: 7"),
            (self.file_generic_5, "YES: 10"),
            (self.file_generic_6, "YES: 28"),
            (self.file_generic_7, "YES: 6"),
            (self.file_generic_8, "YES: 1"),
            (self.file_generic_9, "YES: 13"),
            (self.file_generic_10, "YES: 3"),
        ]
        for file, expected_output in cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                TruthTable(file).infer()
                output = mock_stdout.getvalue().strip()
            self.assertEqual(output, expected_output)
    
    # Test Forward Chaining
    def test_forward_chaining(self):
        cases = [
            # Test Implication Horn Form
            (self.file_horn_1, "YES: a, b, p2, p3, p1, d"),
            (self.file_horn_2, "YES: a, b, x, y, z, w, u, v"),
            (self.file_horn_3, "YES: a, b, d, x, y, z, w, v"),
            (self.file_horn_4, "YES: a, b, c, e, x, y, v"),
            (self.file_horn_5, "NO"),

            #Test Disjunction Horn Form
            (self.file_horn_6, "YES: a, b, p2, p3, p1, d"),
            (self.file_horn_7, "NO"),

            # Test Mix Horn Form
            (self.file_horn_8, "YES: a, b, p2, p3, p1, d"),
            (self.file_horn_9, "YES: a, b, x, y, z, w, u, v"),
            (self.file_horn_10, "YES: a, b, d, x, y, z, w, v"),
            (self.file_horn_11, "YES: a, b, c, e, x, y, v"),
            (self.file_horn_12, "NO"),
        ]
        for file, expected_output in cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                ForwardChaining(file).infer()
                output = mock_stdout.getvalue().strip()
            self.assertEqual(output, expected_output)
    
    # Test Backward Chaining
    def test_backward_chaining(self):
        cases = [
            (self.file_horn_1, "YES: p2, p3, p1, d"),
            (self.file_horn_2, "YES: a, x, b, y, u, z, w, v"),
            (self.file_horn_3, "YES: a, x, b, y, z, d, w, v"),
            (self.file_horn_4, "YES: c, a, b, x, y, v"),
            (self.file_horn_5, "NO"),
            
            #Test Disjunction Horn Form
            (self.file_horn_6, "YES: p2, p3, p1, d"),
            (self.file_horn_7, "NO"),

            # Test Mix Horn Form
            (self.file_horn_8, "YES: p2, p3, p1, d"),
            (self.file_horn_9, "YES: a, x, b, y, u, z, w, v"),
            (self.file_horn_10, "YES: a, x, b, y, z, d, w, v"),
            (self.file_horn_11, "YES: c, a, b, x, y, v"),
            (self.file_horn_12, "NO"),
        ]
        for file, expected_output in cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                BackwardChaining(file).infer()  # Hàm in ra kết quả
                output = mock_stdout.getvalue().strip()  # Lấy kết quả từ stdout

            # So sánh kết quả
            self.assertEqual(output, expected_output)
    
    # Test Resolution
    def test_resolution(self):
        cases = [
            # Test Implication Horn Form
            (self.file_horn_1, "YES"),
            (self.file_horn_2, "YES"),
            (self.file_horn_3, "YES"),
            (self.file_horn_4, "YES"),

            #Test Generic
            (self.file_generic_1, "YES"),
            (self.file_generic_2, "YES"),
            (self.file_generic_3, "YES"),
            (self.file_generic_4, "YES"),
        ]

        i = 1
        for file, expected_output in cases:
            i += 1
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                Resolution(file).infer()
                output = mock_stdout.getvalue().strip()
            self.assertEqual(output, expected_output)
    
    # Test DPLL
    def test_dpll(self):
        cases = [
            # Test Implication Horn Form
            (self.file_horn_1, "YES"),
            (self.file_horn_2, "YES"),
            (self.file_horn_3, "YES"),
            (self.file_horn_4, "YES"),

            #Test Generic
            (self.file_generic_1, "YES"),
            (self.file_generic_2, "YES"),
            (self.file_generic_3, "YES"),
            (self.file_generic_4, "YES"),
            (self.file_generic_5, "YES"),
            (self.file_generic_6, "YES"),
            (self.file_generic_7, "YES"),
            (self.file_generic_8, "YES"),
            (self.file_generic_9, "YES"),
            (self.file_generic_10, "YES"),
        ]
        for file, expected_output in cases:
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                DPLL(file).infer()
                output = mock_stdout.getvalue().strip()
            self.assertEqual(output, expected_output)

if __name__ == "__main__":
    unittest.main()