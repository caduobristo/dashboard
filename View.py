import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self, root):
        self.root = root
        root.title("Dashboard de recursos do sistema")
        root.state("zoomed")

        self.global_info = tk.Label(root, text="Carregando informações globais...")
        self.global_info.pack(pady=10)

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

    def display(self, processes, global_data):
        # Exibir informações globais
        if global_data:
            cpu_usage = global_data.get("cpu_usage", "N/A")
            memory = global_data.get("memory", {})
            disk = global_data.get("disk", {})

            self.global_info.config(
                text=(
                    f"CPU: {cpu_usage}% | "
                    f"Memória: {memory.get('used', 'N/A')}GB/{memory.get('total', 'N/A')}GB "
                    f"({memory.get('percent', 'N/A')}%) | "
                    f"Disco: {disk.get('used', 'N/A')}GB/{disk.get('total', 'N/A')}GB "
                    f"({disk.get('percent', 'N/A')}%)"
                )
            )

        # Atualizar processos
        for item in self.tree.get_children():
            self.tree.delete(item)

        grouped = group_processes(processes)

        for name, processes in grouped.items():
            total_memory = sum(p['current_memory'] for p in processes)
            total_threads = sum(len(p['threads']) for p in processes)
            user = processes[0]['user']

            parent = self.tree.insert(
                "", "end", text=f"{name} ({len(processes)})",
                values=(f"{total_memory:.2f} MB", total_threads, user)
            )

            for process in processes:
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

# Função para agrupar processos
def group_processes(processes):
    """
    Agrupa os processos pelo nome do executável.
    Retorna um dicionário com o nome como chave e a lista de processos como valor.
    """
    grouped = {}
    for pid, info in processes.items():
        name = info['name']
        if name not in grouped:
            grouped[name] = []
        grouped[name].append({'pid': pid, **info})
    # Retorna os grupos ordenados alfabeticamente pelo nome do processo
    return dict(sorted(grouped.items(), key=lambda x: x[0].lower()))
