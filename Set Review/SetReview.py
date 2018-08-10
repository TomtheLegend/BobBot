__author__ = 'tomli'

import scrython
import tkinter as tk
import json

class GUI:
    def __init__(self, master):
        #import from json
        with open('review.json', 'r') as json_data:
            d = json.load(json_data)
            self.set = d["set"]
            self.types = d["types"]

        # first rame
        self.master = master
        self.master.minsize(width=300, height=300)
        self.master.maxsize(width=300, height=300)
        self.frame1 = tk.Frame(self.master)
        self.label1 = tk.Entry(self.frame1)
        self.button1 = tk.Button(self.frame1, text='Execute Search', width=25, command=self.execute_search)
        self.newWindow = tk.Toplevel(self.master)
        self.gui_view = GUI_View(self.newWindow)
        self.label1.pack()
        self.button1.pack()
        self.frame1.pack()

        # second frame
        self.frame2 = tk.Frame(self.master)
        self.frame2_title = tk.Label(self.frame2, text='Types')

        self.listbox = tk.Listbox(self.frame2, selectmode=tk.SINGLE)
        # self.types = ["wizard", "knight", "artifact", "historic", "enchantment", "legendary"]
        for a in self.types:
            self.listbox.insert(tk.END, a)

        self.button_type = tk.Button(self.frame2, text='Get Types', width=25, command=self.get_types)

        self.button_clear = tk.Button(self.frame2, text='Clear', width=25, command=self.clear)

        self.frame2.pack()
        self.frame2_title.pack()
        self.listbox.pack()
        self.button_type.pack()
        self.button_clear.pack()


    def execute_search(self):
        self.gui_view.label1['text'] = self.label1.get()

    def get_types(self):
        type_all_array = []
        selection = self.types[self.listbox.curselection()[0]]
        all = 0
        if selection is "historic":
            command = "e:{0} is:{1}".format(self.set, selection)
        else:
            command = "e:{0} type:{1}".format(self.set, selection)
        try:
            all_type = scrython.cards.Search(q=command)
            all = all_type.total_cards()
        except Exception:
            all = 0

        for t in ["common", "uncommon", "rare", "mythic"]:
            if selection is "historic":
                command = "e:{0} is:{1} rarity:{2}".format(self.set, selection, t)
            else:
                command = "e:{0} type:{1} rarity:{2}".format(self.set, selection, t)
            try:
                all_type = scrython.cards.Search(q=command)
                type_all_array.append(all_type.total_cards())
            except Exception:
                type_all_array.append(0)


        self.gui_view.label_title["text"] = self.types[self.listbox.curselection()[0]] + " : " + str(all)
        for view, x in enumerate(type_all_array):
            self.gui_view.label_numbers[view]["text"] = x
        self.gui_view.show_all()

    def clear(self):
        self.gui_view.hide_all()


class GUI_View:
    def __init__(self, master):
        self.master = master
        self.master.minsize(width=666, height=200)
        self.master.maxsize(width=666, height=200)
        self.frame = tk.Frame(self.master)
        #self.frame.grid_columnconfigure(5, minsize=50)
        #self.frame.grid_rowconfigure(5, minsize=50)
        self.label_title = tk.Label(self.frame, text="", font=("Helvetica", 20))
        self.label_title.grid(row=0, column=0)

        self.label = []
        for i, x in enumerate(["common", "uncommon", "rare", "mythic"]):
            self.label.append(tk.Label(self.frame, text=x, font=("Helvetica", 20)))
            self.label[-1].grid(row=1, column=i, sticky="ew")

        self.label_numbers = []
        for i, x in enumerate([0, 0, 0, 0]):
            self.label_numbers.append(tk.Label(self.frame, text=x, font=("Helvetica", 20)))
            self.label_numbers[-1].grid(row=2, column=i)

        # self.quitButton = tk.Button(self.frame, text = 'Quit', width = 10, command = self.close_windows)
        #
        # self.quitButton.grid(row=5, column=6)

        col_count, row_count = self.frame.grid_size()

        for col in range(col_count):
            self.frame.grid_columnconfigure(col, minsize=0, pad=40)

        for row in range(row_count):
            self.frame.grid_rowconfigure(row, minsize=50)

        self.frame.grid()
        self.hide_all()

    def hide_all(self):
        for v in self.label:
            v.grid_remove()
        for v in self.label_numbers:
            v.grid_remove()
        self.label_title.grid_remove()

    def show_all(self):
        for v in self.label:
            v.grid()
        for v in self.label_numbers:
            v.grid()
        self.label_title.grid()

def main():
    root = tk.Tk()
    app = GUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()