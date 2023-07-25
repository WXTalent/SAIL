# -*- coding: utf-8 -*-
"""
Created on Sun Jul  2 14:04:24 2023

@author: WXH
"""
import sys
import os          
import json                        
import subprocess                                                                                                                
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SAIL')
        self.path_init()
        self.ui_init()
    
    def ui_init(self):
        self.ui = uic.loadUi('./Window.ui')
        self.ui.setWindowIcon(QIcon("./logo.ico"))
        self.ui.setWindowTitle('SAIL')
        self.FolderList = self.ui.FolderList
        self.FileTable  = self.ui.FileTable
        self.AllLabel = self.ui.LabelList
        self.FileLabel = self.ui.listWidget
        self.AddLabel = self.ui.pushButton
        self.set_folder()
        self.FolderList.clicked.connect(self.set_file) 
        self.FolderList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.FolderList.customContextMenuRequested.connect(self.FolderList_right_action)
        self.FileTable.clicked.connect(self.set_label)
        self.FileTable.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁用编辑触发器
        self.FileTable.cellDoubleClicked.connect(self.open_file) # 双击打开文件
        header = self.FileTable.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) # 根据内容自适应宽度
        self.FileTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.FileTable.customContextMenuRequested.connect(self.FileTable_right_action)
        self.AddLabel.clicked.connect(self.add_label)
        self.AllLabel.setSelectionMode(QListWidget.MultiSelection)
        self.AllLabel.clicked.connect(self.label_sort)
        self.AllLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.AllLabel.customContextMenuRequested.connect(self.AllLabel_right_action)
        self.FileLabel.setContextMenuPolicy(Qt.CustomContextMenu)
        self.FileLabel.customContextMenuRequested.connect(self.FileLabel_right_action)
        self.ui.actionFolder.triggered.connect(self.select_folder)
        
         
    def path_init(self):
        ''''''
        with open('./config.txt') as f:
            config = f.readlines()
        self.path = config[0].split('@')[1].strip()
        self.color = eval(config[1].split('@')[1].strip())
        if len(self.path) < 3:
            self.path = QFileDialog.getExistingDirectory(self, '选择文件库')
            config = 'path @ ' + self.path + '\n' + 'color @ ' + str(self.color) + '\n'
            with open('./config.txt', 'w') as f:
                f.write(config)
        self.read_label()
    
    def read_label(self):
        if '#Data' not in os.listdir(self.path):
            # 新建文件
            os.mkdir(self.path+'/'+'#Data')
        if "Label.json" not in os.listdir(self.path + '/' + '#Data'): 
            self.label = {}
            with open(self.path+'/#Data/Label.json', 'w') as f:
                json.dump(self.label, f)
        else:
            # 从Label.json中读取信息
            with open(self.path+'/#Data/Label.json') as f:
                self.label = json.load(f)
            
    def select_folder(self):
        # 选择文献库
        self.path = QFileDialog.getExistingDirectory(self, '选择文件库')
        config = 'path @ ' + self.path + '\n' + 'color @ ' + str(self.color) + '\n'
        with open('./config.txt', 'w') as f:
            f.write(config)
        self.read_label()
        self.set_folder()
    
    def set_folder(self):
        '''设置文件夹列表'''
        self.FolderList.clear()
        for folder in os.listdir(self.path):
            if os.path.isdir(self.path + '/' + folder) and folder != '#Data': # 如果是文件夹，则添加到列表中
                item = QListWidgetItem(folder, self.FolderList)
                item.setIcon(QIcon("./folder.ico"))
                if folder not in self.label.keys(): # 在label中添加文件夹对应的key
                    self.label[folder] = {'label':[], 'color':{}}
        self.save_label()
        
    def save_label(self):
        '''将label的内容保存到Label.json中'''
        with open(self.path+'/#Data/Label.json', 'w') as f:
            json.dump(self.label, f)
            
    def set_file(self):
        '''设置文件列表，更新标签栏的内容'''
        self.FileTable.clearContents()
        item = self.FolderList.currentItem()
        self.folder = item.text()
        files = os.listdir(self.path + '/' + self.folder) # 读取文件夹中的所有文件
        self.FileTable.setRowCount(len(files))
        for i in range(len(files)):
            file_item = QTableWidgetItem(files[i])
            self.FileTable.setItem(i, 1, file_item)
            # 如果self.label中没有某文件的信息，则创建一个
            if files[i] not in self.label[item.text()].keys():
                self.label[self.folder][files[i]] = []
        self.save_label()
        self.show_label()
        self.set_file_label()
        
    def set_file_label(self):
        '''在FileTabel中的第一列加上标签，通过颜色的方式显示不同的标签'''
        for row in range(self.FileTable.rowCount()):
            item = self.FileTable.item(row, 1)
            if item is not None:
                labels = self.label[self.folder][item.text()]
                string = ""
                for label in labels:
                    index = self.label[self.folder]['label'].index(label)
                    if label in self.label[self.folder]['color'].keys():
                        color = self.label[self.folder]['color'][label]
                        string = string + f"<font color={color}>\u25A9"
                        text = QLabel()
                        text.setFont(QFont('Arial', 14))
                        text.setText(string)
                        text.setAlignment(Qt.AlignRight)
                        text.setAlignment(Qt.AlignCenter)
                        self.FileTable.setCellWidget(row, 0, text)
        
    def show_label(self):
        '''将self.label中的信息显示在左下角的标签栏'''
        self.AllLabel.clear()
        labels = self.label[self.folder]['label']
        self.AllLabel.addItems(labels)
        for i in range(len(labels)):
            if labels[i] in self.label[self.folder]['color'].keys():
                color = self.label[self.folder]['color'][labels[i]]
                self.AllLabel.item(i).setForeground(QColor(color))
        color_del = []
        for color in self.label[self.folder]['color'].keys():
            '''如果某一个label被删除，对应的颜色也删除'''
            if color not in labels:
                color_del.append(color)
        for color in color_del:
            del self.label[self.folder]['color'][color]
        
    def set_label(self):
        '''点击文件列表，则显示对应的标签'''
        self.FileLabel.clear()
        if self.FileTable.currentIndex().column() == 1:
            labels = self.label[self.folder][self.FileTable.currentItem().text()]
            if len(labels) == 0:
                self.FileLabel.addItems(['No Label'])
            else:  
                self.FileLabel.addItems(labels)
                
    def open_file(self):
        '''双击打开文件'''
        if self.FileTable.currentIndex().column() == 1:
            item = self.FileTable.currentItem()
            file_path = self.path + '/' + self.folder + '/' + item.text()
            if sys.platform.startswith('darwin'):
                subprocess.run(['open', file_path])  # macOS
            elif sys.platform.startswith('linux'):
                subprocess.run(['xdg-open', file_path])  # Linux
            elif sys.platform.startswith('win'):
                subprocess.run(['start', '', file_path], shell=True)  # Windows
                
    def add_label(self):
        '''给文件添加标签'''
        if self.FileTable.currentIndex().column() == 1:
            item = self.FileTable.currentItem()
            label = self.ui.lineEdit.text()
            self.label[self.folder][item.text()].append(label)
            if label not in self.label[self.folder]['label']:
                self.label[self.folder]['label'].append(label)
            self.ui.lineEdit.clear()
            self.set_label()
            self.show_label()
            self.save_label()
            self.set_file_label()  
        else:
            print('no select')
    
    def label_sort(self):
        '''根据标签筛选文件'''
        item = self.AllLabel.selectedItems()
        selected_labels = []
        for i in item:  
            selected_labels.append(i.text())
        self.FileTable.clearContents()
        file_list = []
        for file in os.listdir(self.path+'./'+self.folder):
            if set(selected_labels).issubset(set(self.label[self.folder][file])):
                file_list.append(file)
        for i in range(len(file_list)):
            file_item = QTableWidgetItem(file_list[i])
            self.FileTable.setItem(i, 1, file_item)
        self.set_file_label()
    
    def AllLabel_right_action(self, pos):
        '''修改标签'''
        item = self.AllLabel.itemAt(pos)
        if item:
            menu = QMenu(self)
            edit_label = QAction('修改标签', self)
            edit_label.triggered.connect(lambda:self.editLabelText(item))
            edit_color = QAction('修改颜色', self)
            edit_color.triggered.connect(lambda:self.editLabelColor(item))
            edit_rank = QAction('修改序号', self)
            edit_rank.triggered.connect(lambda:self.editLabelRank(item))
            remove_label = QAction('删除标签', self)
            remove_label.triggered.connect(lambda:self.removeLabel(item))
            menu.addAction(edit_label)
            menu.addAction(edit_color)
            menu.addAction(edit_rank)
            menu.addAction(remove_label)
            menu.exec_(self.AllLabel.mapToGlobal(pos))
            
    def editLabelText(self, item):
        '''修改标签文字'''
        text, ok = QInputDialog.getText(self, "修改标签", "请输入新的标签", text=item.text())
        if ok and text:
            for key in self.label[self.folder].keys():
                if item.text() in self.label[self.folder][key]:
                    index = self.label[self.folder][key].index(item.text())
                    self.label[self.folder][key][index] = text
        self.save_label()
        self.show_label()
    
    def editLabelColor(self, item):
        '''修改标签颜色'''
        text, ok = QInputDialog.getText(self, "修改颜色", "请输入颜色序号0~9或16进制编号", text='')
        if len(text) == 1:
            color = self.color[int(text)]
        else:
            color = text
        self.label[self.folder]['color'][item.text()] = color
        self.save_label()
        self.show_label()
        self.set_file_label()
    
    def editLabelRank(self, item):
        '''修改标签序号'''
        current_index = self.label[self.folder]['label'].index(item.text())
        text, ok = QInputDialog.getText(self, "修改序号", "请输入新的序号", text=str(current_index))
        if ok and text:
            label = self.label[self.folder]['label'][int(text)]
            self.label[self.folder]['label'][int(text)] = item.text()
            self.label[self.folder]['label'][current_index] = label
        self.save_label()
        self.show_label()
    
    def removeLabel(self, item):
        confirmation = QMessageBox.question(self.AddLabel, "确认删除", "确认删除标签吗？", QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            for file in self.label[self.folder].keys():
                if file != 'color' and item.text() in self.label[self.folder][file]:
                    self.label[self.folder][file].remove(item.text())
        self.save_label()
        self.show_label()
        self.set_file_label()
            
    def FileLabel_right_action(self, pos):
        '''删除标签'''
        if self.FileLabel.itemAt(pos):
            menu = QMenu(self)
            remove = QAction('删除标签', self)
            remove.triggered.connect(self.FileLabel_del_label)
            menu.addAction(remove)
            menu.exec_(self.FileLabel.mapToGlobal(pos))
    
    def FileLabel_del_label(self):
        '''删除标签'''
        item = self.FileLabel.currentItem()
        file = self.FileTable.currentItem()
        self.label[self.folder][file.text()].remove(item.text())
        
        self.save_label()
        self.set_label()
    
    def FileTable_right_action(self, pos):
        '''修改标签'''
        item = self.FileTable.itemAt(pos)
        if item:
            menu = QMenu(self)
            rename = QAction('重命名文件', self)
            rename.triggered.connect(lambda:self.renameFile(item))
            move = QAction('移动文件', self)
            move.triggered.connect(lambda:self.moveFile(item))
            menu.addAction(rename)
            menu.addAction(move)
            menu.exec_(self.FileTable.mapToGlobal(pos))
    
    def renameFile(self, item):
        text, ok = QInputDialog.getText(self, "重命名文件", "请输入新的文件名", text=item.text())
        if ok and text:
            labels = self.label[self.folder].pop(item.text())
            self.label[self.folder][text] = labels
            old_name = item.text()
            new_name = text
            os.rename(self.path+'/'+self.folder+'/'+old_name, self.path+'/'+self.folder+'/'+new_name)
        self.save_label()
        self.show_label()
        self.set_file()
    
    def moveFile(self, item):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if len(folder_path):
            folder = folder_path.split('/')[-1]
            old_path = self.path + '/' + self.folder + '/' + item.text()
            new_path = folder_path + '/' + item.text()
            os.rename(old_path, new_path)
            labels = self.label[self.folder].pop(item.text())
            self.label[folder][item.text()] = labels
            for label in labels:
                if label not in self.label[folder]['label']:
                    self.label[folder]['label'].append(label)
                    if label in self.label[self.folder]['color'].keys():
                        self.label[folder]['color'][label] = self.label[self.folder]['color'][label]
        self.save_label()
        self.show_label()
        self.set_file()
           
        
    def FolderList_right_action(self, pos):
        '''修改标签'''
        item = self.FolderList.itemAt(pos)
        if item:
            menu = QMenu(self)
            rename = QAction('重命名文件夹', self)
            rename.triggered.connect(lambda:self.renameFolder(item))
            menu.addAction(rename)
            menu.exec_(self.FolderList.mapToGlobal(pos))
     
    def renameFolder(self, item):
        text, ok = QInputDialog.getText(self, "重命名文夹", "请输入新的名称", text=item.text())
        if ok and text:
            folder = self.label.pop(item.text())
            self.label[text] = folder
            old_name = item.text()
            new_name = text
            os.rename(self.path+'/'+old_name, self.path+'/'+new_name)
        self.save_label()
        self.set_folder()
            
if __name__ == '__main__':
    app = QApplication(sys.argv)  
    w = MyWindow()
    w.ui.show()
    app.exec_()
