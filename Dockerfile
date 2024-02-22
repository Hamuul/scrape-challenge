# Use python3.12-slim-bookworm as the base image
FROM python:3.12-slim-bookworm

# Install system dependencies
ARG GITHUB_PAT

RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list

RUN apt update -y
RUN apt install libxml2-dev libxslt-dev git firefox-l10n-de wget -y


RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
RUN tar -xzf geckodriver-v0.34.0-linux64.tar.gz
RUN mv geckodriver /usr/local/bin/geckodriver
RUN chmod +x /usr/local/bin/geckodriver

RUN git clone https://${GITHUB_PAT}@github.com/Hamuul/scrape-challenge

WORKDIR /scrape-challenge
# Install required python libraries
RUN pip install asyncio uvloop pypeln ujson aiofiles aiocsv fake_useragent pytest-playwright lxml cssselect selenium xmltodict

# Install Playwright browsers
RUN playwright install chromium && playwright install-deps
RUN mv products.txt products.txt.bak && mv pw/full.csv pw/full.csv.bak
# Clone the scrape-challenge repository
RUN python3 get_xmls.py && cp *.xml pw/

# Run the main script or entrypoint of your application
CMD [ "/bin/bash"]