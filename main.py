from turtle import width
from Board import Board
from Gamevars import Gamevars as gamevars
import tkinter as tk

gamevars.root = tk.Tk()
gamevars.root.title("Minesweeper")
gamevars.width, gamevars.height = 240, 270
gamevars.root.geometry(f"{gamevars.width}x{gamevars.height}")
board = Board()
gamevars.root.mainloop()