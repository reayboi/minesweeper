from email.mime import image
from Gamevars import Gamevars as gamevars
#import Gamevars as gamevars
import tkinter as tk
import random
from PIL import Image, ImageTk
import queue

class Cell():
    def __init__(self, coordinates, position) -> None:
        self.isBomb = False
        self.noSurroundingBombs = 0
        self.isRevealed = False
        self.isFlagged = False
        self.button = None
        self.coordinates = coordinates
        self.position = position
        self.neighbours = []
        self.create_button()
        self.button.bind("<Button>", self.toggle_flag)
        self.flag_img = Image.open("flag.png").resize((gamevars.btnWidth, gamevars.btnHeight)) 
        self.flag_img = ImageTk.PhotoImage(self.flag_img)

    def set_isBomb(self):
        self.isBomb = True

    def create_button(self):
        self.button = tk.Button(gamevars.root, command=self.left_click)
        self.button.place(x=self.coordinates[0], y=self.coordinates[1], width=gamevars.btnWidth, height=gamevars.btnHeight)
    
    def toggle_flag(self, event):
        if event.num in [2, 3]:
            if not self.isRevealed:
                if not self.isFlagged:
                    self.isFlagged = True
                    gamevars.bombCounter -= 1
                    self.button['image'] = self.flag_img
                else:
                    self.isFlagged = False
                    gamevars.bombCounter += 1
                    self.button['image'] = ""
                data = str(gamevars.bombCounter)
                data = "flag" + data
                gamevars.board_queue.put(data)
                self.button.place(x=self.coordinates[0], y=self.coordinates[1])

    def left_click(self):
        if not self.isFlagged:
            if not self.isRevealed : self.reveal()
            if self.isBomb:
                self.bomb_img = Image.open("bomb.png").resize((gamevars.btnWidth, gamevars.btnHeight))
                self.bomb_img = ImageTk.PhotoImage(self.bomb_img)
                self.button['image'] = self.bomb_img
                print("BOOOOOOM!")
                gamevars.gameOver = True
            else:
                print("You're safe... for now.")
                if self.noSurroundingBombs == 0 : gamevars.floodFillCell = self   
    
    def reveal(self):
        self.isFlagged = False
        self.isRevealed = True
        text = str(self.noSurroundingBombs)
        if self.isBomb: 
            self.button.configure(bg="#EDEADE")
            return
        elif text == "0":
            self.button.configure(text="", bg="#EDEADE")
            return
        elif text == "1":
            fg = "green"
        elif text == "2":
            fg = "blue"
        elif text == "3":
            fg = "red"
        else:
            fg = "black"
        self.button.configure(text=text, fg=fg, bg="#EDEADE")
        #removes the colour :(
        self.button['state'] = "disabled"
