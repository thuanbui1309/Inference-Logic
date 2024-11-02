from logic import Literal, Operation
from typing import List, Optional
import re

class TreeNode:
    def __init__(self, literal: Literal):
        self.literal = literal
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None

class ForwardChaining:
    def __init__(self, filename: str):
        self.literals = {}
        self.kb = []
        self.query = None
        self.parse_kb_and_query(filename)

    def add_fact_to_tree(self, root: Optional[TreeNode], literal: Literal) -> TreeNode:
        if root is None:
            return TreeNode(literal)
        elif literal.name < root.literal.name:
            root.left = self.add_fact_to_tree(root.left, literal)
        elif literal.name > root.literal.name:
            root.right = self.add_fact_to_tree(root.right, literal)
        return root

    def fact_in_tree(self, root: Optional[TreeNode], literal: Literal) -> bool:
        if root is None:
            return False
        elif root.literal.name == literal.name:
            return True
        elif literal.name < root.literal.name:
            return self.fact_in_tree(root.left, literal)
        else:
            return self.fact_in_tree(root.right, literal)

    def parse_kb_and_query(self, filename: str):
        with open(filename, 'r') as file:
            content = file.read()
        
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+([\s\S]*)', content).group(1).strip()

        for lit in re.findall(r'[a-zA-Z]+', tell_part + ask_part):
            if lit not in self.literals:
                self.literals[lit] = Literal(lit)

        for clause in tell_part.split(';'):
            if clause.strip():
                tokens = re.findall(r'[a-zA-Z]+|[<=>]+|[~&()]', clause)
                self.kb.append(self.parse_operation(tokens))

        self.query = self.literals[ask_part.strip()]

    def parse_operation(self, tokens: List[str]) -> Operation:
        if len(tokens) == 1:
            return self.literals[tokens[0]]
        if tokens[0] == '~':
            return Operation('~', [self.literals[tokens[1]]])
        if tokens[1] == '&':
            return Operation('&', [self.literals[tokens[0]], self.literals[tokens[2]]])
        elif tokens[1] == '=>':
            return Operation('=>', [self.literals[tokens[0]], self.literals[tokens[2]]])

    def run(self) -> str:
        root = None
        implications = [clause for clause in self.kb if isinstance(clause, Operation) and clause.name == '=>']
        
        for clause in self.kb:
            if isinstance(clause, Literal):
                root = self.add_fact_to_tree(root, clause)

        added_new_fact = True
        while added_new_fact:
            added_new_fact = False
            for implication in implications:
                premises = implication.premises[:-1]
                conclusion = implication.premises[-1]
                if self.fact_in_tree(root, conclusion):
                    continue
                if all(self.fact_in_tree(root, p) for p in premises):
                    root = self.add_fact_to_tree(root, conclusion)
                    added_new_fact = True
                    if self.fact_in_tree(root, self.query):
                        known_facts = []
                        self.collect_facts(root, known_facts)
                        print("YES: " + ', '.join([f.name for f in known_facts]))
                        return
        print("NO")

    def collect_facts(self, root: Optional[TreeNode], known_facts: List[Literal]):
        if root:
            self.collect_facts(root.left, known_facts)
            known_facts.append(root.literal)
            self.collect_facts(root.right, known_facts)
