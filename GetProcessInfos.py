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
        ("cb", wintypes.DWORD),                          # Tamanho da estrutura (em bytes)
        ("PeakWorkingSetSize", ctypes.c_size_t),         # Máximo de memória física usada
        ("WorkingSetSize", ctypes.c_size_t),             # Memória física usada atualmente
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),    # Máximo de memória do pool paginado usada
        ("QuotaPagedPoolUsage", ctypes.c_size_t),        # Memória atual do pool paginado usada
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), # Máximo de memória do pool não paginado usada
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),     # Memória atual do pool não paginado usada
        ("PagefileUsage", ctypes.c_size_t),              # Tamanho do arquivo de paginação usado atualmente
        ("PeakPagefileUsage", ctypes.c_size_t),          # Máximo de uso do arquivo de paginação
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
        ("dwSize", wintypes.DWORD),              # Tamanho da estrutura
        ("cntUsage", wintypes.DWORD),            # Contagem de uso
        ("th32ThreadID", wintypes.DWORD),        # ID do thread
        ("th32OwnerProcessID", wintypes.DWORD),  # ID do processo ao qual o thread pertence
        ("tpBasePri", wintypes.LONG),            # Prioridade base do thread
        ("tpDeltaPri", wintypes.LONG),           # Alteração na prioridade
        ("dwFlags", wintypes.DWORD),             # Reservado, não usado
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
    count = ctypes.c_ulong()        # Número total de bytes no array 

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

    # Retorno em bytes, 1024 ** 2 é a quantidade de bytes em um MB
    def convert_to_MB(size):
        return round(size/(1024 ** 2), 2)

    if GetProcessMemoryInfo(handle, ctypes.byref(mem_infos), mem_infos.cb):
        peak = convert_to_MB(mem_infos.PeakWorkingSetSize)
        current = convert_to_MB(mem_infos.WorkingSetSize)
        nonPaged = convert_to_MB(mem_infos.QuotaNonPagedPoolUsage)
        paged = convert_to_MB(mem_infos.PagefileUsage)
        maxPaged = convert_to_MB(mem_infos.PeakPagefileUsage)

        return {"peak": peak, "current": current, "nonPaged": nonPaged,
                "paged": paged, "maxPaged": maxPaged}        
    else:
        return {"peak": 'N/A', "current": 'N/A', "nonPaged": 'N/A',
                "paged": 'N/A', "maxPaged": 'N/A'} 

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

        # Obtém as informações do token
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

        # Converte os dados em string
        if not LookupAccountSid(None, sid, name, ctypes.byref(name_size), domain, ctypes.byref(domain_size), ctypes.byref(sid_name_use)):
            return "N/A"

        return name.value
    finally:
        CloseHandle(token_handle)

GetProcessTimes = kernel32.GetProcessTimes
GetProcessTimes.restype = wintypes.BOOL

def GetProcessCPUUsage(handle):
    creation = FILETIME()
    exit = FILETIME()
    kernel = FILETIME()
    user = FILETIME()

    if GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit), 
                       ctypes.byref(kernel), ctypes.byref(user)):
        # Converte FILETIME para inteiro (segundo)
        def filetime_to_int(filetime):
            # FILETIME separa o total em dois valores de 32 bits
            return ((filetime.dwHighDateTime << 32) | filetime.dwLowDateTime) / 10_000_000
        '''
        Como a função Time() retorna o valor baseado na data 1º de janeiro de 1970 e
        o valor de criação é baseado na data 1º de janeiro de 1601 é necessário somar 
        11644473600 segundos para alinhar com o valor de creation
        '''
        current = time.time() + 11_644_473_600
    
        total = current - filetime_to_int(creation)
        kernel = filetime_to_int(kernel)
        kernel_percent = round(kernel/total * 100, 2)
        user = filetime_to_int(user)
        user_percent = round(user/total * 100, 2)
        cpu_usage = round((kernel+user)/total * 100, 2)

        return {"cpu_usage": cpu_usage, 
                "kernel": kernel, "kernel_percent": kernel_percent, 
                "user": user, "user_percent": user_percent}
        
    return {"cpu_usage": 'N/A', 
            "kernel": 'N/A', "kernel_percent": 'N/A',
            "user": 'N/A', "user_percent": 'N/A'}

