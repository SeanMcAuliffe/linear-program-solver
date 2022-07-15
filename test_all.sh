#!/bin/bash

input_files="${PWD}"/data/input;

mkdir -p "${PWD}"/output_files;

output_dir="${PWD}"/output_files;
correct_outputs="${PWD}"/data/output;

for lp in "${input_files}"/*; do
  echo "Running ${lp}";
  python3 solver.py < "$lp" | tee "${output_dir}"/"$(basename "${lp}")" 1> /dev/null;
  echo "Completed ${lp}";
  echo "Output saved in ${output_dir}"/"$(basename "${lp}")";
  echo "";
  echo "";
done

total_count=0
correct=0
for lp in "${output_dir}"/*; do
  total_count=$((total_count + 1));
  DIFF=$(diff "$lp" "${correct_outputs}"/"$(basename "${lp}")")
  if [ "$DIFF" == "" ]; then
    correct=$((correct + 1));
  fi
done

echo "Total LPs solved: $total_count";
echo "Correct LPs solved: $correct";
echo "Percentage correct: $((correct * 100 / total_count))%";