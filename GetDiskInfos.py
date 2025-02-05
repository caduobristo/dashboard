import ctypes
import ctypes.wintypes

kernel32 = ctypes.WinDLL('kernel32.dll', use_last_error=True)

class WIN32_FIND_DATAW(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", ctypes.wintypes.DWORD),
        ("ftCreationTime", ctypes.wintypes.FILETIME),
        ("ftLastAccessTime", ctypes.wintypes.FILETIME),
        ("ftLastWriteTime", ctypes.wintypes.FILETIME),
        ("nFileSizeHigh", ctypes.wintypes.DWORD),
        ("nFileSizeLow", ctypes.wintypes.DWORD),
        ("dwReserved0", ctypes.wintypes.DWORD),
        ("dwReserved1", ctypes.wintypes.DWORD),
        ("cFileName", ctypes.c_wchar * 260),
        ("cAlternateFileName", ctypes.c_wchar * 14)
    ]

GetLogicalDrives = kernel32.GetLogicalDrives
GetDriveTypeW = kernel32.GetDriveTypeW

def GetDiskInfos():
    drives = []

    for letter in range(26):  # De A a Z
        if GetLogicalDrives() & (1 << letter):
            drive_letter = f'{chr(65 + letter)}:\\'
            drive_type = GetDriveTypeW(ctypes.c_wchar_p(drive_letter))
            
            if drive_type == 3:  # DRIVE_FIXED
                total, free = GetDriveSpace(drive_letter)
                used = total - free
                percent_used = (used / total * 100) if total > 0 else 0
                root_dirs = GetRootDirs(drive_letter)

                drives.append({
                    'path': drive_letter,
                    'total_gb': round(total / (1024 ** 3), 2),
                    'used_gb': round(used / (1024 ** 3), 2),
                    'free_gb': round(free / (1024 ** 3), 2),
                    'percent_used': round(percent_used, 2),
                    'root_dirs': root_dirs
                })

    return drives

GetDiskFreeSpaceExW = kernel32.GetDiskFreeSpaceExW

def GetDriveSpace(drive_letter):
    free_bytes = ctypes.c_ulonglong(0)
    total_bytes = ctypes.c_ulonglong(0)
    total_free_bytes = ctypes.c_ulonglong(0)

    success = kernel32.GetDiskFreeSpaceExW(
        ctypes.c_wchar_p(drive_letter),
        ctypes.byref(free_bytes),
        ctypes.byref(total_bytes),
        ctypes.byref(total_free_bytes)
    )   

    if success:
        return total_bytes.value, free_bytes.value
    else:
        raise ctypes.WinError()

FindFirstFileW = kernel32.FindFirstFileW
FindFirstFileW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(WIN32_FIND_DATAW)]  # Corrigido aqui
FindFirstFileW.restype = ctypes.wintypes.HANDLE

FindNextFileW = kernel32.FindNextFileW
FindNextFileW.argtypes = [ctypes.wintypes.HANDLE, ctypes.POINTER(WIN32_FIND_DATAW)]
FindNextFileW.restype = ctypes.wintypes.BOOL

FindClose = kernel32.FindClose
FindClose.argtypes = [ctypes.wintypes.HANDLE]
FindClose.restype = ctypes.wintypes.BOOL

def GetRootDirs(drive_letter):
    find_data = WIN32_FIND_DATAW()
    search_path = f"{drive_letter}*"

    handle = FindFirstFileW(search_path, ctypes.byref(find_data))
    root_dirs = []

    INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value

    if handle == INVALID_HANDLE_VALUE:
        return ["Permissão negada ou partição não encontrada"]

    try:
        while True:
            dir_name = find_data.cFileName
            if dir_name not in ('.', '..'):
                root_dirs.append(dir_name)
            if not FindNextFileW(handle, ctypes.byref(find_data)):
                break
    finally:
        FindClose(handle)

    return root_dirs

if __name__ == "__main__":
    partitions = GetDiskInfos()
    for part in partitions:
        print(f"Disco: {part['path']}")
        print(f"  Total: {part['total_gb']} GB")
        print(f"  Usado: {part['used_gb']} GB")
        print(f"  Livre: {part['free_gb']} GB")
        print(f"  Uso: {part['percent_used']}%")
        print("  Diretórios na raiz:")
        for dir_name in part['root_dirs']:
            print(f"    {dir_name}")
        print()
