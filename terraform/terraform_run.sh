#!/bin/bash

# Navigate to the provided directory
cd $1
ls -ltr

# Iterate through the variables and export each as TF_VAR_
if [ ! -z "$2" ]; then
  for var in $(echo "$2" | tr ',' '\n'); do
    key=$(echo $var | cut -d '=' -f 1)   # Extract the variable name
    value=$(echo $var | cut -d '=' -f 2) # Extract the variable value
    echo "Exporting TF_VAR_$key=$value"
    export TF_VAR_$key="$value"          # Export as TF_VAR_ format
  done
fi

# Run the appropriate Terraform command (plan or apply)
if [ "$3" = "apply" ]; then
  terraform apply -auto-approve
else
  terraform plan
fi