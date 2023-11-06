#!/bin/bash

backup="/backup" # directory where the backup is stored
original="/original"

for dir in $( find $backup -type d )
do
    for file in "$dir"/*
    do
        if [ -f "$file" ]
        then
            filename=$(basename "$file")
            if [ -e "$original/$filename" ]
            then    
                rm "$original/$filename" 
            fi
        fi
    done
done

