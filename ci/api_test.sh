#!/bin/bash
mkdir public
python ./api_backend/test.py
OUTPUT=$(cat public/api_test.txt)
echo "$OUTPUT"
SUB='OK'
if [[ "$OUTPUT" == *"$SUB"* ]]
then
    anybadge --label=api --value=passing --file=./public/api_test.svg passing=green failing=red
else
    anybadge --label=api --value=failing --file=./public/api_test.svg passing=green failing=red
fi