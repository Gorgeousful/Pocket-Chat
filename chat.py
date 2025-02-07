#================================================
#* Author: 斑斓GORGEOUS
#* Time: 2025-02-08

#? 使用说明:
#? 在运行脚本 python3 chat.py 这是先决条件（可以根据操作系统创建桌面图标来运行）
#? 按快捷键 <ctrl>+<f1> 即可在光标处弹出对话框
#? 输入问题按Enter发送，按Esc退出
#? 按Esc退出后，再次按快捷键 <ctrl>+<f1> 即可在光标处弹出对话框
#? 另外Linux支持打开窗口时，将选中的文本自动填充到输入框

#TODO 用户仅修改以下内容即可
API_URL = "https://api.deepseek.com/v1" #DeepSeek API URL  其他模型API也行
API_KEY = "sk-c1f60975345d46c496d6e7ef0faf232c" #DeepSeek API Key  其他模型API也行
MODEL = "deepseek-chat" #默认是DeepSeekV3模型，可也用DeepSeekR1，即deepseek-reasoner。其他模型也行。
TEMPERATURE = 1.0 #值约高，回答越随机。
SHORTCUT = "<ctrl>+<f1>" #对话框快捷键
#================================================

from openai import OpenAI
from pynput import keyboard
import threading
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QPushButton
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QIcon, QFont, QCursor
import platform
import subprocess

global_is_processing = False
text_last = ""
system = platform.system()

class ChatAPI:
    def __init__(self):
        self.message_history = []  # 存储对话历史  
    def call_api(self, prompt, callback):
        client = OpenAI(api_key=API_KEY, base_url=API_URL)
        self.message_history.append({"role": "user", "content": prompt})
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.message_history,  
                stream=True,
                temperature=TEMPERATURE,
            )
            collected_content = []
            for chunk in response:
                if not global_is_processing:
                    break
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_content.append(content)
                    callback(content)
            assistant_response = ''.join(collected_content)
            self.message_history.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            callback(f"\nError: {str(e)}")
            return None

class StreamSignals(QObject):
    update_text = Signal(str)
    finished = Signal()  

class QADialog(QDialog):
    def __init__(self):
        super().__init__()
        self.chat_api = ChatAPI()  # 创建 ChatAPI 实例
        self.init_ui()
        self.setup_signals()
        self.move_to_cursor()
        self.apply_styles()  
        self.old_pos = None 
 
    def init_ui(self):
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)  # 添加无边框效果
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)  # 设置边距
        self.setLayout(layout)
        
        # 输入区域
        input_layout = QHBoxLayout()
        self.question_entry = QLineEdit()
        self.question_entry.returnPressed.connect(self.get_answer)
        self.question_entry.setPlaceholderText("在此输入问题，按Enter发送，按Esc退出...")
        self.question_entry.setFont(QFont("微软雅黑", 10))
        
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_answer)
        self.stop_button.setEnabled(False)
        self.stop_button.setFixedWidth(60)
        self.stop_button.setAutoDefault(False)  # 防止停止按键被enter触发
        
        input_layout.addWidget(self.question_entry)
        input_layout.addWidget(self.stop_button)
        layout.addLayout(input_layout)
        
        # 输出区域
        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        self.answer_text.setFont(QFont("微软雅黑", 10))
        layout.addWidget(self.answer_text)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        self.clear_button = QPushButton("清空对话")
        self.clear_button.clicked.connect(self.clear_content)
        self.clear_button.setEnabled(False)
        bottom_layout.addWidget(self.clear_button)
        layout.addLayout(bottom_layout)
        
    def setup_signals(self):
        self.signals = StreamSignals()
        self.signals.update_text.connect(self.update_stream)
        self.signals.finished.connect(self.on_response_finished)
               
    def get_answer(self):
        global global_is_processing
        if global_is_processing:
            return
        question = self.question_entry.text().strip()
        if not question:
            return
        global_is_processing = True

        self.question_entry.clear()
        self.question_entry.setPlaceholderText("思考中...")
        self.question_entry.setReadOnly(True)
        self.stop_button.setEnabled(True)
        self.clear_button.setEnabled(False)
        self.answer_text.append("<br><b style='color: #D05A6E;'>Q:</b>")
        self.answer_text.append(f"{question}")
        self.answer_text.append("<br><b style='color: #51A8DD;'>A:</b><br>")
        
        self.current_thread = threading.Thread(
            target=self.process_answer, 
            args=(question,)
        )
        self.current_thread.daemon = True
        self.current_thread.start()
    
    def process_answer(self, question):
        try:
            response = self.chat_api.call_api(  # 使用实例方法
                question,
                lambda content: self.signals.update_text.emit(content)
            )
        finally:
            self.signals.finished.emit()
            
    def update_stream(self, content):
        cursor = self.answer_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.answer_text.setTextCursor(cursor)
        self.answer_text.insertPlainText(content)

    def on_response_finished(self):
        global global_is_processing
        global_is_processing = False
        self.stop_button.setEnabled(False)
        self.clear_button.setEnabled(True)
        self.question_entry.setReadOnly(False)
        self.question_entry.setPlaceholderText("在此输入问题，按Enter发送，按Esc退出...")
        self.question_entry.setFocus()
    
    def stop_answer(self):
        self.signals.finished.emit()
    
    def clear_content(self):
        self.answer_text.clear()
        self.chat_api.message_history = []  # 清空对话历史
    
    def closeEvent(self, event):
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def mouseMoveEvent(self, event):
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def apply_styles(self):
        # 设置整体样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 1px solid #404040;
                border-radius: 10px;
            }
            QLineEdit {
                padding: 8px;
                background-color: #363636;
                border: 1px solid #404040;
                border-radius: 5px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border: 1px solid #5294e2;
            }            
            QPushButton {
                padding: 8px 15px;
                background-color: #5294e2;
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #60a5f7;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QTextEdit {
                background-color: #363636;
                border: 1px solid #404040;
                border-radius: 5px;
                color: #ffffff;
                padding: 8px;
            }
            QTextEdit:focus {
                border: 1px solid #5294e2;
            }
        """)

    def move_to_cursor(self):
        # 获取鼠标光标位置
        cursor_pos = QCursor.pos()
        # 获取窗口大小
        window_size = self.size()
        # 调整窗口位置，使其不超出屏幕边界
        x = min(cursor_pos.x(), QApplication.primaryScreen().size().width() - window_size.width())
        y = min(cursor_pos.y(), QApplication.primaryScreen().size().height() - window_size.height())
        self.move(x, y)

def get_global_selection():
    """获取全局选中的文本"""
    global text_last
    if system == "Linux":
        text = subprocess.check_output(['xclip', '-o', '-selection', 'primary'], 
                                        stderr=subprocess.DEVNULL).decode('utf-8').strip()
        if text == text_last:
            return ""
        text_last = text
        return text
    else:
        print("目前仅支持Linux")
        return ""

def show_qa_dialog():
    global text_last
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    dialog = QADialog()
    text = get_global_selection().strip()
    dialog.question_entry.setText(text)
    dialog.question_entry.setFocus()
    dialog.show()
    app.exec()

def main():
    with keyboard.GlobalHotKeys({SHORTCUT: show_qa_dialog}) as h:
        h.join()            

if __name__ == "__main__":
    print('🤖 Chat Start!')
    if system == "Linux":
        subprocess.run(['xclip', '-selection', 'primary', '-i', '/dev/null'])
    main()