#!/bin/bash

#!/bin/bash

# Usage
# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/test/microk8.cert.gen.bash
# chmod +x ./microk8.cert.gen.bash
# ./microk8.cert.gen.bash

# Initialize variables to store previous values
previous_ip=""
previous_csr=""

# Function to print a banner
print_banner() {
    local message="$1"
    echo "=================================================="
    echo "$message"
    echo "=================================================="
}

# Function to log with timestamp
log_message() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message"
}

echo "Starting monitoring script..."
echo "Monitoring IP changes and CSR configuration changes..."
echo ""

# Main monitoring loop
while true; do
    # Get current IP address
    current_ip=$(hostname -I | tr -d '\n')
    
    # Check if this is the first run or if IP changed
    if [ -z "$previous_ip" ]; then
        log_message "Initial IP detected: $current_ip"
        previous_ip="$current_ip"
    elif [ "$current_ip" != "$previous_ip" ]; then
        print_banner "IP CHANGE DETECTED!"
        log_message "Old IP: $previous_ip"
        log_message "New IP: $current_ip"
        previous_ip="$current_ip"
    else
        log_message "IP: no change"
    fi
    
    # Get current CSR configuration content
    csr_file="/var/snap/microk8s/current/certs/csr.conf.rendered"
    if [ -f "$csr_file" ]; then
        current_csr=$(cat "$csr_file" 2>/dev/null)
        
        # Check if this is the first run or if CSR changed
        if [ -z "$previous_csr" ]; then
            log_message "Initial CSR configuration loaded"
            previous_csr="$current_csr"
        elif [ "$current_csr" != "$previous_csr" ]; then
            print_banner "CSR CHANGE DETECTED!"
            log_message "Old CSR content:"
            echo "$previous_csr"
            echo ""
            log_message "New CSR content:"
            echo "$current_csr"
            previous_csr="$current_csr"
        else
            log_message "CSR: no change"
        fi
    else
        log_message "CSR file not found: $csr_file"
    fi
    
    # Sleep for 3 seconds
    sleep 3
done