#!/bin/bash
#
# the script pulls docker images from docker hub
# it compresses the images and saves them to output directory
#
# written: 03/08/2019


read -p 'insert path to file containing images to save and compress: ' input_file
read -p 'insert path to output dir: ' output_dir

while read LINE
    do
	docker_image=$LINE

	# parse image to name and tag (if tag is not specified, use latest)
	docker_image_name=$(cut -d ':' -f 1 <<< $docker_image)
	docker_image_tag=$(cut -d ':' -f 2 <<< $docker_image)
	
	echo $docker_image_tag

	if [ "$docker_image_name" == "$docker_image_tag" ]; then
		docker_image_tag='latest'
	fi
	
	echo $docker_image_tag
	
	# pull image
	docker pull $docker_image
	
	# remove "/" from image name, for example from prom/node-exporter, return node-exporter
	docker_image_clean_name=$(cut -d '/' -f 2 <<< $docker_image_name)

	compressed_image_name_tag=$docker_image_clean_name"_"$docker_image_tag

	echo $output_dir"/"$compressed_image_name_tag.tar.gz

	docker save $docker_image > $output_dir"/"$compressed_image_name_tag.tar.gz
	p7zip $output_dir"/"$compressed_image_name_tag.tar.gz
done < $input_file
