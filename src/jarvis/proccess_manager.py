import psutil


def get_processes():
    """Возвращает список запущенных процессов."""
    processes = []

    for process in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = process.info

            processes.append({
                "pid": info["pid"],
                "name": info["name"],
                "cpu": info["cpu_percent"],
                "memory": info["memory_percent"],
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return processes


def get_cpu_processes(limit=5):
    """Возвращает процессы с самым высоким использованием CPU."""
    processes = []

    for process in psutil.process_iter():
        try:
            process.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    import time
    time.sleep(0.5)

    for process in psutil.process_iter(["pid", "name"]):
        try:
            cpu = process.cpu_percent(None)

            processes.append({
                "pid": process.pid,
                "name": process.info["name"],
                "cpu": cpu,
            })

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    processes.sort(key=lambda x: x["cpu"], reverse=True)

    return processes[:limit]


def find_process(process_name):
    """Ищет процессы по имени."""
    result = []

    process_name = process_name.lower()

    for process in psutil.process_iter(["pid", "name"]):
        try:
            name = process.info["name"]

            if name and process_name in name.lower():
                result.append(process)

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return result


def kill_process(process_name):
    """Завершает процесс по имени."""
    processes = find_process(process_name)

    if not processes:
        return False, f"Процесс {process_name} не найден"

    killed = 0

    for process in processes:
        try:
            process.terminate()
            killed += 1

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return True, f"Завершено процессов: {killed}"
