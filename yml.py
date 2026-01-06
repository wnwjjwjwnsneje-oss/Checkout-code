name: "ULTRA POWER TEST"
on:
  workflow_dispatch:
    inputs:
      ip:
        description: "Target IP"
        required: true
      port:
        description: "Target Port"
      duration:
        description: "Duration"
      packet_size:
        description: "Size"
      threads:
        description: "Threads"

jobs:
  network-test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        # Increased to 100 parallel workers for maximum output
        worker: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
    steps:
    - name: Checkout
      uses: actions/checkout@v4
    - name: System Optimization
      run: |
        # Expand network socket limits for high-concurrency tasks
        sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"
        sudo sysctl -w net.ipv4.tcp_fin_timeout=15
        chmod +x mustafa
    - name: Run Test
      run: python3 main.py ${{ inputs.ip }} ${{ inputs.port }} ${{ inputs.duration }} ${{ inputs.packet_size }} ${{ inputs.threads }}
      