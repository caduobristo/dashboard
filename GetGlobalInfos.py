import os
import ctypes

# Bibliotecas do sistema para coletar informações do sistema
kernel32 = ctypes.WinDLL('kernel32.dll')

# Estrutura de retorno da função de informações da CPU
class SYSTEM_INFO(ctypes.Structure):
    _fields_ = [
        ("wProcessorArchitecture", ctypes.c_ushort), # Arquitetura
        ("wReserved", ctypes.c_ushort),              # Reservado, não utilizao
        ("dwPageSize", ctypes.c_uint),               # Tamanho da página de memória
        ("lpMinimumApplicationAddress", ctypes.c_void_p), # Endereço mínimo acessível
        ("lpMaximumApplicationAddress", ctypes.c_void_p), # Endereço máximo acessível
        # Indicação de quais processadores estão disponíveis, cada bit representa um processador
        ("dwActiveProcessorMask", ctypes.POINTER(ctypes.c_uint)),
        ("dwNumberOfProcessors", ctypes.c_uint),    # Número de processadores lógicos
        ("dwProcessorType", ctypes.c_uint),         # Tipo de processador
        ("dwAllocationGranularity", ctypes.c_uint), # Tamanho mínimo de uma unidade de memória alocada em memória virtual.
        ("wProcessorLevel", ctypes.c_ushort),       # Nível do processador
        ("wProcessorRevision", ctypes.c_ushort),    # Revisão do processador
    ]

# Estrutura de retorno da função de memória
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),               # Tamanho da estrutura (em bytes)
        ("dwMemoryLoad", ctypes.c_ulong),           # Percentual de memória em uso
        ("ullTotalPhys", ctypes.c_ulonglong),       # Total de memória física (RAM) no sistema
        ("ullAvailPhys", ctypes.c_ulonglong),       # Memória física disponível
        ("ullTotalPageFile", ctypes.c_ulonglong),   # Tamanho total do arquivo de paginação
        ("ullAvailPageFile", ctypes.c_ulonglong),   # Espaço disponível no arquivo de paginação
        ("ullTotalVirtual", ctypes.c_ulonglong),    # Tamanho total do espaço de endereçamento virtual
        ("ullAvailVirtual", ctypes.c_ulonglong),    # Espaço de endereçamento virtual disponível
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong), # Memória estendida disponível (sempre 0 no Windows atual)
    ]

previous_idle = 0
previous_kernel = 0
previous_user = 0
previous_total = 0

# Estrutura de retorno da função de uso da CPU
class FILETIME(ctypes.Structure):
    _fields_ = [
        ("dwLowDateTime", ctypes.c_uint),
        ("dwHighDateTime", ctypes.c_uint),
    ]

# Obtém informações de CPU usando GetSystemTimes
def get_cpu_infos():
    '''
    A função retorna o tempo de uso desde a inicialização do sistema,
    portanto é necessário descontar valores obtidos anteriormentes para um resultado preciso
    '''
    global previous_idle, previous_kernel, previous_user, previous_total
    idle_time = FILETIME()
    kernel_time = FILETIME()
    user_time = FILETIME()

    kernel32.GetSystemTimes(
        ctypes.byref(idle_time), ctypes.byref(kernel_time), ctypes.byref(user_time)
    )

    # Converte LIFETIME para inteiro (unidades de 100-nanosegundos)
    def filetime_to_int(filetime):
        return (filetime.dwHighDateTime << 32) | filetime.dwLowDateTime

    idle = filetime_to_int(idle_time)
    kernel = filetime_to_int(kernel_time)
    user = filetime_to_int(user_time)
    total = (kernel-idle) + user + idle

    # Calculo da porcentagem de uso de usuário, kernel e tempo ocioso da CPU
    if previous_idle > 0:
        delta_idle = idle - previous_idle
        delta_kernel = (kernel - idle) - (previous_kernel - previous_idle)
        delta_user = user- previous_user
        delta_total = total - previous_total

        percent_idle = round(delta_idle / delta_total * 100, 2)
        percent_kernel = round(delta_kernel / delta_total * 100, 2)
        percent_user = round(delta_user / delta_total * 100, 2)
        cpu_usage = round(percent_user + percent_kernel, 2)
    else:
        delta_idle = delta_kernel = delta_user = delta_total = 'N/A'
        percent_idle = percent_kernel = percent_user = cpu_usage = 'N/A'

    # Atualiza valores anteriores
    previous_idle = idle
    previous_kernel = kernel
    previous_user = user
    previous_total = total

    system_info = SYSTEM_INFO()
    kernel32.GetSystemInfo(ctypes.byref(system_info))

    n_processors = system_info.dwNumberOfProcessors
    page_size = system_info.dwPageSize 

    return {
        # Converte os valores de tempo para porcentagem
        "idle": percent_idle,                           
        "kernel": percent_kernel,                   
        "user": percent_user,                          
        "cpu_usage": cpu_usage,                           
        "n_processors": n_processors,
        "page_size": page_size,                   
    }

# Obtém informações de memória usando GlobalMemoryStatusEx
def get_memory_info():
    memory_status = MEMORYSTATUSEX()
    memory_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    kernel32.GlobalMemoryStatusEx(ctypes.byref(memory_status))

    return {
        "total": round(memory_status.ullTotalPhys / (1024**3), 2),  # Em GB
        "available": round(memory_status.ullAvailPhys / (1024**3), 2),
        "used": round(
            (memory_status.ullTotalPhys - memory_status.ullAvailPhys) / (1024**3), 2
        ),
        "percent": memory_status.dwMemoryLoad,
    }

# Obtém informações de disco usando GetDiskFreeSpaceEx
def get_disk_info():
    free_bytes = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    total_free_bytes = ctypes.c_ulonglong(0)

    kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(os.getenv("SystemDrive") + "\\"),  # Disco principal
        ctypes.byref(free_bytes),
        ctypes.byref(total_bytes),
        ctypes.byref(total_free_bytes),
    )

    return {
        "total": round(total_bytes.value / (1024**3), 2),  # Em GB
        "used": round((total_bytes.value - free_bytes.value) / (1024**3), 2),
        "free": round(free_bytes.value / (1024**3), 2),
        "percent": round(
            (total_bytes.value - free_bytes.value) / total_bytes.value * 100, 2
        ),
    }