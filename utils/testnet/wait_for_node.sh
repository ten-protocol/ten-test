# Wait for an explicit regex in the enclave to indicate the node is ready to
# start L2 contract deployment
#
container_id=`docker ps -aqf "name=testnet-enclave-1"`
  
start=`date +%s`
while true; 
do
  docker logs $container_id | grep "Obscuro enclave service started" > /dev/null 2>&1
  if [[ $? == 0 ]]; then
    echo Regex seen in container output ... exiting;
    break
  fi

  current=`date +%s`
  wait_time=`expr $current - $start`

  if (( $wait_time > 90 )); then
    echo Exceed maximum wait time ... exiting;
    break
  fi

  echo Regex not seen in container output ... wait time is $wait_time
  sleep 1
done


