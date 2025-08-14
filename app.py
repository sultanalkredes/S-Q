import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

conn = sqlite3.connect('mushahadat.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS observations (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    no3_mushahada TEXT,
    tarikh_mushahada TEXT,
    masdar TEXT,
    masafa REAL,
    ihdathi TEXT,
    tarikh_edkhal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()

def save_data():
    data = {
        'entity_id': entry_entity_id.get(),
        'no3_mushahada': entry_no3.get(),
        'tarikh_mushahada': entry_date.get(),
        'masdar': entry_source.get(),
        'masafa': entry_distance.get(),
        'ihdathi': entry_coords.get()
    }
    if not data['entity_id']:
        messagebox.showwarning("تنبيه","الرجاء إدخال معرف العنصر")
        return
    cursor.execute('''
        INSERT INTO observations (entity_id, no3_mushahada, tarikh_mushahada, masdar, masafa, ihdathi)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', tuple(data.values()))
    conn.commit()
    messagebox.showinfo("تم","تم حفظ البيانات")
    clear_fields()
    load_latest_records()

def clear_fields():
    for e in [entry_entity_id, entry_no3, entry_date, entry_source, entry_distance, entry_coords]:
        e.delete(0, tk.END)

def show_history(entity_id):
    win = tk.Toplevel(root)
    win.title(f"سجل {entity_id}")
    win.geometry("700x300")
    tree = ttk.Treeview(win, columns=("id","no3","date","src","dist","coord","entry"), show='headings')
    tree.pack(expand=True,fill='both')
    for c in tree["columns"]:
        tree.heading(c,text=c)
    cursor.execute('''
        SELECT record_id,no3_mushahada,tarikh_mushahada,masdar,masafa,ihdathi,tarikh_edkhal
        FROM observations WHERE entity_id=? ORDER BY tarikh_edkhal ASC
    ''',(entity_id,))
    for r in cursor.fetchall():
        tree.insert('',tk.END,values=r)

def load_latest_records():
    for i in tree_data.get_children():
        tree_data.delete(i)
    cursor.execute('''
        SELECT * FROM observations WHERE tarikh_edkhal IN (
            SELECT MAX(tarikh_edkhal) FROM observations GROUP BY entity_id
        ) ORDER BY tarikh_edkhal DESC
    ''')
    for r in cursor.fetchall():
        tree_data.insert('',tk.END,values=r)

root = tk.Tk()
root.title("MushahadatApp")
root.geometry("900x500")
notebook=ttk.Notebook(root)
notebook.pack(expand=True,fill='both')

f1=ttk.Frame(notebook); notebook.add(f1,text="📥 جمع البيانات")
labels=["Entity ID:","نوع المشاهدة:","تاريخ المشاهدة:","المصدر:","المسافة:","الإحداثي:"]
entries=[]
for idx,lab in enumerate(labels):
    tk.Label(f1,text=lab).grid(row=idx,column=0,sticky='w')
    e=tk.Entry(f1,width=40); e.grid(row=idx,column=1); entries.append(e)
entry_entity_id,entry_no3,entry_date,entry_source,entry_distance,entry_coords = entries
tk.Button(f1,text="💾 حفظ",command=save_data).grid(row=6,column=1,pady=10)

f2=ttk.Frame(notebook); notebook.add(f2,text="📂 بنك المعلومات")
cols=("record_id","entity_id","no3","date","source","distance","coords","entry_date")
tree_data=ttk.Treeview(f2,columns=cols,show='headings')
tree_data.pack(expand=True,fill='both')
for c in cols: tree_data.heading(c,text=c)
tree_data.bind("<Double-1>",lambda e: show_history(tree_data.item(tree_data.selection()[0])["values"][1]))
load_latest_records()
root.mainloop()
