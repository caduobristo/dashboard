import ctypes
from ctypes import wintypes
from tabulate import tabulate

# Constantes de permissões de acesso ao processo
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
TOKEN_QUERY = 0x0008
TH32CS_SNAPTHREAD = 0x00000004

# Bibliotecas do sistema para manipular processos
psapi = ctypes.WinDLL('Psapi.dll')
kernel32 = ctypes.WinDLL('kernel32.dll')
advapi32 = ctypes.WinDLL('Advapi32.dll')

# Estrutura retornada pela função de informações de memória
class MEMORY_INFOS(ctypes.Structure):
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

# Estruturas retornadas pelas funções de informações de usuários
class SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Sid", ctypes.POINTER(ctypes.c_byte)),
        ("Attributes", wintypes.DWORD),
    ]

class TOKEN_USER(ctypes.Structure):
    _fields_ = [
        ("User", SID_AND_ATTRIBUTES),
    ]

# Estrutura retornada pela função de informações de threads
class THREAD_INFOS(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),        # Tamanho da estrutura
        ("cntUsage", wintypes.DWORD),      # Contagem de uso
        ("th32ThreadID", wintypes.DWORD),  # ID do thread
        ("th32OwnerProcessID", wintypes.DWORD),  # ID do processo ao qual o thread pertence
        ("tpBasePri", wintypes.LONG),      # Prioridade base do thread
        ("tpDeltaPri", wintypes.LONG),     # Alteração na prioridade
        ("dwFlags", wintypes.DWORD),       # Reservado, não usado
    ]

# Enumera os processos do sistema
EnumProcesses = psapi.EnumProcesses
EnumProcesses.restype = wintypes.BOOL

def GetProcessIDs():
    arr = (ctypes.c_ulong * 1024)() # Array de retorno da função
    count = ctypes.c_ulong() # Número total de bytes no array 

    if not EnumProcesses(ctypes.byref(arr), ctypes.sizeof(arr), ctypes.byref(count)):
        raise ctypes.WinError()
    
    # Divide os bytes retornados pelo tamanho de cada elemento
    return arr[:int(count.value / ctypes.sizeof(ctypes.c_ulong))]

# Retorna o nome do processo
GetModuleBaseName = psapi.GetModuleBaseNameW
GetModuleBaseName.restype = wintypes.DWORD

def GetProcessName(handle):
    # Buffer de retorno
    buffer = ctypes.create_unicode_buffer(256)
    if GetModuleBaseName(handle, None, buffer, 256) > 0:
        return buffer.value
    else:
        return "erro"

# Retorna informações de uso de memória do processo
GetProcessMemoryInfo = psapi.GetProcessMemoryInfo
GetProcessMemoryInfo.restype = wintypes.BOOL

def GetProcessMemoryInfos(handle):
    # Cria o objeto de retorno
    mem_infos = MEMORY_INFOS()
    # Tamanho da estrutura
    mem_infos.cb = ctypes.sizeof(MEMORY_INFOS)

    if GetProcessMemoryInfo(handle, ctypes.byref(mem_infos), mem_infos.cb):
        # Retorno em bytes, 1024 ** 2 é a quantidade de bytes em um MB
        return mem_infos.PeakWorkingSetSize / (1024 ** 2), mem_infos.WorkingSetSize / (1024 ** 2)
    else:
        print("Erro para coletar informação de memória")
        return (0, 0)

# Abre o token do processo
OpenProcessToken = advapi32.OpenProcessToken
OpenProcessToken.restype = wintypes.BOOL

# Obtém informações do token
GetTokenInformation = advapi32.GetTokenInformation
GetTokenInformation.restype = wintypes.BOOL

# Converte o SID para string
LookupAccountSid = advapi32.LookupAccountSidW
LookupAccountSid.restype = wintypes.BOOL

def GetProcessUser(handle):
    token_handle = wintypes.HANDLE()
    # Obtem o token de segurança do processo
    if not OpenProcessToken(handle, TOKEN_QUERY, ctypes.byref(token_handle)):
        raise ctypes.WinError
    
    try:
        token_user_size = wintypes.DWORD()

        # Obtém o tamanho necessário para o buffer
        GetTokenInformation(token_handle, 1, None, 0, ctypes.byref(token_user_size))
        buffer = ctypes.create_string_buffer(token_user_size.value)

        if not GetTokenInformation(token_handle, 1, buffer, token_user_size, ctypes.byref(token_user_size)):
            return "N/A"

        # Converte o buffer em um ponteiro do tipo TOKEN_USER e retorna o seu conteúdo
        token_user = ctypes.cast(buffer, ctypes.POINTER(TOKEN_USER)).contents
        sid = token_user.User.Sid

        # Buffer para o nome e domínio
        name = ctypes.create_unicode_buffer(256)
        domain = ctypes.create_unicode_buffer(256)
        name_size = wintypes.DWORD(256)
        domain_size = wintypes.DWORD(256)
        sid_name_use = wintypes.DWORD()

        if not LookupAccountSid(None, sid, name, ctypes.byref(name_size), domain, ctypes.byref(domain_size), ctypes.byref(sid_name_use)):
            return "N/A"

        return domain.value, name.value
    finally:
        CloseHandle(token_handle)
    

# Abre o processo e retorna um handle
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE

# Fecha o processo
CloseHandle = kernel32.CloseHandle

def list_processes():
    processes = []
    for pid in GetProcessIDs():
        handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
        if handle:
            processes.append((pid, GetProcessName(handle), *GetProcessMemoryInfos(handle), *GetProcessUser(handle)))
            CloseHandle(handle)
    return processes

# Retorna estado atual dos threads do sistema
CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
CreateToolhelp32Snapshot.restype = wintypes.HANDLE

# Retorna o primeiro thread do snapshot
Thread32First = kernel32.Thread32First
Thread32First.restype = wintypes.BOOL

# Retorna o próximo thread do snapshot
Thread32Next = kernel32.Thread32Next
Thread32Next.restype = wintypes.BOOL

def GetThreads():
    # Estado atual dos threados do sistema
    snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if snapshot == -1:
        raise ctypes.WinError()
    
    try:
        thread_entry = THREAD_INFOS()
        thread_entry.dwSize = ctypes.sizeof(THREAD_INFOS)
        
        threads = [] 
        # Obtém o primeiro thread do snapshot
        has_thread = Thread32First(snapshot, ctypes.byref(thread_entry))
        if not has_thread:
            return [] 
        
        # Enquanto a função retornar true
        while has_thread:
            threads.append((
                thread_entry.th32OwnerProcessID, # ID do processo
                thread_entry.th32ThreadID,       # ID do thread
                thread_entry.tpBasePri,          # Prioridade base
                thread_entry.tpDeltaPri          # Alteração na prioridade
            ))
            has_thread = Thread32Next(snapshot, ctypes.byref(thread_entry))
        
        return threads
    finally:
        CloseHandle(snapshot)

# Lista todos os threads
def list_all_process_threads():
    processes_with_threads = GetThreads()
    print(tabulate(processes_with_threads, headers=["ID do processo", "ID", "Base priority", "Delta priority"], tablefmt="grid"))

# Exibe os processos
if __name__ == "__main__":
    process_list = list_processes()
    if process_list:
        print(tabulate(process_list, headers=["PID", "Nome", "Pico de uso (MB)", "Uso atual (MB)", "Domínio", "Usuário"], tablefmt="grid"))
    else:
        print("Nenhum processo encontrado")
    
    list_all_process_threads()
