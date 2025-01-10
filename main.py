import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import chess
import chess.pgn
import chess.svg
import cairosvg
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import inch
from io import BytesIO
import webbrowser
from PIL import Image, ImageTk
from tkinter import colorchooser

# MIT License
# Copyright (c) 2025 Samuel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# 1. You may not use the name "ChessPdf" or any variations of it in any way
#    without prior permission.
#
# 2. You may not use this software for commercial purposes without explicit
#    permission from the copyright holder.
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

class PGNToPDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ChessPdf")
        self.root.state('zoomed')
        self.light_square_color = tk.StringVar(value="#F0F1F0")
        self.dark_square_color = tk.StringVar(value="#C4D8E4")
        self.root.configure(bg='#F0F0F0')
        self.coffee_image = None
        self.button_size = 80

        self.style = ttk.Style()
        self.style.configure('Custom.TCheckbutton',
                           background='#F0F0F0',
                           font=('Arial', 16))
        
        self.config = self.load_config()
        self.files = []
        self.output_folder = self.config.get("output_folder", "")
        self.flipped = tk.BooleanVar(value=False)
        self.include_comments = tk.BooleanVar(value=True)

        self.board_x = tk.DoubleVar(value=self.config.get("board_x", 1.1))
        self.board_y = tk.DoubleVar(value=self.config.get("board_y", 1.7))
        self.board_size = tk.DoubleVar(value=self.config.get("board_size", 3.8))
        
        self.comment_x = tk.DoubleVar(value=self.config.get("comment_x", 0.75))
        self.comment_y = tk.DoubleVar(value=self.config.get("comment_y", 0.6))
        self.comment_width = tk.DoubleVar(value=self.config.get("comment_width", 4.5))
        self.comment_font_size = tk.DoubleVar(value=self.config.get("comment_font_size", 14))
        
        self.move_x = tk.DoubleVar(value=self.config.get("move_x", 3.0))
        self.move_y = tk.DoubleVar(value=self.config.get("move_y", 1.2))
        self.move_font_size = tk.DoubleVar(value=self.config.get("move_font_size", 15))
        
        self.title_x = tk.DoubleVar(value=self.config.get("title_x", 3.0))
        self.title_y = tk.DoubleVar(value=self.config.get("title_y", 7.25))
        self.title_font_size = tk.DoubleVar(value=self.config.get("title_font_size", 18))
        self.current_config = tk.StringVar(value="none")

        self.info_x = tk.DoubleVar(value=self.config.get("info_x", 3.0))
        self.info_y = tk.DoubleVar(value=self.config.get("info_y", 7.0))
        self.info_font_size = tk.DoubleVar(value=self.config.get("info_font_size", 15))
        self.additional_info_y = tk.DoubleVar(value=self.config.get("additional_info_y", 6.75))

        self.page_width = tk.DoubleVar(value=self.config.get("page_width", 6.0))
        self.page_height = tk.DoubleVar(value=self.config.get("page_height", 8.0))

        self.comment_line_spacing = tk.DoubleVar(value=self.config.get("comment_line_spacing", 0.25))

        self.flipped = tk.BooleanVar(value=self.config.get("white_on_top", False))
        self.include_comments = tk.BooleanVar(value=self.config.get("add_comments", True))

        self.style = ttk.Style()
        self.style.configure('Custom.TCombobox',
                           background='#F0F0F0',
                           fieldbackground='#E8E8E8',
                           foreground='black')
        
        self.style.configure('Custom.TEntry',
                           background='#E8E8E8',
                           fieldbackground='#E8E8E8')

        self.flipped.trace_add("write", self.save_checkbox_states)
        self.include_comments.trace_add("write", self.save_checkbox_states)

        self.setup_ui()

    def save_checkbox_states(self, *args):
        """Guarda el estado de los checkboxes cuando cambian"""
        self.save_config()
    
    def load_config(self):
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                config = json.load(file)
                self.light_square_color.set(config.get("light_square_color", "#F0F1F0"))
                self.dark_square_color.set(config.get("dark_square_color", "#C4D8E4"))
                return config
        return {}

    def choose_light_square_color(self):
        color = colorchooser.askcolor(
            title="Choose light square color",
            color=self.light_square_color.get()
        )
        if color[1]:  # color[1] contiene el código hexadecimal
            self.light_square_color.set(color[1])
            self.light_square_button.configure(bg=color[1])
            self.save_config()

    def choose_dark_square_color(self):
        color = colorchooser.askcolor(
            title="Choose dark square color",
            color=self.dark_square_color.get()
        )
        if color[1]:  # color[1] contiene el código hexadecimal
            self.dark_square_color.set(color[1])
            self.dark_square_button.configure(bg=color[1])
            self.save_config()

    def open_coffee_link(self):
        webbrowser.open('https://paypal.me/chesspdf')

    def save_config(self):
        config = {
            "output_folder": self.output_folder,
            "white_on_top": self.flipped.get(),
            "add_comments": self.include_comments.get(),
            "board_x": self.board_x.get(),
            "board_y": self.board_y.get(),
            "board_size": self.board_size.get(),
            "light_square_color": self.light_square_color.get(),
            "dark_square_color": self.dark_square_color.get(),
            "comment_x": self.comment_x.get(),
            "comment_y": self.comment_y.get(),
            "comment_width": self.comment_width.get(),
            "comment_font_size": self.comment_font_size.get(),
            "move_x": self.move_x.get(),
            "move_y": self.move_y.get(),
            "move_font_size": self.move_font_size.get(),
            "title_x": self.title_x.get(),
            "title_y": self.title_y.get(),
            "title_font_size": self.title_font_size.get(),
            "info_x": self.info_x.get(),
            "info_y": self.info_y.get(),
            "info_font_size": self.info_font_size.get(),
            "additional_info_y": self.additional_info_y.get(),
            "page_width": self.page_width.get(),
            "page_height": self.page_height.get(),
            "comment_line_spacing": self.comment_line_spacing.get()
        }
        config_path = "config.json"
        with open(config_path, "w") as file:
            json.dump(config, file, indent=4)
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#F0F0F0')
        main_frame.pack(padx=40, pady=(0, 30), fill='both', expand=True)

        coffee_container = tk.Frame(main_frame, bg='#F0F0F0')
        coffee_container.pack(fill='x', pady=(20, 30))

        header_container = tk.Frame(coffee_container, bg='#F0F0F0')
        header_container.pack(fill='x')

        title_label = tk.Label(
            header_container,
            text="ChessPdf",
            font=("Helvetica", 42, "bold"),
            bg='#F0F0F0',
            fg='#333333'
        )
        title_label.pack(side='left')

        try:
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'donacion.png')
            image = Image.open(image_path)
            width, height = image.size
            aspect_ratio = width / height
            
            if width > height:
                new_width = self.button_size
                new_height = int(self.button_size / aspect_ratio)
            else:
                new_height = self.button_size
                new_width = int(self.button_size * aspect_ratio)

            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            square_size = max(new_width, new_height)
            square_image = Image.new('RGBA', (square_size, square_size), (0, 0, 0, 0))
            
            paste_x = (square_size - new_width) // 2
            paste_y = (square_size - new_height) // 2
            
            square_image.paste(image, (paste_x, paste_y))
            
            mask = Image.new('L', (square_size, square_size), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, square_size, square_size), fill=255)
            
            output = Image.new('RGBA', (square_size, square_size), (0, 0, 0, 0))
            output.paste(square_image, (0, 0), mask)
            
            self.coffee_image = ImageTk.PhotoImage(output)
            
            coffee_btn = tk.Button(
                header_container,
                image=self.coffee_image,
                bg='#F0F0F0',
                relief='flat',
                bd=0,
                highlightthickness=0,
                command=self.open_coffee_link,
                cursor='hand2'
            )
        except FileNotFoundError:
            coffee_btn = tk.Button(
                header_container,
                text="☕",
                bg='#FFDD00',
                fg='#000000',
                relief='flat',
                font=('Arial', 16),
                command=self.open_coffee_link,
                cursor='hand2',
                padx=5,
                pady=2
            )

        coffee_btn.pack(side='right', padx=(0, 20))
    
        content_frame = tk.Frame(main_frame, bg='#F0F0F0')
        content_frame.pack(fill='both', expand=True)
    
        options_frame = tk.Frame(content_frame, bg='#F0F0F0')
        options_frame.pack(side='left', fill='y', padx=(0, 20))
    
        ttk.Checkbutton(
            options_frame,
            text="White on top",
            cursor='hand2',
            variable=self.flipped,
            style='Custom.TCheckbutton'
        ).pack(anchor='w', pady=5)
    
        ttk.Checkbutton(
            options_frame,
            text="Add comments",
            cursor='hand2',
            variable=self.include_comments,
            style='Custom.TCheckbutton'
        ).pack(anchor='w', pady=5)
    
        config_label = tk.Label(
            options_frame,
            text="Set up item",
            bg='#F0F0F0',
            font=("Arial", 16)
        )
        config_label.pack(anchor='w', pady=(20, 5))

        self.style = ttk.Style()
        self.style.configure(
            'Custom.TCombobox',
            background='#F0F0F0',
            fieldbackground='#E8E8E8',
            foreground='black',
            padding=5
        )

        self.style.configure(
            'TCombobox',
            selectbackground='#0078D7',
            selectforeground='white',
            fieldbackground='white',
            background='white',
            arrowsize=20,
            padding=5
        )

        combo_container = tk.Frame(options_frame, bg='#F0F0F0')
        combo_container.pack(anchor='w', pady=(0, 10))
        combo_container.configure(width=150, height=50)
        combo_container.pack_propagate(False)

        config_combo = ttk.Combobox(
            combo_container,
            cursor='hand2',
            values=[
                "Chessboard",
                "Comments",
                "Move",
                "Title",
                "Additional info",
                "Page size"
            ],
            state="readonly",
            width=30,
            font=('Arial', 12),
            style='Custom.TCombobox'
        )
        config_combo.pack(fill='both', expand=True, padx=5, pady=5)
        config_combo.bind('<<ComboboxSelected>>', lambda e: self.show_config(config_combo.get()))
    
        self.config_frames = {}

        page_size_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Page size"] = page_size_frame
    
        board_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Chessboard"] = board_frame

        light_square_frame = tk.Frame(board_frame, bg='#F0F0F0')
        light_square_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(
            light_square_frame,
            text="Light square:",
            bg='#F0F0F0'
        ).pack(side='left')
        
        self.light_square_button = tk.Button(
            light_square_frame,
            width=8,
            bg=self.light_square_color.get(),
            command=self.choose_light_square_color,
            relief='solid',
            bd=1,
            text="Pick color",
            cursor='hand2'
        )
        self.light_square_button.pack(side='left', padx=5)

        dark_square_frame = tk.Frame(board_frame, bg='#F0F0F0')
        dark_square_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(
            dark_square_frame,
            text="Dark square:",
            bg='#F0F0F0'
        ).pack(side='left')
        
        self.dark_square_button = tk.Button(
            dark_square_frame,
            width=8,
            bg=self.dark_square_color.get(),
            command=self.choose_dark_square_color,
            relief='solid',
            bd=1,
            text="Pick color",
            cursor='hand2'
        )
        self.dark_square_button.pack(side='left', padx=5)
    
        x_frame = tk.Frame(board_frame, bg='#F0F0F0')
        x_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(x_frame, text="X (inches):", bg='#F0F0F0').pack(side='left')
        x_entry = ttk.Entry(x_frame, textvariable=self.board_x, width=10)
        x_entry.pack(side='left', padx=5)
    
        y_frame = tk.Frame(board_frame, bg='#F0F0F0')
        y_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(y_frame, text="Y (inches):", bg='#F0F0F0').pack(side='left')
        y_entry = ttk.Entry(y_frame, textvariable=self.board_y, width=10)
        y_entry.pack(side='left', padx=5)
    
        size_frame = tk.Frame(board_frame, bg='#F0F0F0')
        size_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(size_frame, text="Size (inches)", bg='#F0F0F0').pack(side='left')
        size_entry = ttk.Entry(size_frame, textvariable=self.board_size, width=10)
        size_entry.pack(side='left', padx=5)
    
        comments_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Comments"] = comments_frame
    
        comment_x_frame = tk.Frame(comments_frame, bg='#F0F0F0')
        comment_x_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(comment_x_frame, text="X (inches):", bg='#F0F0F0').pack(side='left')
        comment_x_entry = ttk.Entry(comment_x_frame, textvariable=self.comment_x, width=10)
        comment_x_entry.pack(side='left', padx=5)
    
        comment_y_frame = tk.Frame(comments_frame, bg='#F0F0F0')
        comment_y_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(comment_y_frame, text="Y (inches):", bg='#F0F0F0').pack(side='left')
        comment_y_entry = ttk.Entry(comment_y_frame, textvariable=self.comment_y, width=10)
        comment_y_entry.pack(side='left', padx=5)
    
        comment_width_frame = tk.Frame(comments_frame, bg='#F0F0F0')
        comment_width_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(comment_width_frame, text="Width (inches)", bg='#F0F0F0').pack(side='left')
        comment_width_entry = ttk.Entry(comment_width_frame, textvariable=self.comment_width, width=10)
        comment_width_entry.pack(side='left', padx=5)
    
        comment_size_frame = tk.Frame(comments_frame, bg='#F0F0F0')
        comment_size_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(comment_size_frame, text="Font size", bg='#F0F0F0').pack(side='left')
        comment_size_entry = ttk.Entry(comment_size_frame, textvariable=self.comment_font_size, width=10)
        comment_size_entry.pack(side='left', padx=5)

        line_spacing_frame = tk.Frame(comments_frame, bg='#F0F0F0')
        line_spacing_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(line_spacing_frame, text="Line spacing (inches):", bg='#F0F0F0').pack(side='left')
        line_spacing_entry = ttk.Entry(line_spacing_frame, textvariable=self.comment_line_spacing, width=10)
        line_spacing_entry.pack(side='left', padx=5)
    
        move_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Move"] = move_frame
    
        move_x_frame = tk.Frame(move_frame, bg='#F0F0F0')
        move_x_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(move_x_frame, text="X (inches):", bg='#F0F0F0').pack(side='left')
        move_x_entry = ttk.Entry(move_x_frame, textvariable=self.move_x, width=10)
        move_x_entry.pack(side='left', padx=5)
    
        move_y_frame = tk.Frame(move_frame, bg='#F0F0F0')
        move_y_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(move_y_frame, text="Y (inches):", bg='#F0F0F0').pack(side='left')
        move_y_entry = ttk.Entry(move_y_frame, textvariable=self.move_y, width=10)
        move_y_entry.pack(side='left', padx=5)
    
        move_size_frame = tk.Frame(move_frame, bg='#F0F0F0')
        move_size_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(move_size_frame, text="Font size:", bg='#F0F0F0').pack(side='left')
        move_size_entry = ttk.Entry(move_size_frame, textvariable=self.move_font_size, width=10)
        move_size_entry.pack(side='left', padx=5)
    
        title_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Title"] = title_frame
    
        title_x_frame = tk.Frame(title_frame, bg='#F0F0F0')
        title_x_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(title_x_frame, text="X (inches):", bg='#F0F0F0').pack(side='left')
        title_x_entry = ttk.Entry(title_x_frame, textvariable=self.title_x, width=10)
        title_x_entry.pack(side='left', padx=5)
    
        title_y_frame = tk.Frame(title_frame, bg='#F0F0F0')
        title_y_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(title_y_frame, text="Y (inches):", bg='#F0F0F0').pack(side='left')
        title_y_entry = ttk.Entry(title_y_frame, textvariable=self.title_y, width=10)
        title_y_entry.pack(side='left', padx=5)
    
        title_size_frame = tk.Frame(title_frame, bg='#F0F0F0')
        title_size_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(title_size_frame, text="Font size:", bg='#F0F0F0').pack(side='left')
        title_size_entry = ttk.Entry(title_size_frame, textvariable=self.title_font_size, width=10)
        title_size_entry.pack(side='left', padx=5)
    
        info_frame = tk.LabelFrame(options_frame, text="", bg='#F0F0F0', bd=0)
        self.config_frames["Additional info"] = info_frame
    
        info_x_frame = tk.Frame(info_frame, bg='#F0F0F0')
        info_x_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(info_x_frame, text="X (inches):", bg='#F0F0F0').pack(side='left')
        info_x_entry = ttk.Entry(info_x_frame, textvariable=self.info_x, width=10)
        info_x_entry.pack(side='left', padx=5)
    
        info_y_frame = tk.Frame(info_frame, bg='#F0F0F0')
        info_y_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(info_y_frame, text="Y (inches):", bg='#F0F0F0').pack(side='left')
        info_y_entry = ttk.Entry(info_y_frame, textvariable=self.info_y, width=10)
        info_y_entry.pack(side='left', padx=5)
    
        info_size_frame = tk.Frame(info_frame, bg='#F0F0F0')
        info_size_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(info_size_frame, text="Font size:", bg='#F0F0F0').pack(side='left')
        info_size_entry = ttk.Entry(info_size_frame, textvariable=self.info_font_size, width=10)
        info_size_entry.pack(side='left', padx=5)

        width_frame = tk.Frame(page_size_frame, bg='#F0F0F0')
        width_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(width_frame, text="Width (inches)", bg='#F0F0F0').pack(side='left')
        width_entry = ttk.Entry(width_frame, textvariable=self.page_width, width=10)
        width_entry.pack(side='left', padx=5)

        height_frame = tk.Frame(page_size_frame, bg='#F0F0F0')
        height_frame.pack(fill='x', pady=5, padx=5)
        tk.Label(height_frame, text="Height (inches):", bg='#F0F0F0').pack(side='left')
        height_entry = ttk.Entry(height_frame, textvariable=self.page_height, width=10)
        height_entry.pack(side='left', padx=5)
    
        for frame in self.config_frames.values():
            frame.pack_forget()
    
        self.path_frame = tk.Frame(options_frame, bg='#F0F0F0')
        self.path_frame.pack(fill='x', pady=(10, 10))

        tk.Label(
            self.path_frame,
            text="Output path of the PDF",
            bg='#F0F0F0',
            font=("Arial", 16)
        ).pack(anchor='w')

        path_container = tk.Frame(self.path_frame, bg='#F0F0F0')
        path_container.pack(fill='x', pady=(5, 0))
        path_container.configure(width=400, height=50)
        path_container.pack_propagate(False)

        path_entry_frame = tk.Frame(path_container, bg='white', bd=1, relief='solid')
        path_entry_frame.pack(side='left', fill='x', expand=True)

        self.path_entry = tk.Entry(
            path_entry_frame,
            bg='white',
            relief='flat',
            font=('Arial', 12)
        )
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(5, 0), ipady=5)  # Added internal padding
        self.path_entry.insert(0, self.output_folder)

        browse_btn = tk.Button(
            path_container,
            text="📁",
            bg='#666666',
            fg='white',
            relief='flat',
            font=('Arial', 12),
            cursor='hand2',
            command=self.select_output_folder,
        )

        button_size = 32

        path_container.update()

        container_width = path_container.winfo_width()
        container_height = path_container.winfo_height()

        max_x = container_width - button_size
        max_y = container_height - button_size

        x = min(max(0, 500), max_x)
        y = min(max(0, 9), max_y)

        browse_btn.place(x=x, y=y, width=button_size, height=button_size) 

        convert_btn = tk.Button(
            options_frame,
            text="Convert",
            cursor='hand2',
            bg='#666666',
            fg='white',
            relief='flat',
            font=('Arial', 14, 'bold'),
            padx=20,
            pady=8,
            command=self.convert_files
        )
        convert_btn.pack(pady=(0, 20))
    
        files_container = tk.Frame(content_frame, bg='#E0E0E0', relief='solid', bd=1)
        files_container.pack(side='right', fill='both', expand=True)
    
        self.files_frame = tk.Frame(files_container, bg='#E0E0E0')
        self.files_frame.pack(fill='both', expand=True, padx=10, pady=10)
    
        button_frame = tk.Frame(files_container, bg='#E0E0E0')
        button_frame.pack(fill='x', padx=10, pady=(0, 20))
        
        select_btn = tk.Button(
            button_frame,
            text="Select files",
            cursor='hand2',
            bg='#666666',
            fg='white',
            relief='flat',
            font=('Arial', 16, 'bold'),
            padx=20,
            pady=8,
            command=self.select_files
        )
        select_btn.pack(side='bottom')

    def show_config(self, selected_config):
        for frame in self.config_frames.values():
            frame.pack_forget()
        
        if selected_config in self.config_frames:
            self.config_frames[selected_config].pack(fill='x', pady=10, before=self.path_frame)

    def render_position(self, c, board, game_title, game_info, additional_info, move_number, flipped, include_comments=True, comment=""):
        TITLE_SIZE = self.title_font_size.get()
        INFO_SIZE = self.info_font_size.get()
        MOVE_SIZE = self.move_font_size.get()
        COMMENT_SIZE = self.comment_font_size.get()
        COMMENT_LINE_HEIGHT = self.comment_line_spacing.get() * inch
        
        svg = chess.svg.board(
            board,
            size=1000,
            colors={
                "square light": self.light_square_color.get(),
                "square dark": self.dark_square_color.get(),
            },
            coordinates=False,
            flipped=flipped
        )
        png_data = cairosvg.svg2png(bytestring=svg.encode('utf-8'))
        image_stream = BytesIO(png_data)
        image = ImageReader(image_stream)

        kindle_page_width = self.page_width.get() * inch
        kindle_page_height = self.page_height.get() * inch
        c.setPageSize((kindle_page_width, kindle_page_height))

        c.setFont("Helvetica-Bold", TITLE_SIZE)
        c.drawCentredString(self.title_x.get() * inch, self.title_y.get() * inch, game_title)
        
        margin = 0.75 * inch
        board_size = self.board_size.get() * inch
        
        title_y = kindle_page_height - margin
        info_y = title_y - 0.4 * inch
        additional_y = info_y - 0.3 * inch
        
        board_x = self.board_x.get() * inch
        board_y = self.board_y.get() * inch
        
        move_y = margin + 1.2 * inch

        c.setFont("Helvetica-Bold", TITLE_SIZE)
        c.drawCentredString(kindle_page_width/2, title_y, game_title)

        c.setFont("Helvetica", INFO_SIZE)
        c.drawCentredString(kindle_page_width/2, info_y, game_info)
        c.drawCentredString(kindle_page_width/2, additional_y, additional_info)

        c.drawImage(image, board_x, board_y, width=board_size, height=board_size)

        c.setFont("Helvetica", MOVE_SIZE)
        c.drawCentredString(kindle_page_width/2, move_y, move_number)

        if include_comments and comment:
            c.setFont("Helvetica", COMMENT_SIZE)
            words = comment.split()
            line = ""
            current_y = self.comment_y.get() * inch
            margin = self.comment_x.get() * inch
            max_width = self.comment_width.get() * inch

            for word in words:
                test_line = line + " " + word if line else word
                if c.stringWidth(test_line, "Helvetica", COMMENT_SIZE) < max_width:
                    line = test_line
                else:
                    c.drawString(margin, current_y, line)
                    current_y -= COMMENT_LINE_HEIGHT
                    line = word

                    if current_y < margin:
                        c.showPage()
                        current_y = kindle_page_height - margin
                        c.setFont("Helvetica", COMMENT_SIZE)

            if line:
                c.drawString(margin, current_y, line)

        c.showPage()

    def convert_files(self):
        try:
            
            try:
                x = float(self.board_x.get())
                y = float(self.board_y.get())
                size = float(self.board_size.get())
                if x < 0 or y < 0 or size <= 0:
                    raise ValueError("Positions and size must be positive numbers.")
            except ValueError as e:
                messagebox.showerror("Error: Please enter valid numeric values for the X, Y positions and board size.")
                return

            if not self.files:
                messagebox.showwarning("Warning: Please select at least one PGN file.")
                return

            if not self.output_folder:
                messagebox.showwarning("Warning: Please select an output folder.")
                return

            for file in self.files:
                self.generate_positions_from_pgn(
                    file,
                    self.output_folder,
                    self.flipped.get(),
                    self.include_comments.get()
                )
            
            self.save_config()
            
            messagebox.showinfo("Success: All files have been converted successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while converting the files: {str(e)}")

    def update_files_list(self):
        for widget in self.files_frame.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        
        for file in self.files:
            file_frame = tk.Frame(self.files_frame, bg='#E0E0E0')
            file_frame.pack(fill='x', pady=2)
            
            tk.Button(
                file_frame,
                text="×",
                bg='#E0E0E0',
                fg='#666666',
                relief='flat',
                font=('Arial', 16),
                command=lambda f=file: self.remove_file(f)
            ).pack(side='left', padx=(5, 5))
            
            filename = os.path.basename(file)
            tk.Label(
                file_frame,
                text=filename,
                bg='#E0E0E0',
                font=('Arial', 9)
            ).pack(side='left')

    def remove_file(self, file):
        self.files.remove(file)
        self.update_files_list()

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("PGN Files", "*.pgn")]
        )
        if files:
            self.files = list(files)
            self.update_files_list()

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            self.save_config()

    def generate_positions_from_pgn(self, pgn_path, output_folder, flipped=False, include_comments=True):
        with open(pgn_path, encoding='latin-1') as pgn_file:
            output_pdf = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pgn_path))[0]}.pdf")
            c = canvas.Canvas(output_pdf)

            game_number = 1
            while True:
                game = chess.pgn.read_game(pgn_file)
                if game is None:
                    break

                headers = game.headers
                white = headers.get("White", "Unknown")
                black = headers.get("Black", "Unknown")
                site = headers.get("Site", "")
                date = headers.get("EventDate", "")

                game_title = f"Game {game_number}"
                game_info = f"{white} - {black}"
                additional_info = f"{site}, {date}".strip(', ')

                board = chess.Board()
                self.render_position(
                    c,
                    board,
                    game_title,
                    game_info,
                    additional_info,
                    move_number="Posicion inicial",
                    flipped=flipped,
                    include_comments=include_comments
                )

                node = game
                move_number = 1
                is_white_move = True
                while node.variations:
                    next_node = node.variations[0]
                    move = next_node.move
                    san_move = board.san(move)
                    board.push(move)
                    comment = next_node.comment

                    if is_white_move:
                        formatted_move = f"{move_number}. {san_move}"
                    else:
                        formatted_move = f"{move_number}...{san_move}"
                        move_number += 1

                    self.render_position(
                        c,
                        board,
                        game_title,
                        game_info,
                        additional_info,
                        move_number=formatted_move,
                        flipped=flipped,
                        include_comments=include_comments,
                        comment=comment
                    )
                    is_white_move = not is_white_move
                    node = next_node

                game_number += 1
            c.save()

if __name__ == "__main__":
    root = tk.Tk()
    app = PGNToPDFConverterApp(root)
    root.mainloop()
