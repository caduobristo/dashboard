import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class View:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Dashboard de recursos do sistema")
        self.root.protocol("WM_DELETE_WINDOW", self.CloseApp)
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

        self.graph_frame = tk.Frame(self.main_frame)
        self.graph_frame.pack(expand=True, fill=tk.BOTH)

        # Criar figuras para os gráficos
        self.fig_cpu, self.ax_cpu = plt.subplots(figsize=(4, 4))
        self.fig_mem, self.ax_mem = plt.subplots(figsize=(4, 4))

        # Criar canvases do Tkinter para exibir os gráficos
        self.canvas_cpu = FigureCanvasTkAgg(self.fig_cpu, master=self.graph_frame)
        self.canvas_cpu.get_tk_widget().pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.canvas_mem = FigureCanvasTkAgg(self.fig_mem, master=self.graph_frame)
        self.canvas_mem.get_tk_widget().pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def UpdateGraphs(self, cpu_usage, mem_usage):
        """ Atualiza os gráficos de CPU e Memória """
        if not self.root.winfo_exists():  # Se a janela foi fechada, não faz nada
            return
        
        self.ax_cpu.clear()
        self.ax_mem.clear()
        print(f"CPU Usage Data: {cpu_usage}")
        print(f"Memory Usage Data: {mem_usage}")

        # Gráfico de pizza para CPU
        if sum(cpu_usage) != 0:
            labels_cpu = ["Usuário", "Sistema", "Ocioso"]
            colors_cpu = ["#ff9999", "#66b3ff", "#99ff99"]
            self.ax_cpu.pie(cpu_usage, labels=labels_cpu, autopct='%1.1f%%', colors=colors_cpu, startangle=140)
            self.ax_cpu.set_title("Uso da CPU (%)")

        # Gráfico de pizza para Memória
        labels_mem = ["Usada", "Livre"]
        colors_mem = ["#ffcc99", "#c2c2f0"]
        self.ax_mem.pie(mem_usage, labels=labels_mem, autopct='%1.1f%%', colors=colors_mem, startangle=140)
        self.ax_mem.set_title("Uso da Memória (%)")

        # Atualizar os canvases
        self.canvas_cpu.draw()
        self.canvas_mem.draw()

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
        def safe_float(value):
            try:
                val = float(value)
                return val if not math.isnan(val) else 0
            except (ValueError, TypeError):
                return 0  # Se for 'N/A', retorna 0
        if global_data:
            cpu_usage = [
                safe_float(global_data.get('user', 0)),
                safe_float(global_data.get('kernel', 0)),
                safe_float(global_data.get('idle', 0))
            ]
            mem_usage = [
                safe_float(global_data.get('memory_percent_phys', 0)),
                100 - safe_float(global_data.get('memory_percent_phys', 0))
            ]
            self.UpdateGraphs(cpu_usage, mem_usage)

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

            for process in processes:

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
    def CloseApp(self):
        """ Cancela atualizações e fecha o app corretamente """
        self.controller.stop()  # Interrompe a atualização no Controller
        if hasattr(self, "update_task"):
            self.root.after_cancel(self.update_task)  # Cancela atualizações pendentes
        plt.close('all')  # Fecha os gráficos do matplotlib
        self.root.quit()  # Encerra o loop principal do Tkinter
        self.root.destroy()  # Fecha a janela

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