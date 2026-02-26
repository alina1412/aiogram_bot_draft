#!/bin/sh
echo "Running first script..."

# Create Rabbitmq user
( rabbitmqctl wait --timeout 60 $RABBITMQ_PID_FILE ; \
rabbitmqctl add_user $RABBITMQ_DEFAULT_USER $RABBITMQ_DEFAULT_PASS 2>/dev/null ; \
rabbitmqctl set_user_tags $RABBITMQ_DEFAULT_USER administrator ; \
rabbitmqctl set_permissions -p / $RABBITMQ_DEFAULT_USER  ".*" ".*" ".*" ; \
echo "*** User '$RABBITMQ_DEFAULT_USER' with password '$RABBITMQ_DEFAULT_PASS' completed. ***" ; \
echo "*** Log in the WebUI at port 15672 (example: http:/localhost:15672) ***") &

# $@ is used to pass arguments to the rabbitmq-server command.
# For example if you use it like this: docker run -d rabbitmq arg1 arg2,
# it will be as you run in the container rabbitmq-server arg1 arg2
# rabbitmq-server $@

# Start RabbitMQ in background
rabbitmq-server $@ &

# Wait for RabbitMQ to be fully up
echo "Waiting for RabbitMQ to start..."
while ! rabbitmqctl status > /dev/null 2>&1; do
    sleep 2
done


sleep 2
echo "Running second script..."

# declare queue
curl -i -u $RABBITMQ_DEFAULT_USER:$RABBITMQ_DEFAULT_PASS -H "content-type:application/json" \
-XPUT -d'{"durable":true}' \
http://127.0.0.1:15672/api/queues/%2f/$QUEUE_NAME

# Keep container alive
wait