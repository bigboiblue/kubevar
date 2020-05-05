def err(error_msg: str) -> None:
    print(f"\033[1;31mERROR:\033[m {error_msg}")
    exit(1)

def warn(msg: str) -> None:
    print(f"\033[1;33mWARNING:\033[m {msg}")
