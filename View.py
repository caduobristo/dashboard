import os

class SystemView:
    def display(self, process_data):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 50)
        print("Informações do Sistema")
        print("=" * 50)
        for pid, info in process_data.items():
            print(f"PID: {pid}")
            print(f"Nome: {info['name']}")
            print(f"Memória - Pico: {info['peak_memory']} MB, Atual: {info['current_memory']} MB")
            print("Threads:")
            for thread in info.get("threads", []):
                print(f"  Thread ID: {thread['thread_id']}, Base Priority: {thread['base_priority']}, Priority Delta: {thread['priority_delta']}")
            print("-" * 50)