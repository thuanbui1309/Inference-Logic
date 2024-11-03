from typing import List, Dict, Tuple, Deque
from collections import deque
import re
from logic import Literal  # Import lớp Literal từ logic.py

class ForwardChaining:
    def __init__(self, filename: str):
        # Khởi tạo các biến cho cơ sở tri thức
        self.rules: Dict[str, Tuple[int, List[Tuple[Literal, bool]]]] = {}  # Lưu các quy tắc với phủ định
        self.facts: Deque[Literal] = deque()  # Hàng đợi cho các facts ban đầu
        self.checked_list: List[str] = []  # Danh sách lưu thứ tự kiểm tra
        self.query: Literal = None  # Câu truy vấn cần suy ra
        self.parse_kb_and_query(filename)  # Phân tích file đầu vào để lấy KB và query

    def parse_kb_and_query(self, filename: str) -> None:
        # Đọc nội dung từ file
        with open(filename, 'r') as file:
            content = file.read()

        # Tách phần TELL (KB) và ASK (query) từ nội dung
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+([\s\S]*)', content).group(1).strip()
        
        # Thiết lập câu truy vấn
        self.query = Literal(ask_part.strip())

        # Phân tích các facts và quy tắc từ phần TELL
        for clause in tell_part.split(';'):
            clause = clause.strip()
            if '=>' in clause:
                # Phân tích các quy tắc dạng premises => conclusion
                premises, conclusion = clause.split('=>')
                premises_list = []
                for p in premises.split('&'):
                    # Kiểm tra xem premise có phủ định hay không
                    is_negated = p.strip().startswith('~')
                    # Nếu có phủ định, loại bỏ ký tự đầu tiên (~)
                    literal_name = p[1:] if is_negated else p
                    literal = Literal(literal_name.strip())
                    premises_list.append((literal, is_negated))
                # Lưu kết luận của quy tắc
                conclusion_literal = Literal(conclusion.strip())
                self.rules[conclusion_literal.name] = (len(premises_list), premises_list)
                print(f"Mệnh đề sau xử lý có kết luận {conclusion_literal.name} với điều kiện {self.rules[conclusion_literal.name]}")
            elif clause:
                # Xử lý fact nếu không có dấu =>
                is_negated = clause.startswith('~')
                literal_name = clause[1:] if is_negated else clause
                literal = Literal(literal_name.strip())
                # Chỉ thêm fact vào hàng đợi nếu không có phủ định
                if not is_negated:
                    self.facts.append(literal)

    def run(self) -> None:
        # Bắt đầu quá trình suy diễn tiến
        while self.facts:
            # Lấy fact đầu tiên từ hàng đợi
            current_fact = self.facts.popleft()
            # Thêm fact vào danh sách đã kiểm tra
            self.checked_list.append(current_fact.name)
            
            # Kiểm tra nếu fact hiện tại là câu truy vấn
            if current_fact.name == self.query.name:
                print("YES: " + ", ".join(self.checked_list))
                return

            # Kiểm tra các quy tắc với fact hiện tại
            for conclusion, (remaining_count, premises) in list(self.rules.items()):
                # Tìm các premise khớp với fact hiện tại và không phủ định
                match_premise = next((p for p, is_negated in premises if p.name == current_fact.name and not is_negated), None)
                
                if match_premise:
                    # Giảm số lượng điều kiện còn lại của quy tắc
                    updated_count = remaining_count - 1
                    # Cập nhật danh sách premises sau khi loại bỏ premise khớp
                    new_premises = [(p, is_negated) for p, is_negated in premises if p.name != current_fact.name]
                    self.rules[conclusion] = (updated_count, new_premises)

                    # Nếu tất cả các điều kiện đã thỏa mãn, thêm kết luận vào hàng đợi facts
                    if updated_count == 0:
                        self.facts.append(Literal(conclusion))
                        # Xóa quy tắc đã thỏa mãn
                        del self.rules[conclusion]

        # Nếu không tìm thấy kết luận cho câu truy vấn
        print("NO")  # Không tìm thấy truy vấn
