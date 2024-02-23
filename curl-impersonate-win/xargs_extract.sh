#!/bin/bash

xargs -P 16 -I {} sh -c 'cmd.exe /c curl_chrome116.bat {} | rg productData | jq -r ".productData.productName, (.productData.brandKey // .productData.slug), .productData.pricing.price, .productData.gtin"' < products_links.txt > products.txt


