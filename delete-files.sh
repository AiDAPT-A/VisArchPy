#!/bin/bash

backup="/backup"
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
            else
                echo "File $filename does not exist in $original"
            fi
        fi
    done
done

