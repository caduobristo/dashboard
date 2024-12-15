import tkinter as tk
from tkinter import ttk

class View:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard de recursos do sistema")
        self.root.state("zoomed")

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.menu.add_command(label="Tela principal", command=self.ShowMain)
        self.menu.add_command(label="Dados detalhados", command=self.ShowDetails)
        self.menu.add_command(label="Dados de memória", command=self.ShowMemory)

        self.main_frame = tk.Frame(self.root)
        self.details_frame = tk.Frame(self.root)
        self.memory_frame = tk.Frame(self.root)

        self.CreateMain()
        self.CreateDetails()
        self.CreateMemory()

        self.ShowMain()

    def CreateMain(self):
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

        for col in self.global_tree["columns"]:
            self.global_tree.column(col, width=150, anchor=tk.W)
            self.global_tree.heading(col, text=col, anchor=tk.W)

        self.global_tree.pack(expand=True, fill=tk.BOTH)

        scroll.config(command=self.global_tree.yview)

    def CreateDetails(self):
        self.details_info = tk.Label(self.details_frame, text="Carregando informações...")
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
            "ID", "Prioridade", "Usuário", "Uso da CPU", 
            "Tempo de kernel", "Tempo de usuário",
            "Prioridade base", "Prioridade Alterada")

        self.details_tree.column("#0", width=200, anchor=tk.W)
        self.details_tree.heading("#0", text="Processo", anchor=tk.W)

        for col in self.details_tree["columns"]:
            self.details_tree.column(col, width=150, anchor=tk.W)
            self.details_tree.heading(col, text=col, anchor=tk.W)

        self.details_tree.pack(expand=True, fill=tk.BOTH)
        scroll.config(command=self.details_tree.yview)

    def CreateMemory(self):
        self.memory_info = tk.Label(self.memory_frame, text="Carregando informações...")
        self.memory_info.pack(pady=20)

        tree_frame = tk.Frame(self.memory_frame)
        tree_frame.pack(expand=True, fill=tk.BOTH)

        scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.memory_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=scroll.set,
        )
        self.memory_tree["columns"] = (
            "PID", "Uso de memória", "Pico de memória",
            "Memória não paginada", "Memória paginada",
            "Máximo de memória paginada")

        self.memory_tree.column("#0", anchor=tk.W)
        self.memory_tree.heading("#0", text="Processo", anchor=tk.W)

        for col in self.memory_tree["columns"]:
            self.memory_tree.column(col, width=150, anchor=tk.W)
            self.memory_tree.heading(col, text=col, anchor=tk.W)

        self.memory_tree.pack(expand=True, fill=tk.BOTH)
        scroll.config(command=self.memory_tree.yview)

    def ShowMain(self):
        self.details_frame.pack_forget()
        self.memory_frame.pack_forget()
        self.main_frame.pack(expand=True, fill=tk.BOTH)

    def ShowDetails(self):
        self.main_frame.pack_forget()
        self.memory_frame.pack_forget()
        self.details_frame.pack(expand=True, fill=tk.BOTH)

    def ShowMemory(self):
        self.main_frame.pack_forget()
        self.details_frame.pack_forget()
        self.memory_frame.pack(expand=True, fill=tk.BOTH)
    
    def Display(self, processes, global_data):
        # Configura as informações globais de cada tela
        if global_data:
            self.global_info.config(
                text=(
                    "INFORMAÇÕES GERAIS\n\n"
                    f"Uso de CPU: {global_data['cpu_usage']}% | "
                    f"Memória: {global_data['memory_used_phys']}GB/{global_data['memory_total_phys']}GB "
                    f"({global_data['memory_percent_phys']}%) | "
                    f"Disco: {global_data['disk_used']}GB/{global_data['disk_total']}GB "
                    f"({global_data['disk_percent']}%)"
                )
            )
            self.details_info.config(
                text=(
                    "INFORMAÇÕES DETALHADAS\n\n"
                    f"Uso de CPU: {global_data['cpu_usage']}% | Tempo ocioso: {global_data['idle']}% | "
                    f"Tempo de kernel: {global_data['kernel']}% | Tempo de usuário: {global_data['user']}% | "
                    f"Número de processadores: {global_data['n_processors']}"
                )
            )
            self.memory_info.config(
                text=(
                    "INFORMAÇÕES DETALHADAS DE MEMÓRIA\n\n"
                    f"Memória física: {global_data['memory_used_phys']}GB/{global_data['memory_total_phys']}GB "
                    f"({global_data['memory_percent_phys']}%)\n"
                    f"Memória virtual: {global_data['memory_used_virt']}GB/{global_data['memory_total_virt']}GB "
                    f"({global_data['memory_percent_virt']}%)"
                )
            )

        # Limpas os dados anteriores
        for item in self.global_tree.get_children():
            self.global_tree.delete(item)

        for item in self.details_tree.get_children():
                self.details_tree.delete(item)

        for item in self.memory_tree.get_children():
                self.memory_tree.delete(item)

        # Agrupa os processos por nome
        grouped = group_processes(processes)

        for name, processes in grouped.items():
            user = processes[0]['user']
            memory_usage = sum(p['current_memory'] for p in processes)
            n_threads = sum(len(p['threads']) for p in processes)

            # Informações somadas do processo
            parent_global = self.global_tree.insert(
                "", "end", text=f"{name} ({len(processes)})",
                values=(user, f"{n_threads}", f"{memory_usage:.2f} MB")
            )

            for process in processes:
                # Informações de todos os processos separadamente
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

                # Informações detalhadas dos processos
                parent_details = self.details_tree.insert(
                    "",
                    "end",
                    text=f"{process['name']} ({len(process['threads'])})",
                    values=(
                        process['pid'],
                        process['priority'],
                        process['user'],
                        f"{process['cpu_usage']}%",
                        f"{process['kernel_time']} s ({process['kernel_percent']}%)",
                        f"{process['user_time']} s ({process['user_percent']}%)",
                    )
                )

                # Informações dos threads de cada processo
                for thread in process['threads']:
                    self.details_tree.insert(
                        parent_details,
                        "end",
                        text="",
                        values=(
                            thread['thread_id'],
                            "",
                            "",
                            f"{thread['cpu_usage']}%",
                            f"{thread['kernel_time']} s ({thread['kernel_percent']}%)",
                            f"{thread['user_time']} s ({thread['user_percent']}%)",
                            thread['base_priority'],
                            thread['delta_priority']
                        ),
                    )

                # Porcentagem de uso de memória física pelo processo
                percent_memory = round(process['current_memory']/(global_data['memory_total_phys']*1000)*100,2)

                # Informações detalhadas de memória para cada processo
                self.memory_tree.insert(
                    "",
                    "end",
                    text=process['name'],
                    values=(
                        process['pid'],
                        f"{process['current_memory']} MB ({percent_memory}%)",
                        f"{process['peak_memory']} MB",
                        f"{process['nonPaged_memory']} MB",
                        f"{process['paged_memory']} MB",
                        f"{process['maxPaged_memory']} MB",
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
