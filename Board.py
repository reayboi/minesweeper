import queue
import sys
from tkinter import Image, StringVar, messagebox
from Cell import Cell
from Gamevars import Gamevars as gamevars
from threading import Thread
from time import sleep
import random
import tkinter as tk
from queue import Queue
from PIL import Image, ImageTk


class Board():
    def __init__(self):
        gamevars.btnWidth = int(gamevars.width/8)
        gamevars.btnHeight = int((gamevars.height-30)/8)
        self.board = []
        self.totalBombs = gamevars.totalFlags
        self.create_cells()
        self.assign_bombs()
        self.assign_surrounding()
        self.render_surrounding()
        gamevars.board_queue = queue.Queue()

        #UI ELEMENTS
        self.banner = tk.Frame(gamevars.root,  bg="#EDEADE")
        self.banner.place(x=0, y=0, width=gamevars.width, height=30)

        self.time_var = StringVar()
        self.timer = tk.Label(self.banner, textvariable=self.time_var, fg="black", bg="#EDEADE")
        self.timer.place(x=gamevars.width*0.43, y=gamevars.height*0.025)

        self.flag_img = Image.open("flag.png").resize((gamevars.btnWidth, gamevars.btnHeight)) 
        self.flag_img = ImageTk.PhotoImage(self.flag_img)
        self.flag_counter_img = tk.Label(self.banner, image=self.flag_img, bg="#EDEADE")
        self.flag_counter_img.place(x=gamevars.width*0.7, y=gamevars.height*0.02)
        self.flag_var = StringVar()
        self.flag_var.set(gamevars.bombCounter)
        self.flag_counter = tk.Label(self.banner, textvariable=self.flag_var, fg="black", bg="#EDEADE")
        self.flag_counter.place(x=gamevars.width*0.8, y=gamevars.height*0.025)

        self.game_over_img = Image.open("game_over.png").resize((240, 270)) 
        self.game_over_img = ImageTk.PhotoImage(self.game_over_img)
        self.game_over = tk.Label(gamevars.root, image=self.game_over_img, bg="white")

        #THREADS
        self.flood_thread = Thread(target=self.flood_fill_thread)
        self.flood_thread.start()

        self.timer_threads = Thread(target=self.timer_thread)
        self.timer_threads.start()

        gamevars.root.protocol("WM_DELETE_WINDOW", self.end_game)
        gamevars.root.after(100, self.read_queue)

    def flood_fill_thread(self):
        def flood_fill():
            while len(frontier) > 0:
                #print(len(frontier))
                cells = [cell for cell in self.board if cell.position in frontier]
                for cell in cells:
                    cell.reveal()
                    frontier.remove(cell.position)
                    checked.append(cell.position)
                    if cell.noSurroundingBombs == 0:
                        for neighbour in cell.neighbours:
                            if neighbour[0] < 0 or neighbour[0] > 7 or neighbour[1] < 0 or neighbour[1] > 7 : continue
                            else:
                                if neighbour not in checked : frontier.append(neighbour)

        current_cell = None
        while not gamevars.gameOver:
            if current_cell != gamevars.floodFillCell:
                try:
                    current_cell = gamevars.floodFillCell
                    checked = [current_cell.position]
                    frontier = [neighbour for neighbour in current_cell.neighbours]
                    flood_fill()
                except Exception:
                    print("equality")
    
    def read_queue(self):
        """ Check for updated temp data"""
        try:
            data = gamevars.board_queue.get_nowait()
            if "time" in data:
                data = data.replace("time", "")
                self.time_var.set(data)
            else:
                data = data.replace("flag", "")
                self.flag_var.set(data)
        except Exception as e:
            pass
        gamevars.root.after(100, self.read_queue)
    

    def timer_thread(self):
        gamevars.board_queue.put("time00 : 00")
        minute = 0
        second = 0
        while not gamevars.gameOver:
            sleep(1)
            second += 1
            if second == 60:
                minute += 1
                second = 0
            if minute < 10 and second < 10:
                gamevars.board_queue.put(f"time0{minute} : 0{second}")
            elif minute < 10:
                gamevars.board_queue.put(f"time0{minute} : {second}")
            elif minute >= 10 and second <10:
                gamevars.board_queue.put(f"time{minute} : 0{second}")
            else:
                gamevars.board_queue.put(f"time{minute} : {second}")
        tk.messagebox.showinfo(title="Uh Oh", message="You hit a bomb...\nYou Lost!")


    def end_game(self):
        if messagebox.askokcancel("Quit", "Quit Minesweeper?"):
            gamevars.gameOver = True
            gamevars.root.destroy()
            sys.exit(0)

    def place_flag(self):
        x = gamevars.root.winfo_pointerx()
        y = gamevars.root.winfo_pointery()
        for cell in self.board:
            min_x = cell.coordinates[0]
            max_x = min_x + gamevars.btnWidth
            min_y = cell.coordinates[1]
            max_y = min_y + gamevars.btnHeight
            if (min_x <= x <= max_x) and (min_y <= y <= max_y):
                cell.toggle_flag()
    
    def assign_surrounding(self):
        for cell in self.board:
            x, y = cell.position[0], cell.position[1]
            if not cell.isBomb:
                if x == 0 and y == 0:
                    #ORDER: CENTRE-DOWN, RIGHT-DOWN, RIGHT-CENTRE (top-left)
                    neighbours = [[x, y+1], [x+1, y+1], [x+1, y]]
                elif x == 7 and y == 0:
                    #ORDER: LEFT-CENTRE, LEFT-DOWN, CENTRE-DOWN (top-right)
                    neighbours = [[x-1, y], [x-1, y+1], [x, y+1]]
                elif x == 0 and y == 7:
                    #ORDER: CENTRE-ABOVE, RIGHT-ABOVE, RIGHT-CENTRE (bottom-left)
                    neighbours = [[x, y-1], [x+1, y-1], [x+1, y]]
                elif x == 7 and y == 0:
                    #ORDER: LEFT-CENTRE, LEFT-ABOVE, CENTRE-ABOVE (bottom-right)
                    neighbours = [[x-1, y], [x-1, y-1], [x, y-1]]
                elif x == 0:
                    #ORDER: CENTRE-ABOVE, RIGHT-ABOVE, RIGHT-CENTRE, RIGHT-DOWN, CENTRE-DOWN (left)
                    neighbours = [[x, y-1], [x+1, y-1], [x+1, y], [x+1, y+1], [x, y+1]]
                elif x == 7:
                    #ORDER: CENTRE-ABOVE, LEFT-ABOVE, LEFT-CENTRE, LEFT-DOWN, CENTRE-DOWN (right)
                    neighbours = [[x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1], [x, y+1]]
                elif y == 0:
                    #ORDER: LEFT-CENTRE, LEFT-DOWN, CENTRE-DOWN, RIGHT-DOWN, RIGHT-CENTRE (top)
                    neighbours = [[x-1, y], [x-1, y+1], [x, y+1], [x+1, y+1], [x+1, y]]
                elif y == 7:
                    #ORDER: LEFT-CENTRE, LEFT-ABOVE, CENTRE-ABOVE, RIGHT-ABOVE, RIGHT-CENTRE (bottom)
                    neighbours = [[x-1, y], [x-1, y-1], [x, y-1], [x+1, y-1], [x+1, y]]
                else:
                    #ORDER: CENTRE-ABOVE, LEFT-ABOVE, LEFT-CENTRE, LEFT-DOWN, CENTRE-DOWN, RIGHT-DOWN, RIGHT-CENTRE, RIGHT-ABOVE (normal)
                    neighbours = [[x, y-1], [x-1, y-1], [x-1, y], [x-1, y+1], [x, y+1], [x+1, y+1], [x+1, y], [x+1, y-1]]
                cell.neighbours = neighbours
        for cell in self.board:
            if not cell.isBomb:
                for coords in cell.neighbours:                     
                    for cell2 in self.board:
                        if cell2.isBomb and (coords == cell2.position): cell.noSurroundingBombs += 1
            
    def render_surrounding(self):
        for cell in self.board:
            cell.button["bg"] = "#a1adb0"

    def assign_bombs(self):
        bombNums = []
        for x in range(self.totalBombs):
            num = random.randrange(0, 64)
            while num in bombNums:
                num = random.randrange(0, 64)
            bombNums.append(num)
        for x in bombNums:
            self.board[x].set_isBomb()

    def create_cells(self):
        x, y, coords, positions = 0, 30, [], []
        for row in range(8):
            if row != 0: y += gamevars.width/8
            for column in range(8):
                if column != 0:
                    x += ((gamevars.height-30)/8)
                positions.append([column, row])
                coords.append([x, y])
                if column == 7:
                    x = 0
        for index in range(len(coords)):
            cell = Cell(coords[index], positions[index])
            self.board.append(cell)
        gamevars.root.update()
