import ctypes
from ctypes import wintypes
from tabulate import tabulate

# Constantes de permissões de acesso ao processo
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

# Bibliotecas do sistema para manipular processos
psapi = ctypes.WinDLL('Psapi.dll')
kernel32 = ctypes.WinDLL('kernel32.dll')

# Estrutura retornada pela função de informações de memória
class Memory_Infos(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),             
        ("PeakWorkingSetSize", ctypes.c_size_t),  # Tamanho máximo da memória em uso
        ("WorkingSetSize", ctypes.c_size_t),      # Tamanho atual da memória em uso
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), 
        ("QuotaPagedPoolUsage", ctypes.c_size_t),     
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), 
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),     
        ("PagefileUsage", ctypes.c_size_t),    
        ("PeakPagefileUsage", ctypes.c_size_t),  
    ]

# Enumera os processos do sistema
EnumProcesses = psapi.EnumProcesses
EnumProcesses.restype = wintypes.BOOL

# Retorna o nome do processo
GetModuleBaseName = psapi.GetModuleBaseNameW
GetModuleBaseName.restype = wintypes.DWORD

# Retorna informações de uso de memória do processo
GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
GetProcessMemoryInfo.restype = wintypes.BOOL

# Abre o processo e retorna um handle
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE

# Fecha o processo
CloseHandle = kernel32.CloseHandle

def GetProcessIDs():
    arr = (ctypes.c_ulong * 1024)() # Array de retorno da função
    count = ctypes.c_ulong() # Número total de bytes no array 

    if not EnumProcesses(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(count)):
        raise ctypes.WinError()
    
    # Divide os bytes retornados pelo tamanho de cada elemento
    return arr[:int(count.value / ctypes.sizeof(ctypes.c_ulong))]

def GetProcessName(handle):
    # Buffer de retorno
    buffer = ctypes.create_unicode_buffer(256)
    if GetModuleBaseName(handle, None, buffer, 256) > 0:
        return buffer.value
    else:
        return "erro"
    
def GetProcessMemoryInfos(handle):
    # Cria o objeto de retorno
    mem_infos = Memory_Infos()
    # Tamanho da estrutura
    mem_infos.cb = ctypes.sizeof(Memory_Infos)

    if GetProcessMemoryInfo(handle, ctypes.byref(mem_infos), mem_infos.cb):
        # Retorno em bytes, 1024 ** 2 é a quantidade de bytes em um MB
        return (mem_infos.PeakWorkingSetSize / (1024 ** 2), mem_infos.WorkingSetSize / (1024 ** 2))
    else:
        print("Erro para coletar informação de memória")
        return (0, 0)
    
def list_processes():
    processes = []
    
    for pid in GetProcessIDs():
        handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if handle:
            processes.append((pid, GetProcessName(handle), *GetProcessMemoryInfos(handle)))
            CloseHandle(handle)
    
    return processes

# Exibe os processos
if __name__ == "__main__":
    process_list = list_processes()
    if process_list:
        print(tabulate(process_list, headers=["PID", "Nome", "Pico de uso (MB)", "Uso atual (MB)"], tablefmt="grid"))
    else:
        print("Nenhum processo encontrado")
