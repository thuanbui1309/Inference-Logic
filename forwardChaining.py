from typing import List, Dict, Tuple, Deque
from collections import deque
import re
from logic import Literal  # Importing Literal class from logic.py

class ForwardChaining:
    def __init__(self, filename: str):
        # Khởi tạo các biến cho cơ sở tri thức
        self.rules: Dict[str, Tuple[int, List[Literal]]] = {}  # Lưu các quy tắc dưới dạng {kết luận: (số lượng điều kiện, danh sách các điều kiện)}
        self.facts: Deque[Literal] = deque()  # Hàng đợi cho các facts ban đầu
        self.checked_list: List[str] = []  # Danh sách lưu thứ tự các node đã kiểm tra
        self.query: Literal = None  # Câu truy vấn cần suy ra
        self.parse_kb_and_query(filename)  # Phân tích file đầu vào để lấy KB và query

    # Phương thức parse_kb_and_query phân tích cơ sở tri thức và câu truy vấn từ file đầu vào
    def parse_kb_and_query(self, filename: str) -> None:
        with open(filename, 'r') as file:
            content = file.read()

        # Tách phần TELL (KB) và ASK (query)
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+([\s\S]*)', content).group(1).strip()
        
        # Thiết lập câu truy vấn
        self.query = Literal(ask_part.strip())

        # Phân tích các facts và quy tắc từ phần TELL
        for clause in tell_part.split(';'):
            clause = clause.strip()
            if '=>' in clause:
                # Phân tích các quy tắc dưới dạng premises => conclusion
                premises, conclusion = clause.split('=>')
                premises_list = [Literal(p.strip()) for p in premises.split('&')]  # Danh sách điều kiện là các Literal
                conclusion_literal = Literal(conclusion.strip())  # Kết luận là một Literal
                # Lưu quy tắc với dạng {conclusion: (số lượng điều kiện, danh sách điều kiện)}
                self.rules[conclusion_literal.name] = (len(premises_list), premises_list)
            elif clause:  # Các fact đơn không có '=>'
                self.facts.append(Literal(clause.strip()))  # Thêm vào hàng đợi ban đầu cho các facts

    # Phương thức run thực hiện suy diễn tiến và trả về kết quả
    def run(self) -> None:
        while self.facts:
            current_fact = self.facts.popleft()  # Lấy fact đầu tiên từ hàng đợi
            self.checked_list.append(current_fact.name)  # Thêm fact vào danh sách đã kiểm tra
            
            # Kiểm tra nếu fact hiện tại là câu truy vấn
            if current_fact.name == self.query.name:
                # Trả về kết quả YES với thứ tự các node đã kiểm tra
                print("YES: " + ", ".join(self.checked_list))
                return

            # Duyệt qua các quy tắc để xem fact này có thỏa mãn điều kiện cho bất kỳ kết luận nào không
            for conclusion, (remaining_count, premises) in list(self.rules.items()):
                if current_fact.name in [p.name for p in premises]:
                    # Giảm số lượng điều kiện chưa thỏa mãn
                    updated_count = remaining_count - 1
                    new_premises = [p for p in premises if p.name != current_fact.name]  # Cập nhật danh sách điều kiện
                    
                    # Cập nhật lại quy tắc với số lượng điều kiện và danh sách điều kiện mới
                    self.rules[conclusion] = (updated_count, new_premises)

                    # Nếu tất cả các điều kiện thỏa mãn, thêm kết luận vào hàng đợi
                    if updated_count == 0:
                        self.facts.append(Literal(conclusion))
                        # Sau khi thỏa mãn, xóa quy tắc để tránh kiểm tra lặp lại
                        del self.rules[conclusion]

        # Nếu hàng đợi trống và câu truy vấn chưa được tìm thấy
        print("NO")  # Trả về NO khi không thể suy ra câu truy vấn
