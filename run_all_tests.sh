#!/bin/bash

RED="\e[31m"
GREEN="\e[32m"
ENDCOLOR="\e[0m"

# Gets the input files directory
input_files="${PWD}"/data/input;

# Creates a directory to hold the output files
mkdir -p "${PWD}"/output_files;

# Gets the output files directory
output_dir="${PWD}"/output_files;

# Gets the directory which holds the given correct output files
correct_outputs="${PWD}"/data/output;

# Iterates over all the files in the input directory and creates an output file for each
# Also keeps a count of the number of solutions that match the given outputs exactly
# Keep in mind that it is possible for an LP to have a correct output
total_count=0
correct=0
for lp in "${input_files}"/*; do
  total_count=$((total_count + 1));
  echo "Running ${lp}";
#  python3 main.py < "$lp" | tee -a "${output_dir}"/"$(basename "${lp}")" 1> /dev/null;
  python3 solver.py < "$lp" > "${output_dir}"/"$(basename "${lp}")";
  echo "Completed ${lp}";
  echo "Output saved in ${output_dir}"/"$(basename "${lp}")";\
  DIFF=$(diff <(sed -e :a -e '/^\n*$/{$d;N;};/\n$/ba' "${output_dir}"/"$(basename "${lp}")") <(sed -e :a -e '/^\n*$/{$d;N;};/\n$/ba' "${correct_outputs}"/"$(basename "${lp}")"));
#  echo ""
#  hexdump -C "${output_dir}"/"$(basename "${lp}")";
#  echo ""
#  hexdump -C "${correct_outputs}"/"$(basename "${lp}")";
#  echo ""
  if [ "$DIFF" != "" ]; then
    echo -e "${RED}Output does not match correct output for "$(basename "${lp}")"${ENDCOLOR}";
  else
    correct=$((correct + 1));
    echo -e "${GREEN}Output matches correct output for "$(basename "${lp}")"${ENDCOLOR}";
  fi;
  echo "";
  echo "";
done

echo "Total LPs solved: $total_count";
echo "Correct LPs solved: $correct";
echo "Percentage correct: $((correct * 100 / total_count))%";