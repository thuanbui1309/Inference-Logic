from logic import Literal, Operation
from typing import List, Optional
import re

# Lớp TreeNode đại diện cho một node trong cây nhị phân
class TreeNode:
    def __init__(self, literal: Literal):
        self.literal = literal  # Biến logic (literal) lưu trữ trong node
        self.left: Optional['TreeNode'] = None  # Con trái của node có thể có hoặc không
        self.right: Optional['TreeNode'] = None  # Con phải của node

# Lớp ForwardChaining chứa các phương thức để thực hiện suy diễn bằng cách sử dụng cây nhị phân
class ForwardChaining:
    def __init__(self, filename: str):
        self.literals = {}  # Lưu trữ các biến logic
        self.kb = []  # Cơ sở tri thức (knowledge base)
        self.query = None  # Câu truy vấn (query)
        self.parse_kb_and_query(filename)  # Gọi hàm để phân tích file đầu vào

    # Phân tích cơ sở tri thức (KB) và câu truy vấn từ file đầu vào
    def parse_kb_and_query(self, filename: str):
        with open(filename, 'r') as file:
            content = file.read()
        
        # Tách phần TELL (KB) và phần ASK (query)
        tell_part = re.search(r'TELL\s+([\s\S]*?)\s+ASK', content).group(1).strip()
        ask_part = re.search(r'ASK\s+([\s\S]*)', content).group(1).strip()
        print("Đang phân tích cơ sở tri thức và câu truy vấn...")
        
        # Tạo các literal từ KB và query (literal là các)
        for lit in re.findall(r'\b[a-zA-Z][a-zA-Z0-9]*\b', tell_part + ask_part):
            if lit not in self.literals:
                print(f"Dữ liệu đơn là {lit}")
                self.literals[lit] = Literal(lit)

        # Tạo các mệnh đề logic từ các câu trong TELL
        for clause in tell_part.split(';'):
            if clause.strip():
                tokens = re.findall(r'[a-zA-Z]+|[<=>]+|[~&()]', clause)
                operation = self.parse_operation(tokens)
                self.kb.append(operation)

        # Thiết lập câu truy vấn (query)
        self.query = self.literals[ask_part.strip()]

    # Phân tích cú pháp mệnh đề logic từ chuỗi token
    def parse_operation(self, tokens: List[str]) -> Operation:
        if len(tokens) == 1:
            return self.literals[tokens[0]]
        if tokens[0] == '~':
            return Operation('~', [self.literals[tokens[1]]])
        if tokens[1] == '&':
            return Operation('&', [self.literals[tokens[0]], self.literals[tokens[2]]])
        elif tokens[1] == '=>':
            return Operation('=>', [self.literals[tokens[0]], self.literals[tokens[2]]])

    # Thêm một fact vào cây nhị phân
    def add_fact_to_tree(self, root: Optional[TreeNode], literal: Literal) -> TreeNode:
        if root is None:
            return TreeNode(literal)
        elif literal.name < root.literal.name:
            root.left = self.add_fact_to_tree(root.left, literal)
        elif literal.name > root.literal.name:
            root.right = self.add_fact_to_tree(root.right, literal)
        return root

    # Kiểm tra xem một fact có tồn tại trong cây nhị phân hay không
    def fact_in_tree(self, root: Optional[TreeNode], literal: Literal) -> bool:
        if root is None:
            return False
        elif root.literal.name == literal.name:
            return True
        elif literal.name < root.literal.name:
            return self.fact_in_tree(root.left, literal)
        else:
            return self.fact_in_tree(root.right, literal)

    # Thực hiện suy diễn Forward Chaining
    def run(self) -> str:
        root = None  # Gốc của cây nhị phân để lưu các facts
        implications = [clause for clause in self.kb if isinstance(clause, Operation) and clause.name == '=>']
        
        print("Thêm các facts khởi tạo vào cây...")
        for clause in self.kb:
            if isinstance(clause, Literal):
                root = self.add_fact_to_tree(root, clause)

        added_new_fact = True  # Đánh dấu nếu có fact mới được thêm vào cây
        while added_new_fact:
            added_new_fact = False
            for implication in implications:
                premises = implication.premises[:-1]  # Các điều kiện của mệnh đề
                conclusion = implication.premises[-1]  # Kết luận của mệnh đề
                print(f"Đang đánh giá mệnh đề: {' & '.join([p.name for p in premises])} => {conclusion.name}")

                if self.fact_in_tree(root, conclusion):
                    print(f"Kết luận {conclusion.name} đã tồn tại, bỏ qua.")
                    continue

                if all(self.fact_in_tree(root, p) for p in premises):
                    print(f"Tất cả điều kiện cho {conclusion.name} đều đúng; thêm kết luận vào cây.")
                    root = self.add_fact_to_tree(root, conclusion)
                    added_new_fact = True

                    if self.fact_in_tree(root, self.query):
                        known_facts = []
                        self.collect_facts(root, known_facts)
                        print("YES: " + ', '.join([f.name for f in known_facts]))
                        return
        print("NO")

    # Thu thập tất cả các facts từ cây nhị phân
    def collect_facts(self, root: Optional[TreeNode], known_facts: List[Literal]):
        if root:
            self.collect_facts(root.left, known_facts)
            known_facts.append(root.literal)
            self.collect_facts(root.right, known_facts)
