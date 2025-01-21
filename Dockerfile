# docker start -ai pedantic_wescoff
# docker run -it async /bin/bash

# Use Python 3.12 slim image as the base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Update and upgrade the system
RUN apt-get update && apt-get upgrade -y && \
	apt-get install curl wget git build-essential tmux nodejs npm -y && \
	apt-get autoremove -y && apt-get clean && \
	rm -rf /var/lib/apt/lists/* && \
	curl -LO https://github.com/neovim/neovim/releases/latest/download/nvim-linux64.tar.gz && \
	rm -rf /opt/nvim && \
	tar -C /opt -xzf nvim-linux64.tar.gz && \
	echo "export PATH=\"$PATH:/opt/nvim-linux64/bin\"" >> ~/.bashrc && \
	echo "set -o vi" >> ~/.bashrc && \
	echo "setw -g mode-keys vi" >> ~/.tmux.conf && \
	mkdir /root/.config && mkdir /root/.config/nvim && git clone https://github.com/acesanderson/nvim_settings /root/.config/nvim && \
	touch /app/hello.txt && \ 
	pip install black && \
	# Add these pip install commands before the final "pip install ."
	pip install git+https://github.com/acesanderson/Chain.git && \
	pip install git+https://github.com/acesanderson/Curator.git && \
	pip install .


# Make port 80 available to the world outside this container
EXPOSE 80

# Set the default command
CMD ["tmux"]

