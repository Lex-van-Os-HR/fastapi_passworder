#!/bin/zsh

git clone https://github.com/Lex-van-Os-HR/fastapi_passworder.git

cd "./fastapi_passworder"

pip3 install -r requirements.txt
python3 -m unittest discover .

if [ $? -eq 0 ];
then
    echo "Script ran succesfully!"
else
    echo "Failed to run test: $?"
    echo 1;
fi

git describe --tags > "./git_lex_tags.txt"

cd ".."
mkdir "passworder_test"
mv "./fastapi_passworder" "passworder_test"
cd "./passworder_test/fastapi_passworder/passworder"

python3 main.py

