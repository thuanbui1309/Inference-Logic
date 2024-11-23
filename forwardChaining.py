import re
from collections import deque
from typing import Dict, List, Tuple, Optional
from parser import Parser  

class ForwardChaining:
    def __init__(self, filename: str):
        """
        Initialize the ForwardChaining object with the given filename.

        Args:
            filename (str): The name of the file containing the knowledge base and query.
        """
        # Rules stored as { conclusion: [([premises], is_negated)] }
        self.rules: Dict[str, List[Tuple[List[Tuple[str, bool]], bool]]] = {}
        # Facts stored with negation flag
        self.facts: Dict[str, bool] = {}
        self.query: Optional[Tuple[str, bool]] = None
        self.derived_facts = set()  # Set of facts derived during execution
        self.entailments = []  # List of derived symbols
        self.parse_kb_and_query(filename)

    def parse_kb_and_query(self, filename: str) -> None:
        """
        Parse the input file to get the knowledge base (KB) and query.

        Args:
            filename (str): The name of the file containing the knowledge base and query.
        """
        with open(filename, 'r') as file:
            content = file.read()

        # Separate TELL and ASK parts
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()[:-1]
        ask_part = re.search(r'ASK\s+(.*)', content).group(1).strip()

        # Check if the input is in Horn form
        if not Parser.is_horn_form(tell_part):
            print("The input knowledge base is not in Horn form.")
            exit(1)
        # Parse conditions in TELL
        clauses = tell_part.split(";")
        for clause in clauses:
            clause = clause.strip()
            if "||" in clause:
                # Convert disjunction to implication
                clause = Parser.disjunction_to_implication(clause)
            if "=>" in clause:
                # Parse left-hand side and right-hand side
                premises, conclusion = clause.split("=>")
                premises = [
                    (p.strip().lstrip("~"), p.strip().startswith("~")) for p in premises.split("&")
                ]
                conclusion = conclusion.strip().lstrip("~")
                is_negated_conclusion = clause.strip().startswith("~")
                
                # Add to self.rules
                if conclusion not in self.rules:
                    self.rules[conclusion] = []
                self.rules[conclusion].append((premises, is_negated_conclusion))
            else:
                # If it is a fact
                literal = clause.strip().lstrip("~")
                is_positive = clause.strip().startswith("~")
                self.facts[literal] = not is_positive

        # Store query with negation flag if any
        self.query = (ask_part.strip().lstrip("~"), ask_part.strip().startswith("~"))

    def infer(self) -> None:
        """
        Run the forward chaining algorithm and print YES or NO with the required format.
        """
        # Initialize known facts
        agenda = deque([fact for fact, is_true in self.facts.items() if is_true])
        self.derived_facts = set(agenda)

        while agenda:
            fact = agenda.popleft()
            self.entailments.append(fact)

            # Check if fact matches the query
            if fact == self.query[0] and self.facts[fact] == (not self.query[1]):
                print(f"YES: {', '.join(self.entailments)}")
                return

            # Process rules that have `fact` in their premises
            for conclusion, rules in self.rules.items():
                for premises, is_negated_conclusion in rules:
                    # Check if all premises are in derived facts
                    if all((p in self.derived_facts) == (not neg) for p, neg in premises):
                        if conclusion not in self.derived_facts:
                            agenda.append(conclusion)
                            self.derived_facts.add(conclusion)
                            self.facts[conclusion] = not is_negated_conclusion
                        
        # If the query cannot be derived
        print("NO")