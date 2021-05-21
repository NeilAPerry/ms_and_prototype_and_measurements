#!/bin/bash

for file in *.csv
do
  mv "$file" "${file/uniform_True_uniformSpacing/uniform_True_broadcastType_smart_uniformSpacing}"
done
