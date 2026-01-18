from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout,QHBoxLayout,QPushButton,QFrame,QLabel,QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values

import sys
import os

env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
Username = env_vars.get("Username", "User")
current_dir = os.getcwd()
old_chat_message = ""

TempDirPath = fr"{current_dir}\Frontend\Files"
GraphicsDirPath = fr"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer


def QueryModifier(query):
    new_query = query.lower().strip()
    query_words = new_query.split()

    question_words = [
        "how", "what", "who", "where", "when", "why", "which",
        "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    if any(word in new_query for word in question_words):
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "?"
    else:
        if query_words[-1][-1] not in ['.', '?', '!']:
            new_query = new_query + "."

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(f"{TempDirPath}\\Mic.data", "w", encoding="utf-8") as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(f"{TempDirPath}\\Mic.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status


def SetAssistantStatus(Status):
    with open(rf"{TempDirPath}\Status.data", "w", encoding="utf-8") as file:
        file.write(Status)


def GetAssistantStatus():
    with open(rf"{TempDirPath}\Status.data", "r", encoding="utf-8") as file:
        Status = file.read()
    return Status


def MicButtonInitialed():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def GraphicsDirectoryPath(Filename):
    Path = rf"{GraphicsDirPath}\{Filename}"
    return Path


def TempDirectoryPath(Filename):
    Path = rf"{TempDirPath}\{Filename}"
    return Path


def ShowTextToScreen(Text):
    """Append new text instead of overwriting"""
    try:
        # Read existing content
        if os.path.exists(rf"{TempDirPath}\Responses.data"):
            with open(rf"{TempDirPath}\Responses.data", "r", encoding="utf-8") as file:
                existing_content = file.read()
        else:
            existing_content = ""
        
        # Append new text with newline if there's existing content
        if existing_content and not Text.startswith(Username) and not Text.startswith(Assistantname):
            updated_content = existing_content + "\n" + Text
        else:
            updated_content = existing_content + "\n" + Text if existing_content else Text
        
        # Write back
        with open(rf"{TempDirPath}\Responses.data", "w", encoding="utf-8") as file:
            file.write(updated_content)
    except Exception as e:
        print(f"Error in ShowTextToScreen: {e}")


class ImageDisplayWidget(QWidget):
    """Generated images display करण्यासाठी widget"""
    
    def __init__(self):
        super().__init__()
        self.image_layout = QHBoxLayout()
        self.image_layout.setSpacing(10)
        self.setLayout(self.image_layout)
        self.setStyleSheet("background-color: black;")
        self.image_labels = []
        
        # Timer to check for new images
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.load_generated_images)
        self.timer.start(1000)  # Check every 1 second
        
        self.last_loaded_images = []
    
    def load_generated_images(self):
        """Generated images load करा"""
        result_file = TempDirectoryPath("GeneratedImages.data")
        
        if not os.path.exists(result_file):
            return
        
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not lines:
                return
            
            # Get image paths
            image_paths = [line.strip() for line in lines[1:] if line.strip() and os.path.exists(line.strip())]
            
            # Check if new images
            if image_paths == self.last_loaded_images:
                return
            
            # Clear previous images
            self.clear_images()
            
            # Display new images
            for img_path in image_paths[:4]:  # Maximum 4 images
                self.add_image(img_path)
            
            self.last_loaded_images = image_paths
            
        except Exception as e:
            print(f"Error loading images: {e}")
    
    def clear_images(self):
        """सर्व images clear करा"""
        for label in self.image_labels:
            label.deleteLater()
        self.image_labels.clear()
    
    def add_image(self, image_path):
        """Single image add करा"""
        try:
            label = QLabel()
            pixmap = QPixmap(image_path)
            
            # Resize to fit
            scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            label.setPixmap(scaled_pixmap)
            label.setStyleSheet("border: 2px solid white; padding: 5px;")
            label.setAlignment(Qt.AlignCenter)
            
            self.image_layout.addWidget(label)
            self.image_labels.append(label)
            
        except Exception as e:
            print(f"Error displaying image {image_path}: {e}")


class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))

        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel()
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.LoadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)  # Changed from 5ms to 100ms for better performance

        self.chat_text_edit.viewport().installEventFilter(self)

        # Scrollbar stylesheet
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: black;
            }
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }

            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }

            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position: top;
                subcontrol-origin: margin;
                height: 10px;
            }

            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                border: none;
                background: none;
                color: none;
            }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Track if we've loaded initial messages
        self.initial_load = True

    def LoadMessages(self):
        """Load and display chat messages"""
        global old_chat_message

        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding="utf-8") as file:
                messages = file.read()
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Error reading Responses.data: {e}")
            return

        # Skip if empty or unchanged
        if not messages or len(messages.strip()) <= 1:
            return

        if str(old_chat_message) == str(messages):
            return

        # Clear and reload all messages
        self.chat_text_edit.clear()
        
        # Split messages by lines and format them
        lines = messages.strip().split("\n")
        
        for line in lines:
            if not line.strip():
                continue
                
            # Determine color based on speaker
            if line.startswith(Username) or "User" in line[:20]:
                color = QColor(100, 200, 255)  # Light blue for user
            elif line.startswith(Assistantname) or "Assistant" in line[:20]:
                color = QColor(100, 255, 100)  # Light green for assistant
            else:
                color = QColor(255, 255, 255)  # White for other text
            
            self.addMessage(line, color)
        
        # Auto-scroll to bottom
        scrollbar = self.chat_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        old_chat_message = messages

    def SpeechRecogText(self):
        """Update status label"""
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
            self.label.setText(messages)
        except:
            pass

    def addMessage(self, message, color):
        """Add a single message to the chat display"""
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(cursor.End)
        
        fmt = QTextCharFormat()
        fmt.setForeground(color)
        
        block_fmt = QTextBlockFormat()
        block_fmt.setTopMargin(5)
        block_fmt.setLeftMargin(10)
        block_fmt.setBottomMargin(5)
        
        cursor.setBlockFormat(block_fmt)
        cursor.setCharFormat(fmt)
        cursor.insertText(message + "\n")
        
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath("Mic_on.png"))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        
        self.label = QLabel()
        self.label.setStyleSheet("color: white; font-size:16px ; margin-bottom:0;")
        
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(100)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            self.label.setText(messages)
        except:
            pass

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        label = QLabel()
        layout.addWidget(label)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath('Home.png'))
        home_button.setIcon(home_icon)
        home_button.setText("  Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")

        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText("  Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")

        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath("Maximize.png"))
        self.restore_icon = QIcon(GraphicsDirectoryPath("Minimize.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)

        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")

        title_label = QLabel(f"  {str(Assistantname).capitalize()} AI  ")
        title_label.setStyleSheet("color: black; font-size: 18px; background-color:white")

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))

        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen(self)
        message_screen = MessageScreen(self)
        
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()