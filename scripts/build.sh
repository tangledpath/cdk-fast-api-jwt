#!/bin/bash
# Run docs  in browser:
# PDOC_ALLOW_EXEC=1 poetry run pdoc cdk_fast_api_jwt app.py  --logo https://raw.githubusercontent.com/tangledpath/fast-api-jwt/master/fast_api_jwt.png --favicon https://raw.githubusercontent.com/tangledpath/fast-api-jwt/master/fast_api_jwt_sm.png

PDOC_ALLOW_EXEC=1 poetry run pdoc cdk_fast_api_jwt app.py  -o ./docs --logo https://raw.githubusercontent.com/tangledpath/fast-api-jwt/master/fast_api_jwt.png --favicon https://raw.githubusercontent.com/tangledpath/fast-api-jwt/master/fast_api_jwt_sm.png
poetry build

echo "Exporting requirements.txt"
poetry export --without-hashes --format=requirements.txt > requirements.txt
