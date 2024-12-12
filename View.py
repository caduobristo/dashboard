import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self, root):
        self.root = root
        root.title("Dashboard de recursos do sistema")
        root.state("zoomed")

    def create_dashboard(self):
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("Uso de memória", "Número de threads", "Usuário")

        # Configuração das colunas
        self.tree.column("#0", width=200, anchor=tk.W)
        self.tree.heading("#0", text="Nome / PID", anchor=tk.W)

        self.tree.column("Uso de memória", width=200, anchor=tk.W)
        self.tree.heading("Uso de memória", text="Uso de memória")

        self.tree.column("Número de threads", width=200, anchor=tk.W)
        self.tree.heading("Número de threads", text="Número de threads")

        self.tree.column("Usuário", width=200, anchor=tk.W)
        self.tree.heading("Usuário", text="Usuário")

        self.tree.pack(expand=True, fill=tk.BOTH)

    def display(self, processes):
        # Remove todos os itens atuais
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Agrupa processos por nome
        grouped = group_processes(processes)

        for name, processes in grouped.items():
            # Adicionar o programa como um nó pai
            total_memory = sum(p['current_memory'] for p in processes)
            total_threads = sum(len(p['threads']) for p in processes)
            user = processes[0]['user']

            parent = self.tree.insert("", "end", text=f"{name} ({len(processes)})", values=(f"{total_memory:.2f} MB", total_threads, user))

            for process in processes:
                # Adicionar cada processo como filho
                self.tree.insert(
                    parent,
                    "end",
                    text=f"PID: {process['pid']}",
                    values=(
                        f"{process['current_memory']:.2f} MB",
                        f"{len(process['threads'])}",
                        f"{process['user']}",
                    ),
                )

def group_processes(processes):
    grouped = {}
    for pid, info in processes.items():
        name = info['name']
        if name not in grouped:
            grouped[name] = []
        grouped[name].append({'pid': pid, **info})
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))

