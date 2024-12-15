import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de recursos do sistema")
        self.root.state("zoomed")

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.menu.add_command(label="Tela principal", command=self.show_main_screen)
        self.menu.add_command(label="Dados detalhados", command=self.show_details_screen)
        self.menu.add_command(label="Dados de memória", command=self.show_memory_screen)

        self.main_frame = tk.Frame(self.root)
        self.details_frame = tk.Frame(self.root)
        self.memory_frame = tk.Frame(self.root)

        self.create_main_screen()
        self.create_details_screen()
        self.create_memory_screen()

        self.show_main_screen()

    def create_main_screen(self):
        self.global_info = tk.Label(self.main_frame, text="Carregando informações...")
        self.global_info.pack(pady=20)

        tree_frame = tk.Frame(self.main_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.global_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scroll.set
        )
        self.global_tree["columns"] = ("Usuário", "Número de threads", "Uso de Memória")

        # Configuração das colunas
        self.global_tree.column("#0", width=200, anchor=tk.W)
        self.global_tree.heading("#0", text="Nome / PID", anchor=tk.W)

        self.global_tree.column("Usuário", width=200, anchor=tk.W)
        self.global_tree.heading("Usuário", text="Usuário")

        self.global_tree.column("Número de threads", width=200, anchor=tk.W)
        self.global_tree.heading("Número de threads", text="Número de threads")

        self.global_tree.column("Uso de Memória", width=200, anchor=tk.W)
        self.global_tree.heading("Uso de Memória", text="Uso de Memória")

        self.global_tree.pack(expand=True, fill=tk.BOTH)

        scroll.config(command=self.global_tree.yview)

    def create_details_screen(self):
        self.details_info = tk.Label(self.details_frame, text="Informações detalhadas de cada processo")
        self.details_info.pack(pady=20)

        tree_frame = tk.Frame(self.details_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.details_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scroll.set,
        )
        self.details_tree["columns"] = (
            "PID", "Prioridade", "Usuário", "Uso da CPU", 
            "Tempo de kernel", "Tempo de usuário", "Thread ID",
            "Prioridade base", "Prioridade Alterada")

        self.details_tree.column("#0", width=200, anchor=tk.W)
        self.details_tree.heading("#0", text="Processo", anchor=tk.W)

        for col in self.details_tree["columns"]:
            self.details_tree.column(col, width=150, anchor=tk.W)
            self.details_tree.heading(col, text=col, anchor=tk.W)

        self.details_tree.pack(expand=True, fill=tk.BOTH)
        scroll.config(command=self.details_tree.yview)

    def create_memory_screen(self):
        self.memory_info = tk.Label(self.memory_frame, text="Informações detalhadas do uso de memória")
        self.memory_info.pack(pady=20)

        tree_frame = tk.Frame(self.memory_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.memory_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scroll.set,
        )
        self.memory_tree["columns"] = ("PID", "Uso de memória", "Pico de memória")

        self.memory_tree.column("#0", anchor=tk.W)
        self.memory_tree.heading("#0", text="Processo", anchor=tk.W)

        self.memory_tree.column("PID", anchor=tk.W)
        self.memory_tree.heading("PID", text="PID", anchor=tk.W)

        self.memory_tree.column("Uso de memória", anchor=tk.W)
        self.memory_tree.heading("Uso de memória", text="Uso de memória", anchor=tk.W)

        self.memory_tree.column("Pico de memória", anchor=tk.W)
        self.memory_tree.heading("Pico de memória", text="Pico de memória", anchor=tk.W)

        self.memory_tree.pack(expand=True, fill=tk.BOTH)
        scroll.config(command=self.memory_tree.yview)

    def show_main_screen(self):
        self.details_frame.pack_forget()
        self.memory_frame.pack_forget()
        self.main_frame.pack(expand=True, fill=tk.BOTH)

    def show_details_screen(self):
        self.main_frame.pack_forget()
        self.memory_frame.pack_forget()
        self.details_frame.pack(expand=True, fill=tk.BOTH)

    def show_memory_screen(self):
        self.main_frame.pack_forget()
        self.details_frame.pack_forget()
        self.memory_frame.pack(expand=True, fill=tk.BOTH)
    
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
        for item in self.global_tree.get_children():
            self.global_tree.delete(item)

        for item in self.details_tree.get_children():
                self.details_tree.delete(item)

        for item in self.memory_tree.get_children():
                self.memory_tree.delete(item)

        grouped = group_processes(processes)

        for name, processes in grouped.items():
            user = processes[0]['user']
            memory_usage = sum(p['current_memory'] for p in processes)
            n_threads = sum(len(p['threads']) for p in processes)

            parent_global = self.global_tree.insert(
                "", "end", text=f"{name} ({len(processes)})",
                values=(user, f"{n_threads}", f"{memory_usage:.2f} MB")
            )

            for process in processes:
                self.global_tree.insert(
                    parent_global,
                    "end",
                    text=f"PID: {process['pid']}",
                    values=(
                        f"{user}",
                        f"{len(process['threads'])}",
                        f"{process['current_memory']}",
                    ),
                )

                parent_details = self.details_tree.insert(
                                    "",
                                    "end",
                                    text=process['name'],
                                    values=(
                                        process['pid'],
                                        process['priority'],
                                        process['user'],
                                        f"{process['cpu_usage']}%",
                                        f"{process['kernel_time']} s ({process['kernel_percent']}%)",
                                        f"{process['user_time']} s ({process['user_percent']}%)",
                                    )
                                )

                for thread in process['threads']:
                    self.details_tree.insert(
                        parent_details,
                        "end",
                        text=process['name'],
                        values=(
                            process['pid'],
                            "",
                            "",
                            f"{thread['cpu_usage']}%",
                            f"{thread['kernel_time']} s ({thread['kernel_percent']}%)",
                            f"{thread['user_time']} s ({thread['user_percent']}%)",
                            thread['thread_id'],
                            thread['base_priority'],
                            thread['delta_priority']
                        ),
                    )

                self.memory_tree.insert(
                    "",
                    "end",
                    text=process['name'],
                    values=(
                        process['pid'],
                        f"{process['current_memory']} MB",
                        f"{process['peak_memory']} MB"
                    )
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
