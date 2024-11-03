import re
from collections import deque
from typing import Dict, List, Tuple

class BackwardChaining:
    def __init__(self, filename: str):
        self.rules: Dict[str, List[List[str]]] = {}  # Các quy tắc KB với phần kết luận và vế trái
        self.facts: deque = deque()  # Các sự kiện đã biết
        self.query = None  # Biến query cần suy luận
        self.checked_literals: List[str] = []  # Danh sách các literals đã kiểm tra
        self.prevent_infinite = set()  # Tránh đệ quy vô hạn
        self.parse_kb_and_query(filename)  # Phân tích KB và query từ file

    def parse_kb_and_query(self, filename: str) -> None:
        """Phân tích file đầu vào để lấy KB và query."""
        with open(filename, 'r') as file:
            content = file.read()

        # Sử dụng regex để lấy phần TELL và ASK
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+(.*)', content).group(1).strip()

        # Tách các điều kiện trong TELL
        clauses = tell_part.split(";")
        for clause in clauses:
            clause = clause.strip()
            if "=>" in clause:
                # Phân tách vế trái và vế phải của mệnh đề
                premises, conclusion = clause.split("=>")
                premises = [p.strip() for p in premises.split("&")]
                conclusion = conclusion.strip()
                # Thêm các mệnh đề vào rules
                if conclusion not in self.rules:
                    self.rules[conclusion] = []
                self.rules[conclusion].append(premises)
            else:
                # Nếu là fact, thêm vào hàng đợi facts
                self.facts.append(clause)

        # Lưu query
        self.query = ask_part

    def run(self):
        """Phương thức chạy thuật toán và in kết quả YES hoặc NO."""
        result = self.DoesEntail(self.query)
        if result:
            print("YES: " + ", ".join(self.checked_literals))
        else:
            print("NO")

    def DoesEntail(self, query: str) -> bool:
        """Kiểm tra xem query có thể được suy ra từ KB hay không."""
        return self.TruthValue(query)

    def TruthValue(self, literal: str) -> bool:
        """
        Hàm đệ quy kiểm tra giá trị đúng sai của literal.
        Nếu literal là một sự kiện đã biết, trả về True.
        """
        if literal in self.facts:
            if literal not in self.checked_literals:
                self.checked_literals.append(literal)
            return True

        if literal in self.prevent_infinite:
            return False

        # Thêm literal vào prevent_infinite để tránh đệ quy vô hạn
        self.prevent_infinite.add(literal)

        # Kiểm tra các mệnh đề mà literal xuất hiện ở vế phải
        if literal in self.rules:
            for premises in self.rules[literal]:
                if all(self.TruthValue(premise) for premise in premises):
                    self.prevent_infinite.remove(literal)
                    if literal not in self.checked_literals:
                        self.checked_literals.append(literal)
                    return True

        # Quay lui nếu không suy diễn được literal
        self.prevent_infinite.remove(literal)
        return False
