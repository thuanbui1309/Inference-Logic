import re
from collections import deque
from typing import Dict, List, Tuple

class ForwardChaining:
    def __init__(self, filename: str):
        # Quy tắc lưu dưới dạng { conclusion: [([premises], is_negated)] }
        self.rules: Dict[str, List[Tuple[List[Tuple[str, bool]], bool]]] = {}
        # Sự kiện lưu trữ với cờ phủ định
        self.facts: Dict[str, bool] = {}
        self.query: Tuple[str, bool] = None
        self.derived_facts = set()  # Tập hợp sự kiện được suy diễn trong quá trình chạy
        self.entailments = []  # Danh sách các ký hiệu đã suy diễn
        self.parse_kb_and_query(filename)

    def parse_kb_and_query(self, filename: str) -> None:
        """Phân tích file đầu vào để lấy KB và truy vấn."""
        with open(filename, 'r') as file:
            content = file.read()

        # Tách phần TELL và ASK
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+(.*)', content).group(1).strip()

        # Phân tích các điều kiện trong TELL
        clauses = tell_part.split(";")
        for clause in clauses:
            clause = clause.strip()
            if "=>" in clause:
                # Phân tích vế trái và vế phải
                premises, conclusion = clause.split("=>")
                premises = [
                    (p.strip().lstrip("~"), p.strip().startswith("~")) for p in premises.split("&")
                ]
                conclusion = conclusion.strip().lstrip("~")
                is_negated_conclusion = clause.strip().startswith("~")
                
                # Thêm vào self.rules
                if conclusion not in self.rules:
                    self.rules[conclusion] = []
                self.rules[conclusion].append((premises, is_negated_conclusion))
            else:
                # Nếu là sự kiện
                literal = clause.strip().lstrip("~")
                is_negated = clause.strip().startswith("~")
                self.facts[literal] = not is_negated

        # Lưu truy vấn với cờ phủ định nếu có
        self.query = (ask_part.strip().lstrip("~"), ask_part.strip().startswith("~"))

    def run(self):
        """Chạy thuật toán và in kết quả YES hoặc NO với yêu cầu định dạng."""
        # Khởi tạo các sự kiện đã biết
        agenda = deque([fact for fact, is_true in self.facts.items() if is_true])
        self.derived_facts = set(agenda)  # Theo dõi các sự kiện đã suy diễn

        while agenda:
            fact = agenda.popleft()
            self.entailments.append(fact)  # Thêm vào danh sách suy diễn
            # Kiểm tra nếu sự kiện trùng với truy vấn
            if fact == self.query[0] and self.facts[fact] == (not self.query[1]):
                print(f"YES: {', '.join(self.entailments)}")
                return

            # Xử lý các quy tắc có `fact` trong tiền đề của chúng
            for conclusion, rules in self.rules.items():
                for premises, is_negated_conclusion in rules:
                    # Kiểm tra nếu tất cả tiền đề có trong các sự kiện đã suy diễn
                    if all((p in self.derived_facts) == (not neg) for p, neg in premises):
                        if conclusion not in self.derived_facts:
                            agenda.append(conclusion)
                            self.derived_facts.add(conclusion)
                            self.facts[conclusion] = not is_negated_conclusion
                        
        # Nếu không thể suy diễn ra truy vấn
        print("NO")
