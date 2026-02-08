# Build a bash array of files
# Build a bash array of files
FILES=("./Data"/*.pb)
(IFS=,; echo "${FILES[*]}") > index_to_filename.csv
