import subprocess
import socket
import sys

def check_port_conflicts(ports=[8001, 5180]):
    conflicts = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Set a very short timeout
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', port)) == 0:
                conflicts.append(port)
                
    if not conflicts:
        return
        
    print("\n" + "="*60)
    print(" CRITICAL ERROR: PORT CONFLICT DETECTED")
    print("="*60)
    print("The following port(s) required by BITATLAS are occupied:\n")
    
    for port in conflicts:
        print(f"  * Port {port} is currently IN USE.")
        
        # 1. Try to find PID using netstat
        pid = None
        try:
            output = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True, text=True)
            for line in output.strip().split('\n'):
                if 'LISTENING' in line or f':{port}' in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        break
        except Exception:
            pass
            
        if pid:
            print(f"    - Process ID (PID): {pid}")
            # 2. Try to get process name using tasklist
            try:
                task_out = subprocess.check_output(f'tasklist /FI "PID eq {pid}" /FO CSV /NH', shell=True, text=True)
                parts = [p.strip('"') for p in task_out.strip().split(',')]
                if parts and parts[0]:
                    print(f"    - Executable Name: {parts[0]}")
            except Exception:
                pass
        else:
            print("    - Could not determine PID (check permissions).")
            
        # 3. Check if docker container is mapping this port
        try:
            docker_out = subprocess.check_output('docker ps --format "{{.ID}}\t{{.Names}}\t{{.Ports}}"', shell=True, text=True)
            docker_found = False
            for line in docker_out.strip().split('\n'):
                if f":{port}" in line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        print(f"    - Docker Container: {parts[1]} (ID: {parts[0]})")
                        docker_found = True
            if not docker_found:
                docker_all = subprocess.check_output('docker ps -a --format "{{.ID}}\t{{.Names}}\t{{.Ports}}"', shell=True, text=True)
                for line in docker_all.strip().split('\n'):
                    if f":{port}" in line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            print(f"    - Docker Container (Stopped): {parts[1]} (ID: {parts[0]})")
        except Exception:
            pass
            
    print("\nPlease stop the conflicting process or container before restarting.")
    print("="*60 + "\n")
    sys.exit(1)
