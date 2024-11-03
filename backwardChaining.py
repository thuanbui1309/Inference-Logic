import re
from collections import deque
from typing import Dict, List, Tuple

class BackwardChaining:
    def __init__(self, filename: str):
        # Quy tắc lưu dưới dạng { conclusion: [([premises], is_negated)] }
        self.rules: Dict[str, List[Tuple[List[Tuple[str, bool]], bool]]] = {}
        # Sự kiện lưu trữ với cờ phủ định
        self.facts: Dict[str, bool] = {}
        self.query: Tuple[str, bool] = None
        self.checked_literals: List[str] = []  # Danh sách các literals đã kiểm tra
        self.prevent_infinite = set()  # Ngăn vòng lặp đệ quy
        self.parse_kb_and_query(filename)

    def parse_kb_and_query(self, filename: str) -> None:
        """Phân tích file đầu vào để lấy KB và query."""
        with open(filename, 'r') as file:
            content = file.read()

        # Tách phần TELL và ASK
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+(.*)', content).group(1).strip()

        # Tách các điều kiện trong TELL
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
                is_negated_conclusion = conclusion.startswith("~")
                
                # Thêm vào self.rules
                if conclusion not in self.rules:
                    self.rules[conclusion] = []
                self.rules[conclusion].append((premises, is_negated_conclusion))
            else:
                # Nếu là fact
                literal = clause.strip().lstrip("~")
                is_negated = clause.strip().startswith("~")
                self.facts[literal] = not is_negated  # Thêm trạng thái phủ định vào facts

        # Lưu truy vấn với cờ phủ định nếu có
        self.query = (ask_part.strip().lstrip("~"), ask_part.strip().startswith("~"))

    def run(self):
        """Chạy thuật toán và in kết quả YES hoặc NO."""
        result = self.DoesEntail(*self.query)
        if result:
            print("YES: " + ", ".join(self.checked_literals))
        else:
            print("NO")

    def DoesEntail(self, literal_name: str, is_negated: bool) -> bool:
        """Kiểm tra xem literal có thể suy diễn từ KB không."""
        result = self.TruthValue(literal_name, is_negated)
        return result if not is_negated else not result

    def TruthValue(self, literal_name: str, is_negated: bool) -> bool:
        """
        Đệ quy kiểm tra literal có thể đúng không.
        """
        # Kiểm tra nếu là sự kiện đã biết
        if literal_name in self.facts:
            value = self.facts[literal_name]
            if is_negated:
                return not value
            else:
                if literal_name not in self.checked_literals:
                    self.checked_literals.append(literal_name)
                return value

        if literal_name in self.prevent_infinite:
            return False

        # Thêm vào prevent_infinite để tránh đệ quy vô hạn
        self.prevent_infinite.add(literal_name)
        print(f"{self.prevent_infinite} thêm {literal_name}")

        # Kiểm tra các quy tắc
        if literal_name in self.rules: #Kiểm tra xem có conclusion nào trùng với tên đang tìm kiếm không
            #literal_name là "x", ta sẽ kiểm tra xem có quy tắc nào có kết luận x không (chẳng hạn, a & ~c => x).
            for premises, conclusion_negated in self.rules[literal_name]:
                if conclusion_negated == is_negated: #đảm bảo rằng chỉ khi nào các phủ định của kết luận và literal trùng khớp, quy tắc mới được đánh giá tiếp. Giả dụ a => b hoặc là ~a => ~b 
                    # Kiểm tra tất cả premises với trạng thái phủ định
                    if all(self.TruthValue(p, neg) for p, neg in premises):
                        self.prevent_infinite.remove(literal_name) #đảm bảo rằng khi quay lại các đệ quy cấp cao hơn, literal_name có thể được kiểm tra lại nếu cần mà không bị chặn bởi self.prevent_infinite
                        print(f"{self.prevent_infinite} xóa {literal_name}")
                        if literal_name not in self.checked_literals:
                            self.checked_literals.append(literal_name)
                        return True

        # Quay lui nếu không suy diễn được
        self.prevent_infinite.remove(literal_name)
        print(f"{self.prevent_infinite} xóa {literal_name}")
        return False if not is_negated else True
