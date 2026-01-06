import subprocess
import sys
import os

def main():
    if len(sys.argv) != 6:
        print("Usage: python3 main.py <ip> <port> <time> <packet_size> <threads>")
        sys.exit(1)
    
    # Extract arguments
    ip, port, duration, size, threads = sys.argv[1:6]
    
    # Ensure the binary is executable
    if os.path.exists("mustafa"):
        os.chmod("mustafa", 0o755)
    
    print(f"Starting optimized task on {ip}:{port}")
    
    # Direct execution of the binary with provided parameters
    try:
        subprocess.run(["./mustafa", ip, port, duration, size, threads], check=True)
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    main()
    