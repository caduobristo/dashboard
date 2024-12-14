import ctypes
import time
from ctypes import wintypes

# Constantes de permissões de acesso ao processo
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
TOKEN_QUERY = 0x0008
TH32CS_SNAPTHREAD = 0x00000004
THREAD_QUERY_INFORMATION = 0x0040

# Bibliotecas do sistema para manipular processos
psapi = ctypes.WinDLL('Psapi.dll')
kernel32 = ctypes.WinDLL('kernel32.dll')
advapi32 = ctypes.WinDLL('Advapi32.dll')

# Estrutura retornada pela função de informações de memória
class MEMORY_INFOS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),                       # Tamanho da estrutura (em bytes)
        ("PeakWorkingSetSize", ctypes.c_size_t),      # Máximo de memória física usada
        ("WorkingSetSize", ctypes.c_size_t),          # Memória física usada atualmente
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), # Máximo de memória do pool paginado usada
        ("QuotaPagedPoolUsage", ctypes.c_size_t),     # Memória atual do pool paginado usada
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), # Máximo de memória do pool não paginado usada
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),  # Memória atual do pool não paginado usada
        ("PagefileUsage", ctypes.c_size_t),           # Tamanho do arquivo de paginação usado atualmente
        ("PeakPagefileUsage", ctypes.c_size_t),       # Máximo de uso do arquivo de paginação
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

# Estrutura de retorno do tempo dos threads
class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", ctypes.c_uint),
        ("dwHighDateTime", ctypes.c_uint),
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
        return "N/A"

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
        return (-1, -1)

# Abre o token do processo
OpenProcessToken = advapi32.OpenProcessToken
OpenProcessToken.restype = wintypes.BOOL

# Obtém informações do token
GetTokenInformation = advapi32.GetTokenInformation
GetTokenInformation.restype = wintypes.BOOL

# Converte o SID para string
LookupAccountSid = advapi32.LookupAccountSidW
LookupAccountSid.restype = wintypes.BOOL

# Fecha o processo
CloseHandle = kernel32.CloseHandle

def GetProcessUser(handle):
    token_handle = wintypes.HANDLE()
    # Obtem o token de segurança do processo
    if not OpenProcessToken(handle, TOKEN_QUERY, ctypes.byref(token_handle)):
        return "N/A"
    
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

        return name.value
    finally:
        CloseHandle(token_handle)

GetProcessTimes = kernel32.GetProcessTimes
GetProcessTimes.restype = wintypes.BOOL

previously = {"kernel": 0, "user": 0}

def GetProcessCPUUsage(handle):
    global previously
    creation = FILETIME()
    exit = FILETIME()
    kernel = FILETIME()
    user = FILETIME()

    if GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit), 
                       ctypes.byref(kernel), ctypes.byref(user)):
        # Converte FILETIME para inteiro (segundos)
        def filetime_to_int(filetime):
            return ((filetime.dwHighDateTime << 32) | filetime.dwLowDateTime) / 10000000
        
        creation = filetime_to_int(creation)
        exit = filetime_to_int(exit)
        kernel = filetime_to_int(kernel)
        user = filetime_to_int(user)

        return {"creation": creation, "exit": exit, "kernel": kernel, "user": user}
        
    return {"creation": 'N/A', "exit": 'N/A', "kernel": 'N/A', "user": 'N/A'}

GetPriorityClass = kernel32.GetPriorityClass
GetPriorityClass.restype = wintypes.DWORD

def GetProcessPriority(handle):
    priority = GetPriorityClass(handle)
    if priority == 0:
        return "N/A"
    elif priority == 32:
        return "Baixa"
    else:
        return "Alta"

# Função que retorna os tempos do thread
GetThreadTimes = kernel32.GetThreadTimes
GetThreadTimes.restype = wintypes.BOOL

def GetThreadsTimes(thread_id):
    handle = kernel32.OpenThread(THREAD_QUERY_INFORMATION, False, thread_id)
    if not handle:
        return {"kernel": 0, "user":0}
    
    def filetime_to_ms(filetime):
        return ((filetime.dwHighDateTime << 32) | filetime.dwLowDateTime) / 10000
    
    try:
        creation = FILETIME()
        exit = FILETIME()
        kernel = FILETIME()
        user = FILETIME()

        if GetThreadTimes(handle, ctypes.byref(creation), ctypes.byref(exit), 
                          ctypes.byref(kernel), ctypes.byref(user)):
            return {
                "kernel": filetime_to_ms(kernel),
                "user": filetime_to_ms(user)
            }
        return {"kernel": 0, "user":0}
    finally:
        CloseHandle(handle)

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
        thread = THREAD_INFOS()
        thread.dwSize = ctypes.sizeof(THREAD_INFOS)
        
        threads = {} 
        # Obtém o primeiro thread do snapshot
        has_thread = Thread32First(snapshot, ctypes.byref(thread))
        if not has_thread:
            return {} 
        
        # Enquanto a função retornar true
        while has_thread:
            pid = thread.th32OwnerProcessID

            times = GetThreadsTimes(thread.th32ThreadID)

            # Conjunto com as informações dos threads
            thread_info = {
                "thread_id": thread.th32ThreadID,    # ID do thread
                "base_priority": thread.tpBasePri,   # Prioridade base
                "delta_priority": thread.tpDeltaPri, # Alteração na prioridade
                "kernel_time": times['kernel'],      # Tempo de kernel 
                "user_time": times['user']           # Tempo de usuário
            }

            # Adiciona o thread na biblioteca, organizando pelo pid do processo
            if pid not in threads:
                threads[pid] = []
            threads[pid].append(thread_info)

            has_thread = Thread32Next(snapshot, ctypes.byref(thread))
        
        return threads
    finally:
        CloseHandle(snapshot)

# Abre o processo e retorna um handle
OpenProcess = kernel32.OpenProcess
OpenProcess.restype = wintypes.HANDLE

def list_processes():
    processes = {}
    threads = GetThreads()
    for pid in GetProcessIDs():
        try:
            handle = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
            if handle:
                memory = GetProcessMemoryInfos(handle)
                times = GetProcessCPUUsage(handle)
                processes[pid] = {
                        "name": GetProcessName(handle),
                        "creation_time": times['cpu_usage'],
                        "exit_time": times['exit'],
                        "kernel_time": times['kernel'],
                        "user_time": times['user'],
                        "peak_memory": memory[0],
                        "current_memory": memory[1],
                        "user": GetProcessUser(handle),
                        "priority": GetProcessPriority(handle),
                        "threads": threads.get(pid, [])
                }
        finally:
            CloseHandle(handle)
    return processes

