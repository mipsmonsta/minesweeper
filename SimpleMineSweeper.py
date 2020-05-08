# -*- coding: utf-8 -*-
"""
Author: Yaojin Tham
Date Created: 7 May 2020

Minesweeper Game
"""

import wx
import random


class MineSweeper(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='Mine Sweeper', size=(300, 300))
        
        #add a panel so looks okay in different version of 
        #windows
        
        self.panel = None
        
        self.vbox = None
        
        self.btnDict = dict()
        
        self.grid = None
        
        self.mineSize = (10, 10)
        
        self.numbersOfMine = 20
        
        self.isGameOver = False
        
        self.statusBar = self.CreateStatusBar()
        
        self.initGameUI()
        
        self.Bind(wx.EVT_CLOSE, self.closeWindow)
        
        
    def initGameUI(self):
        
        self.mineField = MineState(size = self.mineSize, numsOfMines = self.numbersOfMine)
     
        self.minesCoord = self.mineField.getMinesCoord()
        
        self.grid = wx.GridSizer(10,10,1,1)
       
        self.panel = wx.Panel(self, wx.ID_ANY)
            
        self.vbox = wx.BoxSizer(wx.VERTICAL)
            
        self.btnDict.clear()
        for i in range(self.mineSize[0]):
            for j in range(self.mineSize[1]):
                btnLabel = ""
                #if  self.mineField.board[i][j] == 'M':
                #    btnLabel = "*"
                button = wx.Button(self.panel, wx.ID_ANY, label=btnLabel)
                self.btnDict[button.Id] = (i,j)
                button.Bind(wx.EVT_BUTTON, self.mineFieldBtnClick)
                button.Bind(wx.EVT_RIGHT_DOWN, self.mineFieldBtnRightClick)
                self.grid.Add(button, 0, wx.EXPAND)
       
        self.vbox.Add(self.grid, proportion=1, flag=wx.EXPAND)
        self.restartBtn = wx.Button(self.panel, wx.ID_ANY, "Restart")
        self.restartBtn.Bind(wx.EVT_BUTTON, self.restartGameStateBtnClick)
        self.vbox.Add(self.restartBtn, flag=wx.LEFT)
        self.panel.SetSizer(self.vbox)
        
    def restartGameStateBtnClick(self, event):
        self.statusBar.SetStatusText("")
        self.isGameOver = False
        self.mineField = MineState(size = self.mineSize, numsOfMines = self.numbersOfMine)
        self.minesCoord = self.mineField.getMinesCoord()
        for Id, coord in self.btnDict.items():
            btn =  self.FindWindowById(Id)
            btn.SetLabel("")
        
    def mineFieldBtnClick(self, event):
        if self.isGameOver == True:
            return
        coord = self.btnDict.get(event.Id)
        board = self.mineField.board
        btnLabel = self.FindWindowById(event.Id).GetLabel()
        if board[coord[0]][coord[1]] == 'X' or board[coord[0]][coord[1]].isnumeric() \
            or btnLabel == 'o':
            return
        
        self.mineField.updateBoard(coord)
        
        self.redrawBtnLabelFromMineState(board)
        
    def mineFieldBtnRightClick(self, event):
        if self.isGameOver == True:
            return
        coord = self.btnDict.get(event.Id)
        btn = self.FindWindowById(event.Id)
        label = btn.GetLabel()
        if label == "":
            btn.SetLabel('o')
            x, y = self.btnDict[event.Id]
            if self.mineField.board[x][y] == 'M' and (x,y) in self.minesCoord:
                print(f"mine marked at {(x, y)}")
                self.minesCoord.remove((x,y))
            self.checkHasWon()
                
        elif label == "o":
            btn.SetLabel("")
            x, y = self.btnDict[event.Id]
            if self.mineField.board[x][y] == 'M' and (x,y) not in self.minesCoord:
                self.minesCoord.append((x,y))
                print(f"mine marked then unmarked at {(x, y)}")
        print(coord)
        
        
    def checkHasWon(self):
        if len(self.minesCoord) == 0:
            self.isGameOver = True
            self.statusBar.SetStatusBarText("All Mines Found")
    
    def redrawBtnLabelFromMineState(self, board):

        for Id, coord in self.btnDict.items():
            btn =  self.FindWindowById(Id)
            x, y = coord
            if board[x][y].isnumeric():
                btn.SetLabel(board[x][y])
            elif board[x][y] == "B":
                btn.SetLabel("-")
            elif board[x][y] == "X":
                #detect game over
                self.isGameOver = True 
                self.statusBar.SetStatusText("Game Over")
                btn.SetLabel("X")
    
    def closeWindow(self, event):
        dlg = wx.MessageDialog(self, "Okay to exit?", "Exit", wx.YES_NO |wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Destroy()  # frame
        dlg.Destroy()
        
class MineState():
    
    def __init__(self, size = (10, 10), numsOfMines=20):
        n, m = size
        self.board = ['E'*m for _ in range(n)]
        
        for _ in range(numsOfMines):
            i = random.randint(0, 9)
            j = random.randint(0, 9)
            while self.board[i][j] == 'M':
                i = random.randint(0, 9)
                j = random.randint(0, 9)
            self.board[i] = self.board[i][:j] + 'M' + self.board[i][j+1:]
            
    def getMinesCoord(self):
        minesCoord = []
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j] == "M":
                    minesCoord.append((i,j))
        return minesCoord
            
    def updateBoard(self, click):
        x, y = click
        if self.board[x][y] == "M":
            self.board[x] = self.board[x][:y] + "X" + self.board[x][y+1:]
        else:
            self.revealE(self.board, x, y)
        
    
        
    def revealE(self, board, x, y):
        neighbours = [(x-1, y), (x+1, y), (x, y-1), (x, y + 1), 
                      (x-1, y+1), (x+1, y+1), (x-1, y-1), (x+1, y-1)]
        
        emptyNeighbors = []
        minedNeighbors = []
        
        for neighbor in neighbours:
            xn, yn = neighbor
            if xn < 0 or xn >= len(board) or yn < 0 or yn >= len(board[0]):
                continue
            if board[xn][yn] == "M":
                minedNeighbors.append((xn, yn))
            if board[xn][yn] == "E":
                emptyNeighbors.append((xn, yn))
        
        if len(minedNeighbors) > 0: #terminating condition
            print(minedNeighbors)
            board[x] = board[x][:y] + f"{len(minedNeighbors)}" + board[x][y+1:]
            return
        
        #at this point, all adjacent neighbours are empty
        board[x] = board[x][:y] + "B" + board[x][y+1:]
        for xe, xy in emptyNeighbors:
            self.revealE(board, xe, xy)
                
        
#Run the program
if __name__== '__main__':
    app = wx.App()
    frame = MineSweeper().Show()
    app.MainLoop()