GetPriorityClass = kernel32.GetPriorityClass
GetPriorityClass.restype = wintypes.DWORD

def GetProcessPriority(handle):
    priority = GetPriorityClass(handle)
    if priority == 32:
        return "Baixa"
    elif priority == 64:
        return "Ocioso"
    elif priority == 32768:
        return "Acima do Normal"
    elif priority == 128:
        return "Alta"
    elif priority == 256:
        return "Tempo Real"
    elif priority == 16384:
        return "Abaixo do Normal"
    else:
        return "N/A"

# Função que retorna os tempos do thread
GetThreadTimes = kernel32.GetThreadTimes
GetThreadTimes.restype = wintypes.BOOL

def GetThreadsTimes(thread_id):
    creation = FILETIME()
    exit = FILETIME()
    kernel = FILETIME()
    user = FILETIME()
    
    try:
        handle = kernel32.OpenThread(THREAD_QUERY_INFORMATION, False, thread_id)
        if not handle:
            return {"cpu_usage": 'N/A', 
                    "kernel": 'N/A', "kernel_percent": 'N/A',
                    "user": 'N/A', "user_percent": 'N/A'}
        
        def filetime_to_int(filetime):
            # FILETIME separa o total em dois valores de 32 bits
            return ((filetime.dwHighDateTime << 32) | filetime.dwLowDateTime) / 10_000_000

        if GetThreadTimes(handle, ctypes.byref(creation), ctypes.byref(exit), 
                        ctypes.byref(kernel), ctypes.byref(user)):
            '''
            Como a função Time() retorna o valor baseado na data 1º de janeiro de 1970 e
            o valor de criação é baseado na data 1º de janeiro de 1601 é necessário somar 
            11644473600 segundos para alinhar com o valor de creation
            '''
            current = time.time() + 11644473600

            total = current - filetime_to_int(creation)
            exit = filetime_to_int(exit)
            kernel = filetime_to_int(kernel)
            kernel_percent = round(kernel/total * 100, 2)
            user = filetime_to_int(user)
            user_percent = round(user/total * 100, 2)
            cpu_usage = round((kernel+user)/total * 100, 2)

            return {"cpu_usage": cpu_usage, 
                "kernel": kernel, "kernel_percent": kernel_percent, 
                "user": user, "user_percent": user_percent}
        
        return {"cpu_usage": 'N/A', 
                "kernel": 'N/A', "kernel_percent": 'N/A',
                "user": 'N/A', "user_percent": 'N/A'}
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
            threads = {
                "thread_id": 'N/A', 
                "base_priority": 'N/A',
                "delta_priority": 'N/A', 
                "cpu_usage": 'N/A',
                "kernel_time": 'N/A',     
                "kernel_percent": 'N/A',
                "user_time": 'N/A',          
                "user_percent": 'N/A'
            }

        # Enquanto ainda houver threads
        while has_thread:
            pid = thread.th32OwnerProcessID

            times = GetThreadsTimes(thread.th32ThreadID)

            # Conjunto com as informações dos threads
            thread_info = {
                "thread_id": thread.th32ThreadID, 
                "base_priority": thread.tpBasePri,
                "delta_priority": thread.tpDeltaPri, 
                "cpu_usage": times['cpu_usage'],
                "kernel_time": times['kernel'],     
                "kernel_percent": times['kernel_percent'],
                "user_time": times['user'],          
                "user_percent": times['user_percent']
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
                        "cpu_usage": times['cpu_usage'],
                        "kernel_time": times['kernel'],
                        "kernel_percent": times['kernel_percent'],
                        "user_time": times['user'],
                        "user_percent": times['user_percent'],
                        "peak_memory": memory['peak'],
                        "current_memory": memory['current'],
                        "nonPaged_memory": memory['nonPaged'],
                        "paged_memory": memory['paged'],
                        "maxPaged_memory": memory['maxPaged'],
                        "user": GetProcessUser(handle),
                        "priority": GetProcessPriority(handle),
                        "threads": threads.get(pid, [])
                }
        finally:
            CloseHandle(handle)
    return processes

