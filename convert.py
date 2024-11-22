from parser import Parser
from converter import CNFConverter

clause_1 = Parser.find_all_words("(((A || B) & (C => D)) <=> (E || F)) => (((G & H) || (I <=> J)) => (K & L))")
clause_2 = Parser.find_all_words("(a => b) & c")
clause_3 = Parser.find_all_words("~(A || (B & ~C)) || D")
clause_4 = Parser.find_all_words("((A || B) => C) & (D || ~(E => F))")
clause_5 = Parser.find_all_words("(a & b) => (c || d)")

output = CNFConverter.convert_sentence(clause_1)

for character in output:
    print(character, end="")

# print(CNFConverter.convert_sentence(clause_2))
# print(CNFConverter.convert_sentence(clause_3))
# print(CNFConverter.convert_sentence(clause_4))
# print(CNFConverter.convert_sentence(clause_5))