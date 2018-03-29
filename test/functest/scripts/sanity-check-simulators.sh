#!/bin/bash

for x in policy has-api so-callback; do
   curl http://localhost:5000/simulated/healthy/$x
   curl http://localhost:5000/simulated/unhealthy/$x
   curl http://localhost:5000/simulated/ERROR/$x
   curl http://localhost:5000/simulated/success/$x
done

curl -d '{"A1": "B1"}' http://localhost:5000/simulated/policy/pdp-has-vcpe-good/getConfig
curl -d '{"A1": "B1"}' http://localhost:5000/simulated/oof/has-api/flow1-success-simple/main.json
