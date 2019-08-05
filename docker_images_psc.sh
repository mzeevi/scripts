#!/bin/bash
#
# the script pulls docker images from docker hub
# it compresses the images and saves them to output directory
#
# written: 03/08/2019

read -p 'insert full path to file containing images to save and compress: ' INPUT_FILE
read -p 'insert full path to output dir: ' OUTPUT_DIR

# check if output dir path has / at the end, if no - add it
if [ ! ${OUTPUT_DIR: -1} == '/' ]; then
	OUTPUT_DIR+="/"
fi

# check if output dir exists, if not - create it
if [ ! -d "$OUTPUT_DIR" ]; then
	mkdir $OUTPUT_DIR
fi

while read LINE
    do
	docker_image=$LINE

	# parse image to name and tag (if tag is not specified, use latest)
	docker_image_name=$(cut -d ':' -f 1 <<< $docker_image)
	docker_image_tag=$(cut -d ':' -f 2 <<< $docker_image)

	if [ "$docker_image_name" == "$docker_image_tag" ]; then
		docker_image_tag='latest'
	fi
		
	# pull image
	docker pull $docker_image
	
	# remove "/" from image name, for example from prom/node-exporter, return node-exporter
	docker_image_clean_name=$(cut -d '/' -f 2 <<< $docker_image_name)

	# save and compress image
	compressed_image_name_tag=$docker_image_clean_name"_"$docker_image_tag
	output_file_path="${OUTPUT_DIR}${compressed_image_name_tag}.tar.gz"

	docker save $docker_image > $output_file_path
	p7zip $output_file_path
done < $INPUT_FILE
