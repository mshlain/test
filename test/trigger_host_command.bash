#!/bin/bash

# Usage
# curl -O https://raw.githubusercontent.com/mshlain/test/refs/heads/main/test/trigger_host_command.bash
# chmod +x ./microk8.cert.gen.bash
# ./microk8.cert.gen.bash | tee -a ./microk8.cert.gen.bash.log

set -x

TASK_ID=$(curl \
  --unix-socket /opt/zerto/host_commands/sockets/socket \
  -X POST "http://localhost/TasksService/StartTask" \
  -H "Content-Type: application/json" \
  -d '{ "CommandName":"GetBootloaderFipsConfiguration", "TimeoutSecs":"9" }' | jq -r '.Id')

echo "Task ID: $TASK_ID"

sleep 3

curl \
  --unix-socket /opt/zerto/host_commands/sockets/socket \
  -X POST "http://localhost/TasksService/GetTaskInfo" \
  -H "Content-Type: application/json" \
  -d "{\"Id\":\"$TASK_ID\"}" | jq
