import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self, root):
        self.root = root
        self.global_info = tk.Label(self.root, text="Carregando informações...")
        self.global_info.pack(pady=20)

    def create_dashboard(self):
        self.root.title("Dashboard de recursos do sistema")
        self.root.state("zoomed")

        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("Usuário", "Número de threads", "Uso de Memória")

        # Configuração das colunas
        self.tree.column("#0", width=200, anchor=tk.W)
        self.tree.heading("#0", text="Nome / PID", anchor=tk.W)

        self.tree.column("Usuário", width=200, anchor=tk.W)
        self.tree.heading("Usuário", text="Usuário")

        self.tree.column("Número de threads", width=200, anchor=tk.W)
        self.tree.heading("Número de threads", text="Número de threads")

        self.tree.column("Uso de Memória", width=200, anchor=tk.W)
        self.tree.heading("Uso de Memória", text="Uso de Memória")

        self.tree.pack(expand=True, fill=tk.BOTH)

    def display(self, processes, global_data):
        # Exibir informações globais
        if global_data:
            self.global_info.config(
                text=(
                    f"CPU - Uso total: {global_data['cpu_usage']}% | Ocioso: {global_data['idle']}% | "
                    f"Kernel: {global_data['kernel']}% | Usuário: {global_data['user']}% | "
                    f"Número de processadores: {global_data['n_processors']} | "
                    f"Tamanho da página de memória: {global_data['page_size']} \n\n"
                    f"Memória: {global_data['memory_used']}GB/{global_data['memory_total']}GB "
                    f"({global_data['memory_percent']}%) | "
                    f"Disco: {global_data['disk_used']}GB/{global_data['disk_total']}GB "
                    f"({global_data['disk_percent']}%)"
                )
            )

        # Atualizar processos
        for item in self.tree.get_children():
            self.tree.delete(item)

        grouped = group_processes(processes)

        for name, processes in grouped.items():
            user = processes[0]['user']
            memory_usage = sum(p['current_memory'] for p in processes)
            n_threads = sum(len(p['threads']) for p in processes)

            parent = self.tree.insert(
                "", "end", text=f"{name} ({len(processes)})",
                values=(user, f"{n_threads}", f"{memory_usage:.2f} MB")
            )

            for process in processes:
                self.tree.insert(
                    parent,
                    "end",
                    text=f"PID: {process['pid']}",
                    values=(
                        f"{user}",
                        f"{len(process['threads'])}",
                        f"{process['current_memory']}",
                    ),
                )

# Função para agrupar processos
def group_processes(processes):
    grouped = {}
    for pid, info in processes.items():
        name = info['name']
        if name not in grouped:
            grouped[name] = []
        grouped[name].append({'pid': pid, **info})
    # Retorna os grupos ordenados alfabeticamente pelo nome do processo
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))
